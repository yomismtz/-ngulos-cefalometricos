package com.cefalo.angulos;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Matrix;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.PointF;
import android.graphics.Rect;
import android.graphics.RectF;
import android.util.AttributeSet;
import android.view.MotionEvent;
import android.view.ScaleGestureDetector;
import android.view.View;

import java.util.ArrayList;
import java.util.List;

public class MeasurementView extends View {

    public interface ProgressListener {
        void onProgress(int placed, int total, String currentLabel);
    }

    public interface CalibrationListener {
        void onCalibrationReady(PointF first, PointF second, double pixelDistance);
    }

    private Bitmap bitmap;
    private final List<String> landmarkLabels = new ArrayList<>();
    private final List<PointF> points = new ArrayList<>();

    private final Paint imagePaint = new Paint(Paint.ANTI_ALIAS_FLAG | Paint.FILTER_BITMAP_FLAG);
    private final Paint pointPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint selectedPointPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint selectedRingPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint haloPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint textPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint magnifierBorderPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint calibrationPaint = new Paint(Paint.ANTI_ALIAS_FLAG);

    private final Matrix matrix = new Matrix();
    private final Matrix inverse = new Matrix();
    private float zoom = 1f;

    private final ScaleGestureDetector scaleDetector;
    private float lastTwoFingerX, lastTwoFingerY;
    private boolean twoFingerTracking = false;

    private int selectedIndex = 0;
    private int draggingPoint = -1;
    private float downX, downY;
    private boolean moved = false;
    private boolean locked = false;

    private boolean magnifierActive = false;
    private PointF magnifierImagePoint;

    private ProgressListener progressListener;
    private CalibrationListener calibrationListener;
    private boolean calibrationMode = false;
    private PointF calibrationPoint1;
    private PointF calibrationPoint2;

    public MeasurementView(Context context, AttributeSet attrs) {
        super(context, attrs);
        setLayerType(View.LAYER_TYPE_SOFTWARE, null);

        pointPaint.setColor(Color.rgb(34, 191, 199));
        pointPaint.setStyle(Paint.Style.FILL);

        selectedPointPaint.setColor(Color.rgb(34, 191, 199));
        selectedPointPaint.setStyle(Paint.Style.FILL);

        selectedRingPaint.setColor(Color.rgb(142, 103, 214));
        selectedRingPaint.setStyle(Paint.Style.STROKE);
        selectedRingPaint.setStrokeWidth(dp(3));

        haloPaint.setColor(Color.WHITE);
        haloPaint.setStyle(Paint.Style.FILL);

        textPaint.setColor(Color.rgb(225, 255, 248));
        textPaint.setTextSize(25f);
        textPaint.setFakeBoldText(true);
        textPaint.setShadowLayer(5f, 1f, 1f, Color.BLACK);

        magnifierBorderPaint.setColor(Color.rgb(185, 243, 230));
        magnifierBorderPaint.setStyle(Paint.Style.STROKE);
        magnifierBorderPaint.setStrokeWidth(dp(4));

        calibrationPaint.setColor(Color.rgb(255, 190, 66));
        calibrationPaint.setStyle(Paint.Style.STROKE);
        calibrationPaint.setStrokeWidth(dp(3));

        scaleDetector = new ScaleGestureDetector(context,
                new ScaleGestureDetector.SimpleOnScaleGestureListener() {
                    @Override
                    public boolean onScale(ScaleGestureDetector detector) {
                        if (bitmap == null) return false;

                        float factor = detector.getScaleFactor();
                        float newZoom = Math.max(1f, Math.min(8f, zoom * factor));
                        factor = newZoom / zoom;
                        zoom = newZoom;

                        matrix.postScale(
                                factor,
                                factor,
                                detector.getFocusX(),
                                detector.getFocusY()
                        );

                        updateInverse();
                        invalidate();
                        return true;
                    }
                });
    }

    public void setProgressListener(ProgressListener listener) {
        progressListener = listener;
        notifyProgress();
    }

    public void startCalibration(CalibrationListener listener) {
        if (bitmap == null) return;
        calibrationListener = listener;
        calibrationMode = true;
        calibrationPoint1 = null;
        calibrationPoint2 = null;
        magnifierActive = false;
        invalidate();
    }

    public void cancelCalibration() {
        calibrationMode = false;
        calibrationListener = null;
        magnifierActive = false;
        invalidate();
    }

    public boolean isCalibrationMode() {
        return calibrationMode;
    }

    public void setLandmarks(List<String> labels) {
        landmarkLabels.clear();
        landmarkLabels.addAll(labels);

        points.clear();
        for (int i = 0; i < landmarkLabels.size(); i++) {
            points.add(null);
        }

        selectedIndex = landmarkLabels.isEmpty() ? -1 : 0;
        notifyProgress();
        invalidate();
    }

    public void setPoints(List<PointF> savedPoints) {
        for (int i = 0; i < points.size(); i++) {
            PointF source = savedPoints != null && i < savedPoints.size()
                    ? savedPoints.get(i)
                    : null;

            points.set(i, source == null ? null : new PointF(source.x, source.y));
        }

        int missing = firstMissingIndex();
        if (missing >= 0) {
            selectedIndex = missing;
        } else if (!points.isEmpty()) {
            selectedIndex = Math.max(0, Math.min(selectedIndex, points.size() - 1));
        }

        notifyProgress();
        invalidate();
    }

    public List<PointF> getPointsSnapshot() {
        List<PointF> copy = new ArrayList<>();
        for (PointF p : points) {
            copy.add(p == null ? null : new PointF(p.x, p.y));
        }
        return copy;
    }

    public List<String> getLandmarkLabels() {
        return new ArrayList<>(landmarkLabels);
    }

    public void setBitmap(Bitmap b) {
        bitmap = b;
        fitImage();
        invalidate();
    }

    public boolean hasBitmap() {
        return bitmap != null;
    }

    public boolean isComplete() {
        return !points.isEmpty() && getPlacedCount() == points.size();
    }

    public int getPlacedCount() {
        int count = 0;
        for (PointF p : points) {
            if (p != null) count++;
        }
        return count;
    }

    public int getTotalCount() {
        return landmarkLabels.size();
    }

    public int getSelectedIndex() {
        return selectedIndex;
    }

    public String getCurrentLabel() {
        if (selectedIndex < 0 || selectedIndex >= landmarkLabels.size()) return null;
        return landmarkLabels.get(selectedIndex);
    }

    public String getNextLabel() {
        return getCurrentLabel();
    }

    public boolean hasPointAt(int index) {
        return index >= 0 && index < points.size() && points.get(index) != null;
    }

    public PointF getPoint(String label) {
        int index = landmarkLabels.indexOf(label);
        if (index < 0 || index >= points.size()) return null;

        PointF p = points.get(index);
        return p == null ? null : new PointF(p.x, p.y);
    }

    public void setSelectedIndex(int index, boolean centerIfPlaced) {
        if (landmarkLabels.isEmpty()) return;

        selectedIndex = Math.max(0, Math.min(index, landmarkLabels.size() - 1));

        if (centerIfPlaced && hasPointAt(selectedIndex)) {
            centerOnPoint(points.get(selectedIndex));
        }

        notifyProgress();
        invalidate();
    }

    public void selectPrevious() {
        if (landmarkLabels.isEmpty()) return;
        int next = selectedIndex <= 0 ? landmarkLabels.size() - 1 : selectedIndex - 1;
        setSelectedIndex(next, true);
    }

    public void selectNext() {
        if (landmarkLabels.isEmpty()) return;
        int next = selectedIndex >= landmarkLabels.size() - 1 ? 0 : selectedIndex + 1;
        setSelectedIndex(next, true);
    }

    public void setLocked(boolean value) {
        locked = value;
        magnifierActive = false;
        invalidate();
    }

    public boolean isLocked() {
        return locked;
    }

    public void undo() {
        if (locked || points.isEmpty()) return;

        int start = selectedIndex - 1;
        if (start < 0) start = points.size() - 1;

        int found = -1;
        for (int step = 0; step < points.size(); step++) {
            int i = (start - step + points.size()) % points.size();
            if (points.get(i) != null) {
                found = i;
                break;
            }
        }

        if (found >= 0) {
            points.set(found, null);
            selectedIndex = found;
        }

        notifyProgress();
        invalidate();
    }

    public void resetMeasurement() {
        if (locked) return;

        for (int i = 0; i < points.size(); i++) {
            points.set(i, null);
        }

        selectedIndex = landmarkLabels.isEmpty() ? -1 : 0;
        notifyProgress();
        invalidate();
    }

    public void fitImage() {
        if (bitmap == null || getWidth() == 0 || getHeight() == 0) return;

        float sx = (float) getWidth() / bitmap.getWidth();
        float sy = (float) getHeight() / bitmap.getHeight();
        float scale = Math.min(sx, sy);

        float w = bitmap.getWidth() * scale;
        float h = bitmap.getHeight() * scale;
        float dx = (getWidth() - w) / 2f;
        float dy = (getHeight() - h) / 2f;

        matrix.reset();
        matrix.setScale(scale, scale);
        matrix.postTranslate(dx, dy);

        zoom = 1f;
        updateInverse();
        invalidate();
    }

    private void centerOnPoint(PointF point) {
        if (point == null || bitmap == null) return;

        PointF screen = imageToScreen(point);
        float dx = getWidth() / 2f - screen.x;
        float dy = getHeight() / 2f - screen.y;

        matrix.postTranslate(dx, dy);
        updateInverse();
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);
        if (bitmap != null) fitImage();
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        canvas.drawColor(Color.rgb(18, 22, 28));

        if (bitmap == null) {
            textPaint.setTextSize(34f);
            canvas.drawText("Abra una radiografía", 40, 80, textPaint);
            return;
        }

        canvas.drawBitmap(bitmap, matrix, imagePaint);
        drawPoints(canvas);
        drawCalibration(canvas);

        if (magnifierActive && magnifierImagePoint != null) {
            drawMagnifier(canvas);
        }
    }

    private void drawPoints(Canvas canvas) {
        for (int i = 0; i < points.size(); i++) {
            PointF point = points.get(i);
            if (point == null) continue;

            PointF s = imageToScreen(point);

            canvas.drawCircle(s.x, s.y, dp(12), haloPaint);
            canvas.drawCircle(
                    s.x,
                    s.y,
                    dp(i == selectedIndex ? 9 : 8),
                    i == selectedIndex ? selectedPointPaint : pointPaint
            );

            if (i == selectedIndex) {
                canvas.drawCircle(s.x, s.y, dp(15), selectedRingPaint);
                canvas.drawLine(s.x - dp(20), s.y, s.x - dp(11), s.y, selectedRingPaint);
                canvas.drawLine(s.x + dp(11), s.y, s.x + dp(20), s.y, selectedRingPaint);
                canvas.drawLine(s.x, s.y - dp(20), s.x, s.y - dp(11), selectedRingPaint);
                canvas.drawLine(s.x, s.y + dp(11), s.x, s.y + dp(20), selectedRingPaint);
            }

            String label = i < landmarkLabels.size()
                    ? landmarkLabels.get(i)
                    : String.valueOf(i + 1);

            textPaint.setTextSize(dp(14));
            canvas.drawText(label, s.x + dp(12), s.y - dp(10), textPaint);
        }
    }

    private void drawCalibration(Canvas canvas) {
        if (calibrationPoint1 == null) return;

        PointF a = imageToScreen(calibrationPoint1);

        if (calibrationPoint2 != null) {
            PointF b = imageToScreen(calibrationPoint2);
            canvas.drawLine(a.x, a.y, b.x, b.y, calibrationPaint);
            canvas.drawCircle(b.x, b.y, dp(7), calibrationPaint);
        }

        canvas.drawCircle(a.x, a.y, dp(7), calibrationPaint);

        textPaint.setTextSize(dp(13));
        canvas.drawText(
                calibrationMode ? "CALIBRAR" : "CAL",
                a.x + dp(10),
                a.y - dp(10),
                textPaint
        );
    }

    private void drawMagnifier(Canvas canvas) {
        if (bitmap == null || magnifierImagePoint == null) return;

        float radius = dp(64);
        float cx = getWidth() - radius - dp(16);
        float cy = radius + dp(16);

        float[] values = new float[9];
        matrix.getValues(values);
        float currentScale = (float) Math.sqrt(
                values[Matrix.MSCALE_X] * values[Matrix.MSCALE_X] +
                values[Matrix.MSKEW_Y] * values[Matrix.MSKEW_Y]
        );

        if (currentScale <= 0f) currentScale = 1f;

        float magnification = 3.2f;
        float sourceHalf = radius / (currentScale * magnification);

        int left = Math.max(0, Math.round(magnifierImagePoint.x - sourceHalf));
        int top = Math.max(0, Math.round(magnifierImagePoint.y - sourceHalf));
        int right = Math.min(bitmap.getWidth(), Math.round(magnifierImagePoint.x + sourceHalf));
        int bottom = Math.min(bitmap.getHeight(), Math.round(magnifierImagePoint.y + sourceHalf));

        if (right <= left || bottom <= top) return;

        Rect src = new Rect(left, top, right, bottom);
        RectF dst = new RectF(cx - radius, cy - radius, cx + radius, cy + radius);

        canvas.save();

        Path clip = new Path();
        clip.addCircle(cx, cy, radius, Path.Direction.CW);
        canvas.clipPath(clip);
        canvas.drawColor(Color.BLACK);
        canvas.drawBitmap(bitmap, src, dst, imagePaint);

        canvas.restore();

        canvas.drawCircle(cx, cy, radius, magnifierBorderPaint);

        Paint cross = new Paint(Paint.ANTI_ALIAS_FLAG);
        cross.setColor(Color.rgb(154, 111, 232));
        cross.setStrokeWidth(dp(2));

        canvas.drawLine(cx - dp(12), cy, cx + dp(12), cy, cross);
        canvas.drawLine(cx, cy - dp(12), cx, cy + dp(12), cross);
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        if (bitmap == null || landmarkLabels.isEmpty()) return true;

        scaleDetector.onTouchEvent(event);

        if (calibrationMode) {
            return handleCalibrationTouch(event);
        }

        if (event.getPointerCount() >= 2) {
            magnifierActive = false;
            handleTwoFingerPan(event);
            draggingPoint = -1;
            return true;
        } else {
            twoFingerTracking = false;
        }

        switch (event.getActionMasked()) {
            case MotionEvent.ACTION_DOWN:
                downX = event.getX();
                downY = event.getY();
                moved = false;

                PointF initial = screenToImage(downX, downY);
                if (insideImage(initial)) {
                    magnifierImagePoint = initial;
                    magnifierActive = true;
                }

                draggingPoint = locked
                        ? -1
                        : findNearbyPoint(downX, downY, dp(34));

                invalidate();
                return true;

            case MotionEvent.ACTION_MOVE:
                if (Math.hypot(event.getX() - downX, event.getY() - downY) > dp(6)) {
                    moved = true;
                }

                PointF movePoint = screenToImage(event.getX(), event.getY());
                if (insideImage(movePoint)) {
                    magnifierImagePoint = movePoint;
                    magnifierActive = true;
                }

                if (!locked && draggingPoint >= 0 && insideImage(movePoint)) {
                    points.set(draggingPoint, movePoint);
                    selectedIndex = draggingPoint;
                }

                invalidate();
                return true;

            case MotionEvent.ACTION_UP:
                PointF upPoint = screenToImage(event.getX(), event.getY());

                if (!locked) {
                    if (draggingPoint >= 0) {
                        draggingPoint = -1;
                        notifyProgress();
                    } else if (!moved && insideImage(upPoint)
                            && selectedIndex >= 0
                            && selectedIndex < points.size()) {

                        points.set(selectedIndex, upPoint);

                        int nextMissing = nextMissingIndex(selectedIndex);
                        if (nextMissing >= 0) {
                            selectedIndex = nextMissing;
                        }

                        notifyProgress();
                    }
                }

                magnifierActive = false;
                invalidate();
                return true;

            case MotionEvent.ACTION_CANCEL:
                draggingPoint = -1;
                magnifierActive = false;
                invalidate();
                return true;
        }

        return true;
    }

    private boolean handleCalibrationTouch(MotionEvent event) {
        if (event.getPointerCount() >= 2) {
            magnifierActive = false;
            handleTwoFingerPan(event);
            return true;
        } else {
            twoFingerTracking = false;
        }

        switch (event.getActionMasked()) {
            case MotionEvent.ACTION_DOWN:
                downX = event.getX();
                downY = event.getY();
                moved = false;

                PointF initial = screenToImage(downX, downY);
                if (insideImage(initial)) {
                    magnifierImagePoint = initial;
                    magnifierActive = true;
                }

                invalidate();
                return true;

            case MotionEvent.ACTION_MOVE:
                if (Math.hypot(event.getX() - downX, event.getY() - downY) > dp(6)) {
                    moved = true;
                }

                PointF movePoint = screenToImage(event.getX(), event.getY());
                if (insideImage(movePoint)) {
                    magnifierImagePoint = movePoint;
                    magnifierActive = true;
                }

                invalidate();
                return true;

            case MotionEvent.ACTION_UP:
                PointF upPoint = screenToImage(event.getX(), event.getY());

                if (!moved && insideImage(upPoint)) {
                    if (calibrationPoint1 == null) {
                        calibrationPoint1 = upPoint;
                    } else {
                        calibrationPoint2 = upPoint;

                        double pixels = Math.hypot(
                                calibrationPoint2.x - calibrationPoint1.x,
                                calibrationPoint2.y - calibrationPoint1.y
                        );

                        calibrationMode = false;
                        magnifierActive = false;

                        CalibrationListener listener = calibrationListener;
                        calibrationListener = null;

                        invalidate();

                        if (listener != null && pixels > 0.0) {
                            listener.onCalibrationReady(
                                    new PointF(calibrationPoint1.x, calibrationPoint1.y),
                                    new PointF(calibrationPoint2.x, calibrationPoint2.y),
                                    pixels
                            );
                        }

                        return true;
                    }
                }

                magnifierActive = false;
                invalidate();
                return true;

            case MotionEvent.ACTION_CANCEL:
                magnifierActive = false;
                invalidate();
                return true;
        }

        return true;
    }

    private void handleTwoFingerPan(MotionEvent event) {
        float cx = (event.getX(0) + event.getX(1)) / 2f;
        float cy = (event.getY(0) + event.getY(1)) / 2f;

        if (!twoFingerTracking || event.getActionMasked() == MotionEvent.ACTION_POINTER_DOWN) {
            lastTwoFingerX = cx;
            lastTwoFingerY = cy;
            twoFingerTracking = true;
            return;
        }

        if (event.getActionMasked() == MotionEvent.ACTION_MOVE
                && !scaleDetector.isInProgress()) {
            matrix.postTranslate(cx - lastTwoFingerX, cy - lastTwoFingerY);
            updateInverse();
            invalidate();
        }

        lastTwoFingerX = cx;
        lastTwoFingerY = cy;
    }

    private int findNearbyPoint(float sx, float sy, float radiusPx) {
        for (int i = 0; i < points.size(); i++) {
            PointF point = points.get(i);
            if (point == null) continue;

            PointF p = imageToScreen(point);
            if (Math.hypot(sx - p.x, sy - p.y) <= radiusPx) {
                return i;
            }
        }

        return -1;
    }

    private int firstMissingIndex() {
        for (int i = 0; i < points.size(); i++) {
            if (points.get(i) == null) return i;
        }
        return -1;
    }

    private int nextMissingIndex(int after) {
        for (int i = after + 1; i < points.size(); i++) {
            if (points.get(i) == null) return i;
        }

        for (int i = 0; i <= after && i < points.size(); i++) {
            if (points.get(i) == null) return i;
        }

        return -1;
    }

    private PointF imageToScreen(PointF p) {
        float[] v = {p.x, p.y};
        matrix.mapPoints(v);
        return new PointF(v[0], v[1]);
    }

    private PointF screenToImage(float x, float y) {
        float[] v = {x, y};
        inverse.mapPoints(v);
        return new PointF(v[0], v[1]);
    }

    private boolean insideImage(PointF p) {
        return p != null
                && p.x >= 0
                && p.y >= 0
                && p.x <= bitmap.getWidth()
                && p.y <= bitmap.getHeight();
    }

    private void updateInverse() {
        matrix.invert(inverse);
    }

    private float dp(float value) {
        return value * getResources().getDisplayMetrics().density;
    }

    public Bitmap renderAnnotatedBitmap() {
        if (bitmap == null) return null;

        int maxDimension = 2400;
        float exportScale = Math.min(
                1f,
                (float) maxDimension / Math.max(bitmap.getWidth(), bitmap.getHeight())
        );

        int outW = Math.max(1, Math.round(bitmap.getWidth() * exportScale));
        int outH = Math.max(1, Math.round(bitmap.getHeight() * exportScale));

        Bitmap output = Bitmap.createBitmap(outW, outH, Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas(output);

        Paint exportImagePaint = new Paint(Paint.ANTI_ALIAS_FLAG | Paint.FILTER_BITMAP_FLAG);
        Rect src = new Rect(0, 0, bitmap.getWidth(), bitmap.getHeight());
        RectF dst = new RectF(0, 0, outW, outH);
        canvas.drawBitmap(bitmap, src, dst, exportImagePaint);

        Paint exportHalo = new Paint(Paint.ANTI_ALIAS_FLAG);
        exportHalo.setColor(Color.WHITE);
        exportHalo.setStyle(Paint.Style.FILL);

        Paint exportPoint = new Paint(Paint.ANTI_ALIAS_FLAG);
        exportPoint.setColor(Color.rgb(34, 191, 199));
        exportPoint.setStyle(Paint.Style.FILL);

        Paint exportText = new Paint(Paint.ANTI_ALIAS_FLAG);
        exportText.setColor(Color.rgb(225, 255, 248));
        exportText.setTextSize(Math.max(24f, 32f * exportScale));
        exportText.setFakeBoldText(true);
        exportText.setShadowLayer(4f, 1f, 1f, Color.BLACK);

        float outerRadius = Math.max(9f, 13f * exportScale);
        float innerRadius = Math.max(6f, 9f * exportScale);
        float labelOffset = Math.max(11f, 15f * exportScale);

        for (int i = 0; i < points.size(); i++) {
            PointF p = points.get(i);
            if (p == null) continue;

            float x = p.x * exportScale;
            float y = p.y * exportScale;

            canvas.drawCircle(x, y, outerRadius, exportHalo);
            canvas.drawCircle(x, y, innerRadius, exportPoint);

            String label = i < landmarkLabels.size()
                    ? landmarkLabels.get(i)
                    : String.valueOf(i + 1);

            canvas.drawText(
                    label,
                    x + labelOffset,
                    y - labelOffset,
                    exportText
            );
        }

        return output;
    }

    public Double calculate(MeasurementDefinition definition) {
        if (definition == null) return null;

        if (definition.type == MeasurementDefinition.Type.THREE_POINTS) {
            PointF a = getPoint(definition.pointLabels[0]);
            PointF b = getPoint(definition.pointLabels[1]);
            PointF c = getPoint(definition.pointLabels[2]);

            if (a == null || b == null || c == null) return null;
            return angleAtVertex(a, b, c);
        }

        PointF a = getPoint(definition.pointLabels[0]);
        PointF b = getPoint(definition.pointLabels[1]);
        PointF c = getPoint(definition.pointLabels[2]);
        PointF d = getPoint(definition.pointLabels[3]);

        if (a == null || b == null || c == null || d == null) return null;

        double raw = angleBetweenVectors(a, b, c, d);

        if (definition.chooseSupplementClosestToNorm) {
            double supplement = 180.0 - raw;
            double center = (definition.normalMin + definition.normalMax) / 2.0;

            if (Math.abs(supplement - center) < Math.abs(raw - center)) {
                return supplement;
            }
        }

        return raw;
    }

    private double angleAtVertex(PointF a, PointF b, PointF c) {
        return angleFromComponents(
                a.x - b.x,
                a.y - b.y,
                c.x - b.x,
                c.y - b.y
        );
    }

    private double angleBetweenVectors(PointF a, PointF b, PointF c, PointF d) {
        return angleFromComponents(
                b.x - a.x,
                b.y - a.y,
                d.x - c.x,
                d.y - c.y
        );
    }

    private double angleFromComponents(
            double v1x,
            double v1y,
            double v2x,
            double v2y
    ) {
        double m1 = Math.hypot(v1x, v1y);
        double m2 = Math.hypot(v2x, v2y);

        if (m1 == 0 || m2 == 0) return 0;

        double cos = (v1x * v2x + v1y * v2y) / (m1 * m2);
        cos = Math.max(-1.0, Math.min(1.0, cos));

        return Math.toDegrees(Math.acos(cos));
    }

    private void notifyProgress() {
        if (progressListener != null) {
            progressListener.onProgress(
                    getPlacedCount(),
                    landmarkLabels.size(),
                    getCurrentLabel()
            );
        }
    }
}
