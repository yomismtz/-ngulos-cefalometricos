package com.cefalo.angulos;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Matrix;
import android.graphics.Paint;
import android.graphics.PointF;
import android.util.AttributeSet;
import android.view.MotionEvent;
import android.view.ScaleGestureDetector;
import android.view.View;

import java.util.ArrayList;
import java.util.List;

public class MeasurementView extends View {

    public interface ProgressListener {
        void onProgress(int placed, int total, String nextLabel);
    }

    private Bitmap bitmap;
    private final List<String> landmarkLabels = new ArrayList<>();
    private final List<PointF> points = new ArrayList<>();

    private final Paint imagePaint = new Paint(Paint.ANTI_ALIAS_FLAG | Paint.FILTER_BITMAP_FLAG);
    private final Paint pointPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint haloPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint textPaint = new Paint(Paint.ANTI_ALIAS_FLAG);

    private final Matrix matrix = new Matrix();
    private final Matrix inverse = new Matrix();
    private float zoom = 1f;

    private final ScaleGestureDetector scaleDetector;
    private float lastTwoFingerX, lastTwoFingerY;
    private boolean twoFingerTracking = false;
    private int draggingPoint = -1;
    private float downX, downY;
    private boolean moved = false;

    private ProgressListener progressListener;

    public MeasurementView(Context context, AttributeSet attrs) {
        super(context, attrs);
        setLayerType(View.LAYER_TYPE_SOFTWARE, null);

        pointPaint.setColor(Color.rgb(34, 191, 199));
        pointPaint.setStyle(Paint.Style.FILL);

        haloPaint.setColor(Color.WHITE);
        haloPaint.setStyle(Paint.Style.FILL);

        textPaint.setColor(Color.rgb(225, 255, 248));
        textPaint.setTextSize(25f);
        textPaint.setFakeBoldText(true);
        textPaint.setShadowLayer(5f, 1f, 1f, Color.BLACK);

        scaleDetector = new ScaleGestureDetector(context,
                new ScaleGestureDetector.SimpleOnScaleGestureListener() {
                    @Override
                    public boolean onScale(ScaleGestureDetector detector) {
                        if (bitmap == null) return false;
                        float factor = detector.getScaleFactor();
                        float newZoom = Math.max(1f, Math.min(8f, zoom * factor));
                        factor = newZoom / zoom;
                        zoom = newZoom;
                        matrix.postScale(factor, factor, detector.getFocusX(), detector.getFocusY());
                        updateInverse();
                        invalidate();
                        return true;
                    }
                });
    }

    public void setProgressListener(ProgressListener listener) {
        this.progressListener = listener;
        notifyProgress();
    }

    public void setLandmarks(List<String> labels) {
        landmarkLabels.clear();
        landmarkLabels.addAll(labels);
        points.clear();
        notifyProgress();
        invalidate();
    }

    public void setBitmap(Bitmap b) {
        bitmap = b;
        points.clear();
        fitImage();
        notifyProgress();
        invalidate();
    }

    public boolean hasBitmap() {
        return bitmap != null;
    }

    public boolean isComplete() {
        return !landmarkLabels.isEmpty() && points.size() == landmarkLabels.size();
    }

    public int getPlacedCount() {
        return points.size();
    }

    public int getTotalCount() {
        return landmarkLabels.size();
    }

    public String getNextLabel() {
        if (points.size() >= landmarkLabels.size()) return null;
        return landmarkLabels.get(points.size());
    }

    public PointF getPoint(String label) {
        int index = landmarkLabels.indexOf(label);
        if (index < 0 || index >= points.size()) return null;
        PointF p = points.get(index);
        return new PointF(p.x, p.y);
    }

    public void undo() {
        if (!points.isEmpty()) {
            points.remove(points.size() - 1);
            notifyProgress();
            invalidate();
        }
    }

    public void resetMeasurement() {
        points.clear();
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
    }

    private void drawPoints(Canvas canvas) {
        for (int i = 0; i < points.size(); i++) {
            PointF s = imageToScreen(points.get(i));

            canvas.drawCircle(s.x, s.y, 12f, haloPaint);
            canvas.drawCircle(s.x, s.y, 8f, pointPaint);

            String label = i < landmarkLabels.size() ? landmarkLabels.get(i) : String.valueOf(i + 1);
            textPaint.setTextSize(25f);
            canvas.drawText(label, s.x + 14f, s.y - 14f, textPaint);
        }
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        if (bitmap == null || landmarkLabels.isEmpty()) return true;

        scaleDetector.onTouchEvent(event);

        if (event.getPointerCount() >= 2) {
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
                draggingPoint = findNearbyPoint(downX, downY, 36f);
                return true;

            case MotionEvent.ACTION_MOVE:
                if (Math.hypot(event.getX() - downX, event.getY() - downY) > 8) {
                    moved = true;
                }

                if (draggingPoint >= 0) {
                    PointF p = screenToImage(event.getX(), event.getY());
                    if (insideImage(p)) {
                        points.set(draggingPoint, p);
                        invalidate();
                    }
                }
                return true;

            case MotionEvent.ACTION_UP:
                if (draggingPoint >= 0) {
                    draggingPoint = -1;
                    return true;
                }

                if (!moved && points.size() < landmarkLabels.size()) {
                    addPoint(event.getX(), event.getY());
                }
                return true;

            case MotionEvent.ACTION_CANCEL:
                draggingPoint = -1;
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

        if (event.getActionMasked() == MotionEvent.ACTION_MOVE && !scaleDetector.isInProgress()) {
            matrix.postTranslate(cx - lastTwoFingerX, cy - lastTwoFingerY);
            updateInverse();
            invalidate();
        }

        lastTwoFingerX = cx;
        lastTwoFingerY = cy;
    }

    private void addPoint(float sx, float sy) {
        PointF p = screenToImage(sx, sy);
        if (!insideImage(p)) return;

        points.add(p);
        notifyProgress();
        invalidate();
    }

    private int findNearbyPoint(float sx, float sy, float radiusPx) {
        for (int i = 0; i < points.size(); i++) {
            PointF p = imageToScreen(points.get(i));
            if (Math.hypot(sx - p.x, sy - p.y) <= radiusPx) return i;
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
        return p.x >= 0 && p.y >= 0 && p.x <= bitmap.getWidth() && p.y <= bitmap.getHeight();
    }

    private void updateInverse() {
        matrix.invert(inverse);
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
        return angleFromComponents(a.x - b.x, a.y - b.y, c.x - b.x, c.y - b.y);
    }

    private double angleBetweenVectors(PointF a, PointF b, PointF c, PointF d) {
        return angleFromComponents(b.x - a.x, b.y - a.y, d.x - c.x, d.y - c.y);
    }

    private double angleFromComponents(double v1x, double v1y, double v2x, double v2y) {
        double m1 = Math.hypot(v1x, v1y);
        double m2 = Math.hypot(v2x, v2y);

        if (m1 == 0 || m2 == 0) return 0;

        double cos = (v1x * v2x + v1y * v2y) / (m1 * m2);
        cos = Math.max(-1.0, Math.min(1.0, cos));

        return Math.toDegrees(Math.acos(cos));
    }

    private void notifyProgress() {
        if (progressListener != null) {
            progressListener.onProgress(points.size(), landmarkLabels.size(), getNextLabel());
        }
    }
}
