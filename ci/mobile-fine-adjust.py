from pathlib import Path
import re

activity = Path('app/src/main/java/com/cefalo/angulos/AnalysisActivity.java')
a = activity.read_text(encoding='utf-8')

# Replace the previous fixed-density nudge pad with an image-pixel based pad.
pattern = re.compile(r'''    private void showFineAdjustDialog\(\) \{.*?\n    \}\n\n(?=    private void polishStaticTextAlignment\(\))''', re.S)
m = pattern.search(a)
if m:
    method = '''    private void showFineAdjustDialog() {
        if (measurementView == null) return;

        int selected = measurementView.getSelectedIndex();
        if (selected < 0 || !measurementView.hasPointAt(selected)) {
            Toast.makeText(this, "Coloque o seleccione primero un punto.", Toast.LENGTH_SHORT).show();
            return;
        }
        if (measurementView.isPointLocked(selected)) {
            Toast.makeText(this, "Desbloquee el punto antes de ajustarlo.", Toast.LENGTH_SHORT).show();
            return;
        }

        final float[] step = {0.5f};
        final int[] axis = {0}; // 0 libre, 1 horizontal, 2 vertical

        LinearLayout pad = new LinearLayout(this);
        pad.setOrientation(LinearLayout.VERTICAL);
        pad.setGravity(Gravity.CENTER);
        pad.setPadding(dp(14), dp(8), dp(14), dp(8));

        TextView help = new TextView(this);
        help.setText("Punto: " + measurementView.getCurrentLabel() +
                "\nEl paso se expresa en píxeles de la imagen y no cambia con el zoom.");
        help.setTextSize(13f);
        help.setGravity(Gravity.CENTER);
        help.setTextAlignment(View.TEXT_ALIGNMENT_CENTER);
        help.setPadding(0, 0, 0, dp(8));
        pad.addView(help);

        TextView stepTitle = new TextView(this);
        stepTitle.setText("PASO · 0.5 px");
        stepTitle.setTypeface(null, Typeface.BOLD);
        stepTitle.setGravity(Gravity.CENTER);
        pad.addView(stepTitle);

        LinearLayout steps = new LinearLayout(this);
        steps.setOrientation(LinearLayout.HORIZONTAL);
        steps.setGravity(Gravity.CENTER);
        final float[] values = {0.1f, 0.5f, 1.0f};
        final TextView[] stepButtons = new TextView[3];
        for (int i = 0; i < values.length; i++) {
            TextView b = makePrecisionChoice(values[i] + " px");
            stepButtons[i] = b;
            final int index = i;
            b.setOnClickListener(v -> {
                step[0] = values[index];
                stepTitle.setText("PASO · " + values[index] + " px");
                for (int j = 0; j < stepButtons.length; j++) {
                    stepButtons[j].setAlpha(j == index ? 1f : 0.55f);
                }
            });
            b.setAlpha(i == 1 ? 1f : 0.55f);
            steps.addView(b, new LinearLayout.LayoutParams(dp(82), dp(44)));
        }
        pad.addView(steps);

        TextView axisTitle = new TextView(this);
        axisTitle.setText("BLOQUEO DE EJE · LIBRE");
        axisTitle.setTypeface(null, Typeface.BOLD);
        axisTitle.setGravity(Gravity.CENTER);
        axisTitle.setPadding(0, dp(8), 0, 0);
        pad.addView(axisTitle);

        LinearLayout axes = new LinearLayout(this);
        axes.setOrientation(LinearLayout.HORIZONTAL);
        axes.setGravity(Gravity.CENTER);
        final String[] axisNames = {"LIBRE", "HORIZONTAL", "VERTICAL"};
        final TextView[] axisButtons = new TextView[3];
        for (int i = 0; i < axisNames.length; i++) {
            TextView b = makePrecisionChoice(axisNames[i]);
            b.setTextSize(9.5f);
            axisButtons[i] = b;
            final int index = i;
            b.setOnClickListener(v -> {
                axis[0] = index;
                axisTitle.setText("BLOQUEO DE EJE · " + axisNames[index]);
                for (int j = 0; j < axisButtons.length; j++) {
                    axisButtons[j].setAlpha(j == index ? 1f : 0.55f);
                }
            });
            b.setAlpha(i == 0 ? 1f : 0.55f);
            axes.addView(b, new LinearLayout.LayoutParams(dp(90), dp(44)));
        }
        pad.addView(axes);

        final String[][] symbols = {
                {"↖", "↑", "↗"},
                {"←", "●", "→"},
                {"↙", "↓", "↘"}
        };
        final float[][] dx = {
                {-1f, 0f, 1f},
                {-1f, 0f, 1f},
                {-1f, 0f, 1f}
        };
        final float[][] dy = {
                {-1f, -1f, -1f},
                {0f, 0f, 0f},
                {1f, 1f, 1f}
        };

        for (int r = 0; r < 3; r++) {
            LinearLayout row = new LinearLayout(this);
            row.setOrientation(LinearLayout.HORIZONTAL);
            row.setGravity(Gravity.CENTER);
            for (int c = 0; c < 3; c++) {
                TextView key = new TextView(this);
                key.setText(symbols[r][c]);
                key.setTextSize(r == 1 && c == 1 ? 15f : 23f);
                key.setGravity(Gravity.CENTER);
                key.setTextAlignment(View.TEXT_ALIGNMENT_CENTER);
                key.setIncludeFontPadding(false);
                LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(dp(58), dp(50));
                lp.setMargins(dp(2), dp(2), dp(2), dp(2));
                key.setLayoutParams(lp);

                if (r == 1 && c == 1) {
                    key.setAlpha(0.35f);
                } else {
                    key.setBackgroundResource(R.drawable.button_soft_purple_centered);
                    final float ux = dx[r][c];
                    final float uy = dy[r][c];
                    key.setOnClickListener(v -> {
                        float moveX = ux * step[0];
                        float moveY = uy * step[0];
                        if (axis[0] == 1) moveY = 0f;
                        if (axis[0] == 2) moveX = 0f;
                        measurementView.nudgeSelectedPointImagePixels(moveX, moveY);
                    });
                }
                row.addView(key);
            }
            pad.addView(row);
        }

        new AlertDialog.Builder(this)
                .setTitle("🎯 Ajuste fino")
                .setView(pad)
                .setNeutralButton("¿Dónde está?", (d, w) -> showCurrentPointGuide())
                .setPositiveButton("Cerrar", null)
                .show();
    }

    private TextView makePrecisionChoice(String value) {
        TextView tv = new TextView(this);
        tv.setText(value);
        tv.setGravity(Gravity.CENTER);
        tv.setTextAlignment(View.TEXT_ALIGNMENT_CENTER);
        tv.setIncludeFontPadding(false);
        tv.setTextSize(11f);
        tv.setTypeface(null, Typeface.BOLD);
        tv.setTextColor(getColor(R.color.brand_purple));
        tv.setBackgroundResource(R.drawable.button_soft_purple_centered);
        tv.setClickable(true);
        tv.setFocusable(true);
        return tv;
    }

'''
    a = a[:m.start()] + method + a[m.end():]

activity.write_text(a, encoding='utf-8')

# Add an exact image-space movement API. The previous method accepts screen
# pixels and divides by current zoom; this one is intentionally zoom-independent.
view = Path('app/src/main/java/com/cefalo/angulos/MeasurementView.java')
v = view.read_text(encoding='utf-8')
if 'nudgeSelectedPointImagePixels' not in v:
    anchor = '''    @Override
    public boolean onTouchEvent(MotionEvent event) {'''
    method = '''    public boolean nudgeSelectedPointImagePixels(float imageDx, float imageDy) {
        if (bitmap == null
                || locked
                || selectedIndex < 0
                || selectedIndex >= points.size()
                || isPointLocked(selectedIndex)) {
            return false;
        }

        PointF current = points.get(selectedIndex);
        if (current == null) return false;

        PointF adjusted = new PointF(
                clamp(current.x + imageDx, 0f, bitmap.getWidth()),
                clamp(current.y + imageDy, 0f, bitmap.getHeight())
        );
        points.set(selectedIndex, adjusted);
        notifyProgress();
        invalidate();
        return true;
    }

'''
    if anchor in v:
        v = v.replace(anchor, method + anchor, 1)
view.write_text(v, encoding='utf-8')

print('Exact 0.1/0.5/1 px fine adjustment and axis locking applied.')
