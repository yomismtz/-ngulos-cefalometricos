package com.cefalo.angulos;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.PointF;
import android.view.View;

/** Simple original schematic locator. Not to scale and not used for analysis. */
public class LandmarkDiagramView extends View {
    private String landmark = "";
    private final Paint line = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint accent = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint label = new Paint(Paint.ANTI_ALIAS_FLAG);

    public LandmarkDiagramView(Context context) {
        super(context);
        line.setColor(Color.rgb(91, 83, 105));
        line.setStyle(Paint.Style.STROKE);
        line.setStrokeWidth(dp(2));
        accent.setColor(Color.rgb(142, 103, 214));
        accent.setStyle(Paint.Style.FILL);
        label.setColor(Color.rgb(50, 46, 58));
        label.setTextSize(dp(13));
        label.setFakeBoldText(true);
        setBackgroundColor(Color.rgb(248, 247, 251));
    }

    public void setLandmark(String value) {
        landmark = value == null ? "" : value;
        invalidate();
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        if (isPanoramic(landmark)) drawPanoramic(canvas);
        else drawLateral(canvas);

        PointF p = positionFor(landmark);
        float x = p.x * getWidth();
        float y = p.y * getHeight();
        canvas.drawCircle(x, y, dp(9), Paints.white());
        canvas.drawCircle(x, y, dp(6), accent);

        String shortLabel = landmark.length() > 18 ? landmark.substring(0, 18) + "…" : landmark;
        float tx = Math.min(getWidth() - label.measureText(shortLabel) - dp(8), x + dp(12));
        tx = Math.max(dp(8), tx);
        float ty = y > getHeight() * 0.78f ? y - dp(12) : y + dp(18);
        canvas.drawText(shortLabel, tx, ty, label);
    }

    private void drawLateral(Canvas c) {
        float w = getWidth(), h = getHeight();
        Path skull = new Path();
        skull.moveTo(.18f*w,.46f*h);
        skull.cubicTo(.12f*w,.16f*h,.38f*w,.06f*h,.60f*w,.16f*h);
        skull.cubicTo(.71f*w,.21f*h,.73f*w,.32f*h,.76f*w,.38f*h);
        skull.lineTo(.84f*w,.44f*h);
        skull.lineTo(.76f*w,.49f*h);
        skull.cubicTo(.78f*w,.57f*h,.73f*w,.63f*h,.71f*w,.70f*h);
        skull.cubicTo(.64f*w,.84f*h,.42f*w,.84f*h,.31f*w,.72f*h);
        skull.cubicTo(.24f*w,.63f*h,.20f*w,.55f*h,.18f*w,.46f*h);
        c.drawPath(skull, line);
        c.drawLine(.42f*w,.44f*h,.69f*w,.44f*h,line); // palate
        c.drawLine(.39f*w,.50f*h,.66f*w,.50f*h,line); // occlusion
        c.drawLine(.35f*w,.70f*h,.62f*w,.80f*h,line); // mandibular base
        c.drawLine(.27f*w,.54f*h,.25f*w,.84f*h,line); // cervical guide
        c.drawLine(.33f*w,.55f*h,.31f*w,.84f*h,line);
        c.drawCircle(.37f*w,.72f*h,dp(5),line); // hyoid cue
    }

    private void drawPanoramic(Canvas c) {
        float w = getWidth(), h = getHeight();
        Path jaw = new Path();
        jaw.moveTo(.16f*w,.31f*h);
        jaw.cubicTo(.10f*w,.48f*h,.14f*w,.78f*h,.50f*w,.86f*h);
        jaw.cubicTo(.86f*w,.78f*h,.90f*w,.48f*h,.84f*w,.31f*h);
        c.drawPath(jaw,line);
        c.drawLine(.50f*w,.12f*h,.50f*w,.90f*h,line);
        c.drawCircle(.16f*w,.23f*h,dp(11),line);
        c.drawCircle(.84f*w,.23f*h,dp(11),line);
        Path cor = new Path();
        cor.moveTo(.22f*w,.34f*h); cor.lineTo(.27f*w,.18f*h); cor.lineTo(.31f*w,.37f*h);
        c.drawPath(cor,line);
        Path cor2 = new Path();
        cor2.moveTo(.78f*w,.34f*h); cor2.lineTo(.73f*w,.18f*h); cor2.lineTo(.69f*w,.37f*h);
        c.drawPath(cor2,line);
        c.drawArc(.30f*w,.42f*h,.70f*w,.71f*h,190,160,false,line);
    }

    private boolean isPanoramic(String s) {
        return s.contains("der.") || s.contains("izq.") || s.startsWith("LM ")
                || s.startsWith("Cuerpo Md") || s.startsWith("M2 distal")
                || s.startsWith("Rama ");
    }

    private PointF positionFor(String s) {
        if (isPanoramic(s)) {
            boolean right = s.contains("der.");
            float side = right ? .82f : .18f;
            if (s.startsWith("LM ")) return new PointF(.50f, s.contains("sup") ? .22f : .55f);
            if (s.startsWith("Cd")) return new PointF(side,.23f);
            if (s.startsWith("Kr")) return new PointF(right ? .73f : .27f,.18f);
            if (s.startsWith("Go")) return new PointF(right ? .82f : .18f,.66f);
            if (s.startsWith("IC max")) return new PointF(right ? .54f : .46f,.48f);
            if (s.startsWith("IC mand")) return new PointF(right ? .54f : .46f,.58f);
            if (s.startsWith("M2")) return new PointF(right ? .66f : .34f,.55f);
            if (s.startsWith("Rama ant")) return new PointF(right ? .74f : .26f,.48f);
            if (s.startsWith("Rama post")) return new PointF(right ? .83f : .17f,.48f);
            return new PointF(side,.66f);
        }

        switch (s) {
            case "S": return new PointF(.43f,.25f);
            case "N": return new PointF(.66f,.27f);
            case "A": return new PointF(.69f,.48f);
            case "B": return new PointF(.66f,.66f);
            case "D": return new PointF(.58f,.68f);
            case "Po": return new PointF(.28f,.36f);
            case "Or": return new PointF(.53f,.35f);
            case "ENA": return new PointF(.68f,.43f);
            case "ENP": return new PointF(.43f,.43f);
            case "Ba": return new PointF(.28f,.32f);
            case "Ar": return new PointF(.29f,.48f);
            case "Go": return new PointF(.35f,.72f);
            case "Me": return new PointF(.58f,.82f);
            case "Gn": return new PointF(.64f,.79f);
            case "IS borde": return new PointF(.66f,.51f);
            case "IS ápice": return new PointF(.61f,.46f);
            case "II borde": return new PointF(.65f,.56f);
            case "II ápice": return new PointF(.59f,.63f);
            case "Oclusal 1": return new PointF(.66f,.53f);
            case "Oclusal 2": return new PointF(.45f,.52f);
            case "Cv2tg": return new PointF(.27f,.53f);
            case "Cv2ip": return new PointF(.27f,.62f);
            case "Cv4ip": return new PointF(.29f,.73f);
            case "Occipital": return new PointF(.20f,.35f);
            case "C1 posterior": return new PointF(.24f,.43f);
            case "Odontoides ápice": return new PointF(.28f,.47f);
            case "C2 anteroinf.": return new PointF(.34f,.61f);
            case "C3": return new PointF(.34f,.69f);
            case "RGn": return new PointF(.48f,.76f);
            case "H": return new PointF(.42f,.72f);
            case "AA": return new PointF(.35f,.45f);
            case "C2 post-sup.": return new PointF(.25f,.50f);
            case "C7 post-inf.": return new PointF(.29f,.86f);
            case "Profundidad cervical": return new PointF(.34f,.71f);
            case "G'": return new PointF(.72f,.23f);
            case "N'": return new PointF(.75f,.30f);
            case "Pr": return new PointF(.84f,.42f);
            case "Pg'": return new PointF(.75f,.70f);
            case "Me'": return new PointF(.65f,.82f);
            case "C": return new PointF(.48f,.86f);
            case "AD1": return new PointF(.31f,.44f);
            case "AD2": return new PointF(.32f,.39f);
            case "Faringe sup ant.": return new PointF(.43f,.51f);
            case "Faringe sup post.": return new PointF(.29f,.51f);
            case "Faringe inf ant.": return new PointF(.47f,.65f);
            case "Faringe inf post.": return new PointF(.30f,.65f);
            default: return new PointF(.50f,.50f);
        }
    }

    private float dp(float v) {
        return v * getResources().getDisplayMetrics().density;
    }

    private static final class Paints {
        private static Paint white;
        static Paint white() {
            if (white == null) {
                white = new Paint(Paint.ANTI_ALIAS_FLAG);
                white.setColor(Color.WHITE);
                white.setStyle(Paint.Style.FILL);
            }
            return white;
        }
    }
}
