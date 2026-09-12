package com.cefalo.angulos;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Matrix;
import android.graphics.Paint;
import android.graphics.RectF;
import android.util.AttributeSet;
import android.view.MotionEvent;
import android.view.ScaleGestureDetector;
import android.view.View;

/**
 * Lightweight radiograph viewer for qualitative assessments. One finger pans,
 * pinch zooms and the image can be reset with fitImage(). It intentionally has
 * no landmark-placement behavior.
 */
public class RadiographImageView extends View {
    private final Paint imagePaint = new Paint(Paint.ANTI_ALIAS_FLAG | Paint.FILTER_BITMAP_FLAG);
    private final Paint textPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Matrix matrix = new Matrix();
    private final ScaleGestureDetector scaleDetector;

    private Bitmap bitmap;
    private float relativeZoom = 1f;
    private float lastX;
    private float lastY;
    private boolean moved;

    public RadiographImageView(Context context) {
        this(context, null);
    }

    public RadiographImageView(Context context, AttributeSet attrs) {
        super(context, attrs);
        setClickable(true);
        textPaint.setColor(Color.rgb(225, 255, 248));
        textPaint.setTextSize(dp(16));
        textPaint.setFakeBoldText(true);

        scaleDetector = new ScaleGestureDetector(
                context,
                new ScaleGestureDetector.SimpleOnScaleGestureListener() {
                    @Override
                    public boolean onScale(ScaleGestureDetector detector) {
                        if (bitmap == null) return false;
                        float desired = Math.max(
                                1f,
                                Math.min(8f, relativeZoom * detector.getScaleFactor())
                        );
                        float factor = desired / relativeZoom;
                        relativeZoom = desired;
                        matrix.postScale(
                                factor,
                                factor,
                                detector.getFocusX(),
                                detector.getFocusY()
                        );
                        constrain();
                        invalidate();
                        return true;
                    }
                }
        );
    }

    public void setBitmap(Bitmap bitmap) {
        this.bitmap = bitmap;
        post(this::fitImage);
    }

    public boolean hasBitmap() {
        return bitmap != null;
    }

    public void fitImage() {
        if (bitmap == null || getWidth() <= 0 || getHeight() <= 0) return;
        float scale = Math.min(
                (float) getWidth() / bitmap.getWidth(),
                (float) getHeight() / bitmap.getHeight()
        );
        float width = bitmap.getWidth() * scale;
        float height = bitmap.getHeight() * scale;
        matrix.reset();
        matrix.setScale(scale, scale);
        matrix.postTranslate(
                (getWidth() - width) / 2f,
                (getHeight() - height) / 2f
        );
        relativeZoom = 1f;
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
            canvas.drawText("Abra una radiografía", dp(18), dp(42), textPaint);
            return;
        }
        canvas.drawBitmap(bitmap, matrix, imagePaint);
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        if (bitmap == null) return true;
        scaleDetector.onTouchEvent(event);

        switch (event.getActionMasked()) {
            case MotionEvent.ACTION_DOWN:
                lastX = event.getX();
                lastY = event.getY();
                moved = false;
                return true;

            case MotionEvent.ACTION_MOVE:
                if (event.getPointerCount() == 1 && !scaleDetector.isInProgress()) {
                    float x = event.getX();
                    float y = event.getY();
                    float dx = x - lastX;
                    float dy = y - lastY;
                    if (Math.hypot(dx, dy) > dp(1)) moved = true;
                    matrix.postTranslate(dx, dy);
                    constrain();
                    lastX = x;
                    lastY = y;
                    invalidate();
                }
                return true;

            case MotionEvent.ACTION_UP:
                if (!moved) performClick();
                return true;

            case MotionEvent.ACTION_CANCEL:
                return true;

            default:
                return true;
        }
    }

    @Override
    public boolean performClick() {
        super.performClick();
        return true;
    }

    private void constrain() {
        if (bitmap == null || getWidth() <= 0 || getHeight() <= 0) return;
        RectF rect = new RectF(0, 0, bitmap.getWidth(), bitmap.getHeight());
        matrix.mapRect(rect);

        float dx = 0f;
        float dy = 0f;

        if (rect.width() <= getWidth()) {
            dx = getWidth() / 2f - rect.centerX();
        } else if (rect.left > 0) {
            dx = -rect.left;
        } else if (rect.right < getWidth()) {
            dx = getWidth() - rect.right;
        }

        if (rect.height() <= getHeight()) {
            dy = getHeight() / 2f - rect.centerY();
        } else if (rect.top > 0) {
            dy = -rect.top;
        } else if (rect.bottom < getHeight()) {
            dy = getHeight() - rect.bottom;
        }

        matrix.postTranslate(dx, dy);
    }

    private float dp(float value) {
        return value * getResources().getDisplayMetrics().density;
    }
}
