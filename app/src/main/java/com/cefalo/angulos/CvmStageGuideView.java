package com.cefalo.angulos;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RectF;
import android.util.AttributeSet;
import android.view.View;

/**
 * Original schematic aid for the modified CVM method. It is deliberately a
 * diagram rather than a copied published radiograph/figure.
 */
public class CvmStageGuideView extends View {
    private final Paint line = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint accent = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint text = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint subtext = new Paint(Paint.ANTI_ALIAS_FLAG);

    public CvmStageGuideView(Context context) {
        this(context, null);
    }

    public CvmStageGuideView(Context context, AttributeSet attrs) {
        super(context, attrs);
        line.setStyle(Paint.Style.STROKE);
        line.setStrokeWidth(dp(1.5f));
        line.setColor(context.getColor(R.color.text_primary));

        accent.setStyle(Paint.Style.STROKE);
        accent.setStrokeWidth(dp(2.2f));
        accent.setColor(context.getColor(R.color.brand_teal));

        text.setColor(context.getColor(R.color.brand_purple));
        text.setTextSize(dp(12));
        text.setFakeBoldText(true);
        text.setTextAlign(Paint.Align.CENTER);

        subtext.setColor(context.getColor(R.color.text_secondary));
        subtext.setTextSize(dp(8.5f));
        subtext.setTextAlign(Paint.Align.CENTER);

        setContentDescription("Esquema comparativo de maduración cervical CS1 a CS6 usando C2, C3 y C4");
        setMinimumHeight((int) dp(325));
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        float w = getWidth();
        if (w <= 0) return;

        float margin = dp(5);
        float gap = dp(5);
        float cellW = (w - margin * 2 - gap) / 2f;
        float cellH = dp(102);

        for (int stage = 1; stage <= 6; stage++) {
            int index = stage - 1;
            int col = index % 2;
            int row = index / 2;
            float left = margin + col * (cellW + gap);
            float top = dp(4) + row * cellH;
            drawStage(canvas, stage, left, top, cellW, cellH - dp(4));
        }
    }

    private void drawStage(Canvas c, int stage, float left, float top, float width, float height) {
        RectF card = new RectF(left, top, left + width, top + height);
        Paint cardPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        cardPaint.setStyle(Paint.Style.STROKE);
        cardPaint.setStrokeWidth(dp(1));
        cardPaint.setColor(getContext().getColor(R.color.card_stroke));
        c.drawRoundRect(card, dp(8), dp(8), cardPaint);

        c.drawText("CS" + stage, card.centerX(), top + dp(16), text);

        float cx = left + width * 0.35f;
        float y2 = top + dp(31);
        float vertebraW = width * 0.33f;
        float h2 = dp(13);
        float h3 = dp(16);
        float h4 = dp(16);
        float gap = dp(6);

        // C2 is shown as a compact vertebral body because the diagnostic cue is
        // the inferior border, not the complete odontoid anatomy.
        drawBody(c, cx, y2, vertebraW, h2, bodyShape(stage, 2), concave(stage, 2));
        drawLabel(c, "C2", left + width * 0.68f, y2 + h2 * 0.65f);

        float y3 = y2 + h2 + gap;
        drawBody(c, cx, y3, vertebraW, h3, bodyShape(stage, 3), concave(stage, 3));
        drawLabel(c, "C3", left + width * 0.68f, y3 + h3 * 0.65f);

        float y4 = y3 + h3 + gap;
        drawBody(c, cx, y4, vertebraW, h4, bodyShape(stage, 4), concave(stage, 4));
        drawLabel(c, "C4", left + width * 0.68f, y4 + h4 * 0.65f);

        String cue;
        if (stage == 1) cue = "planas · trap.";
        else if (stage == 2) cue = "C2 cóncava";
        else if (stage == 3) cue = "C2+C3 cóncavas";
        else if (stage == 4) cue = "3 cóncavas · horiz.";
        else if (stage == 5) cue = "3 cóncavas · cuadrada";
        else cue = "3 cóncavas · vertical";
        c.drawText(cue, card.centerX(), top + height - dp(6), subtext);
    }

    private int bodyShape(int stage, int vertebra) {
        if (vertebra == 2) return 1;
        if (stage <= 2) return 0;      // trapezoid
        if (stage == 3) return 1;      // simplified horizontal/intermediate
        if (stage == 4) return 1;      // horizontal rectangle
        if (stage == 5) return 2;      // square
        return 3;                      // vertical rectangle
    }

    private boolean concave(int stage, int vertebra) {
        if (stage == 1) return false;
        if (stage == 2) return vertebra == 2;
        if (stage == 3) return vertebra == 2 || vertebra == 3;
        return true;
    }

    private void drawBody(
            Canvas c,
            float centerX,
            float top,
            float baseWidth,
            float baseHeight,
            int shape,
            boolean concavity
    ) {
        float width = baseWidth;
        float height = baseHeight;
        if (shape == 2) {
            width = Math.min(baseWidth, baseHeight * 1.05f);
            height = width;
        } else if (shape == 3) {
            width = baseWidth * 0.72f;
            height = baseHeight * 1.22f;
        } else if (shape == 1) {
            width = baseWidth * 1.05f;
            height = baseHeight * 0.78f;
        }

        float l = centerX - width / 2f;
        float r = centerX + width / 2f;
        float b = top + height;

        Path p = new Path();
        if (shape == 0) {
            // Superior border slopes downward anteriorly to suggest trapezoid.
            p.moveTo(l + width * 0.16f, top);
            p.lineTo(r, top + height * 0.15f);
        } else {
            p.moveTo(l, top);
            p.lineTo(r, top);
        }
        p.lineTo(r, b);

        if (concavity) {
            p.cubicTo(
                    centerX + width * 0.28f, b,
                    centerX + width * 0.18f, b - height * 0.30f,
                    centerX, b - height * 0.30f
            );
            p.cubicTo(
                    centerX - width * 0.18f, b - height * 0.30f,
                    centerX - width * 0.28f, b,
                    l, b
            );
        } else {
            p.lineTo(l, b);
        }
        p.close();
        c.drawPath(p, concavity ? accent : line);
    }

    private void drawLabel(Canvas c, String value, float x, float y) {
        c.drawText(value, x, y, subtext);
    }

    private float dp(float value) {
        return value * getResources().getDisplayMetrics().density;
    }
}
