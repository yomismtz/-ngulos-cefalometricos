from pathlib import Path

# -----------------------------------------------------------------------------
# Clinical / partial-result patches
# -----------------------------------------------------------------------------
analysis = Path('app/src/main/java/com/cefalo/angulos/AnalysisActivity.java')
text = analysis.read_text(encoding='utf-8')

old = '''        } else {
            definitions = MeasurementCatalog.steiner();
        }
'''
new = '''        } else {
            definitions = MeasurementCatalog.steiner();
            linearDefinitions = LinearMeasurementCatalog.cephalometric();
        }
'''
if old in text:
    text = text.replace(old, new, 1)

needle = '''        if (def.type == LinearMeasurementDefinition.Type.DISTANCE) {
            PointF a = measurementView.getPoint(def.pointLabels[0]);
            PointF b = measurementView.getPoint(def.pointLabels[1]);

            if (a == null || b == null) return null;

            return Math.hypot(
                    b.x - a.x,
                    b.y - a.y
            ) * mmPerPixel;
        }

        PointF a = measurementView.getPoint(def.pointLabels[0]);
'''
replacement = '''        if (def.type == LinearMeasurementDefinition.Type.DISTANCE) {
            PointF a = measurementView.getPoint(def.pointLabels[0]);
            PointF b = measurementView.getPoint(def.pointLabels[1]);

            if (a == null || b == null) return null;

            return Math.hypot(
                    b.x - a.x,
                    b.y - a.y
            ) * mmPerPixel;
        }

        if (def.type == LinearMeasurementDefinition.Type.AXIAL_PROJECTION) {
            PointF a = measurementView.getPoint(def.pointLabels[0]);
            PointF b = measurementView.getPoint(def.pointLabels[1]);
            PointF p = measurementView.getPoint(def.pointLabels[2]);

            if (a == null || b == null || p == null) return null;

            double dx = b.x - a.x;
            double dy = b.y - a.y;
            double length = Math.hypot(dx, dy);
            if (length == 0.0) return null;

            double axialPixels =
                    ((p.x - a.x) * dx + (p.y - a.y) * dy) / length;

            // SL y SE son longitudes S-L / S-E sobre el eje SN, no distancias
            // perpendiculares. Se informa la magnitud de la proyección construida.
            return Math.abs(axialPixels) * mmPerPixel;
        }

        PointF a = measurementView.getPoint(def.pointLabels[0]);
'''
if needle in text:
    text = text.replace(needle, replacement, 1)

old_complete = '''        if (!measurementView.isComplete()) {
            String next =
                    measurementView.getCurrentLabel();

            Toast.makeText(
                    this,
                    "Faltan puntos. Seleccionado: " +
                    (
                            next == null
                                    ? "—"
                                    : next
                    ),
                    Toast.LENGTH_LONG
            ).show();

            return;
        }

'''
new_complete = '''        if (measurementView.getPlacedCount() < 2) {
            Toast.makeText(
                    this,
                    "Coloque los puntos necesarios para al menos una medición.",
                    Toast.LENGTH_LONG
            ).show();
            return;
        }

'''
if old_complete in text:
    text = text.replace(old_complete, new_complete, 1)

# Thematic titles: the modules are no longer presented as literal author analyses.
old_titles = '''    private String modeTitle() {
        if ("VERTEBRAL".equals(mode)) return "Vertebral / Rocabado";
        if ("POWELL".equals(mode)) return "Análisis de Powell";
        if ("TWEED".equals(mode)) return "Análisis de Tweed";
        if ("LEVANDOSKI".equals(mode)) return "Panorámico de Levandoski";
        if ("AIRWAY".equals(mode)) return "Análisis de vía aérea";
        return "Análisis de Steiner";
    }
'''
new_titles = '''    private String modeTitle() {
        if ("VERTEBRAL".equals(mode)) return "Postura cráneo-cervical e hioides";
        if ("POWELL".equals(mode)) return "Perfil facial";
        if ("TWEED".equals(mode)) return "Triángulo dentofacial";
        if ("LEVANDOSKI".equals(mode)) return "Simetría panorámica";
        if ("AIRWAY".equals(mode)) return "Vía aérea superior";
        return "Análisis cefalométrico";
    }
'''
if old_titles in text:
    text = text.replace(old_titles, new_titles, 1)

# Point help card: tapping it opens the complete, non-truncated description.
listener_anchor = '''        pointChips = findViewById(R.id.pointChips);

        polishStaticTextAlignment();
'''
listener_replacement = '''        pointChips = findViewById(R.id.pointChips);

        if (txtInstruction != null) {
            txtInstruction.setClickable(true);
            txtInstruction.setFocusable(true);
            txtInstruction.setOnClickListener(v -> showFullPointDescription());
        }

        View btnFineAdjust = findViewById(R.id.btnFineAdjust);
        if (btnFineAdjust != null) {
            btnFineAdjust.setOnClickListener(v -> showFineAdjustDialog());
        }

        polishStaticTextAlignment();
'''
if listener_anchor in text:
    text = text.replace(listener_anchor, listener_replacement, 1)

old_hint = '''        txtInstruction.setText(
                "Un dedo: coloca y arrastra el punto con precisión fina. Dos dedos: mueve o amplía la radiografía."
        );
'''
new_hint = '''        txtInstruction.setText(
                "Toque y suelte: colocar. Mantenga sobre un punto: moverlo. Dos dedos: desplazar. Pellizco: zoom. Toque esta ayuda para verla completa."
        );
'''
if old_hint in text:
    text = text.replace(old_hint, new_hint, 1)

# Add precision-control button to centered-text pass.
text = text.replace(
    '''                R.id.btnFit,\n                R.id.btnSaveStudy,''',
    '''                R.id.btnFit,\n                R.id.btnFineAdjust,\n                R.id.btnSaveStudy,'''
)

# Full-description dialog + joystick-like precision pad.
method_anchor = '''    private void polishStaticTextAlignment() {
'''
if 'private void showFullPointDescription()' not in text and method_anchor in text:
    helper_methods = '''    private void showFullPointDescription() {
        if (measurementView == null) return;

        String label = measurementView.getCurrentLabel();
        if (label == null || label.trim().isEmpty()) {
            Toast.makeText(this, "Seleccione primero un punto.", Toast.LENGTH_SHORT).show();
            return;
        }

        new AlertDialog.Builder(this)
                .setTitle(label)
                .setMessage(PointGuide.description(label))
                .setPositiveButton("Cerrar", null)
                .show();
    }

    private void showFineAdjustDialog() {
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

        LinearLayout pad = new LinearLayout(this);
        pad.setOrientation(LinearLayout.VERTICAL);
        pad.setGravity(Gravity.CENTER);
        pad.setPadding(dp(18), dp(10), dp(18), dp(10));

        TextView help = new TextView(this);
        help.setText("Ajuste fino del punto " + measurementView.getCurrentLabel() +
                "\\nToque una flecha para moverlo un paso pequeño. Mantenga una flecha para un paso mayor.");
        help.setTextSize(14f);
        help.setGravity(Gravity.CENTER);
        help.setTextAlignment(View.TEXT_ALIGNMENT_CENTER);
        help.setPadding(0, 0, 0, dp(10));
        pad.addView(help, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        ));

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
                key.setTextSize(r == 1 && c == 1 ? 16f : 24f);
                key.setGravity(Gravity.CENTER);
                key.setTextAlignment(View.TEXT_ALIGNMENT_CENTER);
                key.setIncludeFontPadding(false);

                LinearLayout.LayoutParams params =
                        new LinearLayout.LayoutParams(dp(62), dp(54));
                params.setMargins(dp(3), dp(3), dp(3), dp(3));
                key.setLayoutParams(params);

                if (r == 1 && c == 1) {
                    key.setAlpha(0.45f);
                    key.setClickable(false);
                } else {
                    final float stepX = dx[r][c];
                    final float stepY = dy[r][c];
                    key.setBackgroundResource(R.drawable.button_soft_purple_centered);
                    key.setOnClickListener(v -> measurementView.nudgeSelectedPoint(
                            stepX * dp(1.6f),
                            stepY * dp(1.6f)
                    ));
                    key.setOnLongClickListener(v -> {
                        measurementView.nudgeSelectedPoint(
                                stepX * dp(5f),
                                stepY * dp(5f)
                        );
                        return true;
                    });
                }

                row.addView(key);
            }

            pad.addView(row);
        }

        new AlertDialog.Builder(this)
                .setTitle("🎯 Ajuste fino")
                .setView(pad)
                .setPositiveButton("Cerrar", null)
                .show();
    }

'''
    text = text.replace(method_anchor, helper_methods + method_anchor, 1)

analysis.write_text(text, encoding='utf-8')

# -----------------------------------------------------------------------------
# Gesture redesign + smaller visible points
# -----------------------------------------------------------------------------
view = Path('app/src/main/java/com/cefalo/angulos/MeasurementView.java')
v = view.read_text(encoding='utf-8')

# No automatic advance after a point is placed.
auto_advance = '''                    if (editingPointWasMissing) {
                        int nextMissing =
                                nextMissingIndex(selectedIndex);

                        if (nextMissing >= 0) {
                            selectedIndex = nextMissing;
                        }
                    }

'''
if auto_advance in v:
    v = v.replace(auto_advance, '', 1)

if 'import android.view.ViewConfiguration;' not in v:
    v = v.replace(
            'import android.view.View;\n',
            'import android.view.View;\nimport android.view.ViewConfiguration;\n'
    )

field_anchor = '''    private static final float FINE_DRAG_FACTOR = 0.34f;
'''
if 'POINT_HIT_RADIUS_DP' not in v and field_anchor in v:
    v = v.replace(
            field_anchor,
            field_anchor +
            '''    private static final float TAP_SLOP_DP = 7f;\n''' +
            '''    private static final float POINT_HIT_RADIUS_DP = 24f;\n''' +
            '''    private int pressedPointIndex = -1;\n''',
            1
    )

# Much smaller visible point, while touch target remains generous and invisible.
old_points = '''            canvas.drawCircle(s.x, s.y, dp(12), haloPaint);
            canvas.drawCircle(
                    s.x,
                    s.y,
                    dp(i == selectedIndex ? 9 : 8),
                    i == selectedIndex ? selectedPointPaint : pointPaint
            );

            if (isPointLocked(i)) {
                canvas.drawCircle(s.x, s.y, dp(16), lockedRingPaint);
            }

            if (i == selectedIndex) {
                canvas.drawCircle(s.x, s.y, dp(15), selectedRingPaint);
                canvas.drawLine(s.x - dp(20), s.y, s.x - dp(11), s.y, selectedRingPaint);
                canvas.drawLine(s.x + dp(11), s.y, s.x + dp(20), s.y, selectedRingPaint);
                canvas.drawLine(s.x, s.y - dp(20), s.x, s.y - dp(11), selectedRingPaint);
                canvas.drawLine(s.x, s.y + dp(11), s.x, s.y + dp(20), selectedRingPaint);
            }
'''
new_points = '''            // Visual marker intentionally small so it does not hide anatomy.
            // The hit target is larger (POINT_HIT_RADIUS_DP) but remains invisible.
            canvas.drawCircle(s.x, s.y, dp(5.2f), haloPaint);
            canvas.drawCircle(
                    s.x,
                    s.y,
                    dp(i == selectedIndex ? 3.8f : 3.2f),
                    i == selectedIndex ? selectedPointPaint : pointPaint
            );

            if (isPointLocked(i)) {
                canvas.drawCircle(s.x, s.y, dp(7.2f), lockedRingPaint);
            }

            if (i == selectedIndex) {
                canvas.drawCircle(s.x, s.y, dp(7.5f), selectedRingPaint);
                canvas.drawLine(s.x - dp(11), s.y, s.x - dp(6), s.y, selectedRingPaint);
                canvas.drawLine(s.x + dp(6), s.y, s.x + dp(11), s.y, selectedRingPaint);
                canvas.drawLine(s.x, s.y - dp(11), s.x, s.y - dp(6), selectedRingPaint);
                canvas.drawLine(s.x, s.y + dp(6), s.x, s.y + dp(11), selectedRingPaint);
            }
'''
if old_points in v:
    v = v.replace(old_points, new_points, 1)

v = v.replace('textPaint.setTextSize(dp(14));', 'textPaint.setTextSize(dp(11));')
v = v.replace('float labelX = s.x + dp(12);', 'float labelX = s.x + dp(8);')
v = v.replace('float labelY = s.y - dp(10);', 'float labelY = s.y - dp(7);')
v = v.replace('s.x - textWidth - dp(12)', 's.x - textWidth - dp(8)')
v = v.replace('labelY = s.y + dp(24);', 'labelY = s.y + dp(16);')

# Add nudge API used by the precision pad.
nudge_anchor = '''    @Override
    public boolean onTouchEvent(MotionEvent event) {
'''
if 'public boolean nudgeSelectedPoint(' not in v and nudge_anchor in v:
    nudge_method = '''    public boolean nudgeSelectedPoint(float screenDx, float screenDy) {
        if (bitmap == null
                || locked
                || selectedIndex < 0
                || selectedIndex >= points.size()
                || isPointLocked(selectedIndex)) {
            return false;
        }

        PointF current = points.get(selectedIndex);
        if (current == null) return false;

        float scale = getCurrentMatrixScale();
        PointF adjusted = new PointF(
                clamp(current.x + screenDx / scale, 0f, bitmap.getWidth()),
                clamp(current.y + screenDy / scale, 0f, bitmap.getHeight())
        );

        points.set(selectedIndex, adjusted);
        notifyProgress();
        invalidate();
        return true;
    }

    private int findPointNearScreen(float x, float y, float radiusPx) {
        int nearest = -1;
        float best = radiusPx;

        for (int i = 0; i < points.size(); i++) {
            PointF point = points.get(i);
            if (point == null) continue;

            PointF screen = imageToScreen(point);
            float distance = (float) Math.hypot(screen.x - x, screen.y - y);
            if (distance <= best) {
                best = distance;
                nearest = i;
            }
        }

        return nearest;
    }

'''
    v = v.replace(nudge_anchor, nudge_method + nudge_anchor, 1)

# Replace the one-finger interaction: tap-to-place; long-press existing point to edit;
# pan is reserved for two fingers, pinch remains handled by ScaleGestureDetector.
start_marker = '''    @Override
    public boolean onTouchEvent(MotionEvent event) {
'''
end_marker = '''    private void restoreEditingPoint() {
'''
start = v.find(start_marker)
end = v.find(end_marker, start) if start != -1 else -1
if start != -1 and end != -1:
    new_touch = '''    @Override
    public boolean onTouchEvent(MotionEvent event) {
        if (bitmap == null || landmarkLabels.isEmpty()) return true;

        scaleDetector.onTouchEvent(event);

        if (calibrationMode) {
            return handleCalibrationTouch(event);
        }

        if (event.getPointerCount() >= 2) {
            if (editingPoint) {
                restoreEditingPoint();
                editingPoint = false;
            }

            moved = true;
            pressedPointIndex = -1;
            magnifierActive = false;
            handleTwoFingerPan(event);
            return true;
        } else {
            twoFingerTracking = false;
        }

        switch (event.getActionMasked()) {
            case MotionEvent.ACTION_DOWN: {
                downX = event.getX();
                downY = event.getY();
                lastFineTouchX = downX;
                lastFineTouchY = downY;
                moved = false;
                editingPoint = false;
                editingPointOriginal = null;
                editingPointWasMissing = false;

                PointF initial = screenToImage(downX, downY);
                pressedPointIndex = findPointNearScreen(
                        downX,
                        downY,
                        dp(POINT_HIT_RADIUS_DP)
                );

                // A tap near an existing landmark selects it but does not move it.
                if (pressedPointIndex >= 0) {
                    selectedIndex = pressedPointIndex;
                    notifyProgress();
                }

                if (insideImage(initial)) {
                    magnifierImagePoint = initial;
                    magnifierActive = true;
                }

                invalidate();
                return true;
            }

            case MotionEvent.ACTION_MOVE: {
                float x = event.getX();
                float y = event.getY();
                long heldMs = event.getEventTime() - event.getDownTime();

                // Long press over an existing point enters precision-edit mode.
                if (!editingPoint
                        && pressedPointIndex >= 0
                        && !locked
                        && !isPointLocked(pressedPointIndex)
                        && heldMs >= ViewConfiguration.getLongPressTimeout()) {

                    selectedIndex = pressedPointIndex;
                    PointF previous = points.get(selectedIndex);
                    if (previous != null) {
                        editingPointOriginal = new PointF(previous.x, previous.y);
                        editingPoint = true;
                        lastFineTouchX = x;
                        lastFineTouchY = y;
                        magnifierImagePoint = new PointF(previous.x, previous.y);
                        magnifierActive = true;
                    }
                }

                if (editingPoint) {
                    PointF current = points.get(selectedIndex);

                    if (current != null) {
                        float scale = getCurrentMatrixScale();
                        float dxImage =
                                (x - lastFineTouchX) / scale * FINE_DRAG_FACTOR;
                        float dyImage =
                                (y - lastFineTouchY) / scale * FINE_DRAG_FACTOR;

                        PointF adjusted = new PointF(
                                clamp(current.x + dxImage, 0f, bitmap.getWidth()),
                                clamp(current.y + dyImage, 0f, bitmap.getHeight())
                        );

                        points.set(selectedIndex, adjusted);
                        magnifierImagePoint = new PointF(adjusted.x, adjusted.y);
                        magnifierActive = true;
                    }

                    autoPanNearEdges(x, y);
                    lastFineTouchX = x;
                    lastFineTouchY = y;
                    invalidate();
                    return true;
                }

                if (Math.hypot(x - downX, y - downY) > dp(TAP_SLOP_DP)) {
                    moved = true;
                }

                // One finger never pans the radiograph. It only shows the loupe while
                // preparing a tap or a long-press edit. Pan requires two fingers.
                PointF movePoint = screenToImage(x, y);
                if (insideImage(movePoint)) {
                    magnifierImagePoint = movePoint;
                    magnifierActive = true;
                }

                invalidate();
                return true;
            }

            case MotionEvent.ACTION_UP: {
                if (editingPoint) {
                    performClick();
                    editingPoint = false;
                    editingPointOriginal = null;
                    editingPointWasMissing = false;
                    pressedPointIndex = -1;
                    magnifierActive = false;
                    notifyProgress();
                    invalidate();
                    return true;
                }

                PointF upPoint = screenToImage(event.getX(), event.getY());

                if (!moved && insideImage(upPoint)) {
                    performClick();

                    if (pressedPointIndex >= 0) {
                        // Selecting an existing point must not relocate it.
                        selectedIndex = pressedPointIndex;
                        notifyProgress();
                    } else if (!locked
                            && selectedIndex >= 0
                            && selectedIndex < points.size()
                            && !isPointLocked(selectedIndex)) {
                        // Short tap + release places/replaces only the explicitly selected point.
                        points.set(selectedIndex, new PointF(upPoint.x, upPoint.y));
                        notifyProgress();
                    }
                }

                pressedPointIndex = -1;
                magnifierActive = false;
                invalidate();
                return true;
            }

            case MotionEvent.ACTION_CANCEL:
                if (editingPoint) {
                    restoreEditingPoint();
                    editingPoint = false;
                    editingPointOriginal = null;
                    editingPointWasMissing = false;
                }

                pressedPointIndex = -1;
                magnifierActive = false;
                invalidate();
                return true;
        }

        return true;
    }

'''
    v = v[:start] + new_touch + v[end:]

# Smaller points in exported annotated images too.
v = v.replace(
        'float outerRadius = Math.max(9f, 13f * exportScale);',
        'float outerRadius = Math.max(4f, 6f * exportScale);'
)
v = v.replace(
        'float innerRadius = Math.max(6f, 9f * exportScale);',
        'float innerRadius = Math.max(2.5f, 4f * exportScale);'
)
v = v.replace(
        'float labelOffset = Math.max(11f, 15f * exportScale);',
        'float labelOffset = Math.max(7f, 10f * exportScale);'
)

view.write_text(v, encoding='utf-8')

# -----------------------------------------------------------------------------
# Point-guide corrections for tangent constructions
# -----------------------------------------------------------------------------
guide = Path('app/src/main/java/com/cefalo/angulos/PointGuide.java')
g = guide.read_text(encoding='utf-8')

replacements = {
    'GUIDE.put("CV2tg", "CV2tg: punto de tangencia en el extremo superoposterior del proceso odontoideo de C2. Es el punto superior común de las líneas OPT y CVT en la nomenclatura de Solow/Tallgren.");':
    'GUIDE.put("CV2tg", "CV2tg: landmark de tangencia sobre el contorno dorsal del extremo superoposterior de la odontoides de C2. CV2tg es un punto, no una línea. Para construir OPT se necesitan 2 puntos: CV2tg + CV2ip. Para construir CVT, en el protocolo Solow/Tallgren adoptado por la app, se necesitan 2 puntos: CV2tg + CV4ip.");',

    'GUIDE.put("CV2ip", "CV2ip: punto más inferior y posterior del cuerpo de C2. Junto con CV2tg forma la línea OPT.");':
    'GUIDE.put("CV2ip", "CV2ip: punto más inferoposterior del cuerpo de C2. Es el segundo landmark de OPT: marque CV2tg + CV2ip para formar la tangente del proceso odontoideo.");',

    'GUIDE.put("CV4ip", "CV4ip: punto más inferior y posterior del cuerpo de C4. Junto con CV2tg forma la línea CVT; también puede servir como punto superior de la línea EVT.");':
    'GUIDE.put("CV4ip", "CV4ip: punto más inferoposterior del cuerpo de C4. Es el segundo landmark de CVT (CV2tg + CV4ip) y el primer landmark de EVT (CV4ip + CV6ip). Por eso CV4ip se comparte al calcular el ángulo CVT/EVT.");',

    'GUIDE.put("CV6ip", "CV6ip: punto más inferior y posterior del cuerpo de C6. Junto con CV4ip forma la línea EVT para describir la curvatura cervical inferior.");':
    'GUIDE.put("CV6ip", "CV6ip: punto más inferoposterior del cuerpo de C6. Es el segundo landmark de EVT: marque CV4ip + CV6ip para formar la línea cervical inferior.");',

    'GUIDE.put("C2 post-sup.", "C2 posterosuperior para Penning: punto del margen posterosuperior del proceso odontoideo de C2 desde el que se traza la tangente posterior hacia C7.");':
    'GUIDE.put("C2 post-sup.", "C2 posterosuperior para Penning: landmark superior de la línea de referencia posterior. La tangente de Penning se construye con 2 puntos: C2 post-sup. + C7 post-inf.; después se mide perpendicularmente la profundidad a nivel cervical medio.");',

    'GUIDE.put("C7 post-inf.", "C7 posteroinferior para Penning: punto más posterior e inferior del cuerpo de C7; es el extremo inferior de la tangente usada para valorar la profundidad cervical.");':
    'GUIDE.put("C7 post-inf.", "C7 posteroinferior para Penning: landmark inferior de la tangente posterior C2-C7. Debe marcarse junto con C2 post-sup.; ambos puntos forman la línea sobre la que se calcula la profundidad cervical.");'
}
for old_text, new_text in replacements.items():
    if old_text in g:
        g = g.replace(old_text, new_text, 1)

# SL / SE guide additions retained for older source snapshots.
anchor = '        GUIDE.put("Gn", "Gnathion (Gn):'
idx = g.find(anchor)
if idx != -1 and 'GUIDE.put("Pg"' not in g:
    line_end = g.find('\n', idx)
    extra = '''\n        GUIDE.put("Pg", "Pogonion (Pg): punto más anterior del contorno óseo de la sínfisis mandibular. Para SL, el software proyecta Pg perpendicularmente sobre SN para construir L.");\n        GUIDE.put("Cóndilo posterior", "Contorno posterior del cóndilo: marque el punto más posterior de la cabeza condilar mandibular visible. Para SE, el software lo proyecta perpendicularmente sobre SN para construir E.");'''
    g = g[:line_end] + extra + g[line_end:]

guide.write_text(g, encoding='utf-8')

# -----------------------------------------------------------------------------
# Layout: clickable description card + precision-adjust button
# -----------------------------------------------------------------------------
layout = Path('app/src/main/res/layout/activity_analysis.xml')
x = layout.read_text(encoding='utf-8')

instruction_old = '''        android:maxLines="2"
        android:ellipsize="end"
        android:paddingLeft="10dp"'''
instruction_new = '''        android:maxLines="2"
        android:ellipsize="end"
        android:clickable="true"
        android:focusable="true"
        android:contentDescription="Toca para abrir la descripción completa del punto"
        android:paddingLeft="10dp"'''
if instruction_old in x:
    x = x.replace(instruction_old, instruction_new, 1)

fine_button_anchor = '''            <TextView
                android:id="@+id/btnSaveStudy"'''
if '@+id/btnFineAdjust' not in x and fine_button_anchor in x:
    fine_button = '''            <TextView
                android:id="@+id/btnFineAdjust"
                android:layout_width="104dp"
                android:layout_height="48dp"
                android:gravity="center"
                android:textAlignment="center"
                android:includeFontPadding="false"
                android:text="🎯 AJUSTE FINO"
                android:textStyle="bold"
                android:textSize="9.5sp"
                android:textColor="@color/brand_purple"
                android:background="@drawable/button_soft_purple_centered"
                android:clickable="true"
                android:focusable="true"
                android:layout_marginRight="4dp" />

'''
    x = x.replace(fine_button_anchor, fine_button + fine_button_anchor, 1)

layout.write_text(x, encoding='utf-8')

print('Test-build clinical, tangent, gesture and precision-control patches applied.')
