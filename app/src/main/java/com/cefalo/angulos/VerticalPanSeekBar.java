package com.cefalo.angulos;

import android.content.Context;
import android.graphics.Canvas;
import android.util.AttributeSet;
import android.view.MotionEvent;

import androidx.appcompat.widget.AppCompatSeekBar;

/**
 * Vertical SeekBar used only to navigate the visible radiograph viewport.
 * Progress grows from bottom to top after rotation, so AnalysisActivity
 * converts it to the image-space top-to-bottom fraction.
 */
public class VerticalPanSeekBar extends AppCompatSeekBar {

    public VerticalPanSeekBar(Context context) {
        super(context);
    }

    public VerticalPanSeekBar(Context context, AttributeSet attrs) {
        super(context, attrs);
    }

    public VerticalPanSeekBar(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
    }

    @Override
    protected synchronized void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
        super.onMeasure(heightMeasureSpec, widthMeasureSpec);
        setMeasuredDimension(getMeasuredHeight(), getMeasuredWidth());
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(h, w, oldh, oldw);
    }

    @Override
    protected synchronized void onDraw(Canvas canvas) {
        canvas.rotate(-90f);
        canvas.translate(-getHeight(), 0f);
        super.onDraw(canvas);
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        if (!isEnabled()) return false;

        switch (event.getActionMasked()) {
            case MotionEvent.ACTION_DOWN:
            case MotionEvent.ACTION_MOVE:
            case MotionEvent.ACTION_UP:
                float fraction = 1f - (event.getY() / Math.max(1f, getHeight()));
                fraction = Math.max(0f, Math.min(1f, fraction));
                setProgress(Math.round(getMax() * fraction));
                if (event.getActionMasked() == MotionEvent.ACTION_UP) {
                    performClick();
                }
                return true;
            default:
                return super.onTouchEvent(event);
        }
    }

    @Override
    public boolean performClick() {
        super.performClick();
        return true;
    }
}
