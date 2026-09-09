package com.cefalo.angulos;

import android.content.Context;
import android.util.AttributeSet;
import android.view.View;
import android.view.ViewGroup;

public class LandmarkFlowLayout extends ViewGroup {

    private int horizontalSpacing;
    private int verticalSpacing;

    public LandmarkFlowLayout(Context context) {
        super(context);
        init();
    }

    public LandmarkFlowLayout(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    public LandmarkFlowLayout(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init();
    }

    private void init() {
        float density = getResources().getDisplayMetrics().density;
        horizontalSpacing = Math.round(5f * density);
        verticalSpacing = Math.round(5f * density);
        setClipToPadding(false);
    }

    @Override
    protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
        int widthSize = MeasureSpec.getSize(widthMeasureSpec);
        int widthMode = MeasureSpec.getMode(widthMeasureSpec);

        int availableWidth = Math.max(
                0,
                widthSize - getPaddingLeft() - getPaddingRight()
        );

        int lineWidth = 0;
        int lineHeight = 0;
        int totalHeight = getPaddingTop() + getPaddingBottom();
        int maxLineWidth = 0;
        boolean hasVisibleChild = false;

        for (int i = 0; i < getChildCount(); i++) {
            View child = getChildAt(i);

            if (child.getVisibility() == GONE) continue;

            hasVisibleChild = true;
            measureChildWithMargins(
                    child,
                    widthMeasureSpec,
                    getPaddingLeft() + getPaddingRight(),
                    heightMeasureSpec,
                    getPaddingTop() + getPaddingBottom()
            );

            MarginLayoutParams lp = (MarginLayoutParams) child.getLayoutParams();

            int childWidth =
                    child.getMeasuredWidth() +
                    lp.leftMargin +
                    lp.rightMargin;

            int childHeight =
                    child.getMeasuredHeight() +
                    lp.topMargin +
                    lp.bottomMargin;

            int proposed =
                    lineWidth == 0
                            ? childWidth
                            : lineWidth + horizontalSpacing + childWidth;

            if (availableWidth > 0
                    && lineWidth > 0
                    && proposed > availableWidth) {

                maxLineWidth = Math.max(maxLineWidth, lineWidth);
                totalHeight += lineHeight + verticalSpacing;

                lineWidth = childWidth;
                lineHeight = childHeight;

            } else {
                lineWidth = proposed;
                lineHeight = Math.max(lineHeight, childHeight);
            }
        }

        if (hasVisibleChild) {
            maxLineWidth = Math.max(maxLineWidth, lineWidth);
            totalHeight += lineHeight;
        }

        int desiredWidth =
                maxLineWidth +
                getPaddingLeft() +
                getPaddingRight();

        int measuredWidth =
                widthMode == MeasureSpec.EXACTLY
                        ? widthSize
                        : resolveSize(desiredWidth, widthMeasureSpec);

        int measuredHeight =
                resolveSize(totalHeight, heightMeasureSpec);

        setMeasuredDimension(measuredWidth, measuredHeight);
    }

    @Override
    protected void onLayout(
            boolean changed,
            int left,
            int top,
            int right,
            int bottom
    ) {
        int availableWidth =
                right - left - getPaddingLeft() - getPaddingRight();

        int x = getPaddingLeft();
        int y = getPaddingTop();
        int lineHeight = 0;

        for (int i = 0; i < getChildCount(); i++) {
            View child = getChildAt(i);

            if (child.getVisibility() == GONE) continue;

            MarginLayoutParams lp = (MarginLayoutParams) child.getLayoutParams();

            int childWidth = child.getMeasuredWidth();
            int childHeight = child.getMeasuredHeight();

            int requiredWidth =
                    lp.leftMargin +
                    childWidth +
                    lp.rightMargin;

            if (x > getPaddingLeft()
                    && x + requiredWidth > getPaddingLeft() + availableWidth) {

                x = getPaddingLeft();
                y += lineHeight + verticalSpacing;
                lineHeight = 0;
            }

            int childLeft = x + lp.leftMargin;
            int childTop = y + lp.topMargin;

            child.layout(
                    childLeft,
                    childTop,
                    childLeft + childWidth,
                    childTop + childHeight
            );

            x =
                    childLeft +
                    childWidth +
                    lp.rightMargin +
                    horizontalSpacing;

            lineHeight = Math.max(
                    lineHeight,
                    lp.topMargin +
                    childHeight +
                    lp.bottomMargin
            );
        }
    }

    @Override
    protected LayoutParams generateDefaultLayoutParams() {
        return new MarginLayoutParams(
                LayoutParams.WRAP_CONTENT,
                LayoutParams.WRAP_CONTENT
        );
    }

    @Override
    public LayoutParams generateLayoutParams(AttributeSet attrs) {
        return new MarginLayoutParams(getContext(), attrs);
    }

    @Override
    protected LayoutParams generateLayoutParams(LayoutParams p) {
        return new MarginLayoutParams(p);
    }

    @Override
    protected boolean checkLayoutParams(LayoutParams p) {
        return p instanceof MarginLayoutParams;
    }
}
