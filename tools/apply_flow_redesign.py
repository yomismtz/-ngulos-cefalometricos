from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def write(rel, text):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_once(text, old, new, label):
    if old not in text:
        raise RuntimeError(f"Missing replacement target: {label}")
    if text.count(old) != 1:
        raise RuntimeError(f"Expected one target for {label}, found {text.count(old)}")
    return text.replace(old, new, 1)


def replace_between(text, start, end, replacement, label):
    a = text.find(start)
    if a < 0:
        raise RuntimeError(f"Missing start marker: {label}")
    b = text.find(end, a)
    if b < 0:
        raise RuntimeError(f"Missing end marker: {label}")
    return text[:a] + replacement + text[b:]


# -----------------------------------------------------------------------------
# MeasurementView: tap to place, one-finger pan, pinch zoom, long-press to edit.
# ----------------------------------------------------------------------------
view_path = "app/src/main/java/com/cefalo/angulos/MeasurementView.java"
text = read(view_path)
text = replace_once(
    text,
    "import android.view.ScaleGestureDetector;\nimport android.view.View;",
    "import android.view.ScaleGestureDetector;\nimport android.view.View;\nimport android.view.ViewConfiguration;",
    "MeasurementView ViewConfiguration import",
)

old_undo = '''    public void undo() {
        if (locked || points.isEmpty()) return;

        int start = selectedIndex - 1;
        if (start < 0) start = points.size() - 1;

        int found = -1;
        for (int step = 0; step < points.size(); step++) {
            int i = (start - step + points.size()) % points.size();
            if (points.get(i) != null && !isPointLocked(i)) {
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
'''
new_undo = '''    public void undo() {
        if (locked || points.isEmpty()) return;

        // With explicit landmark selection, undo the selected landmark first.
        // If it has not been placed, fall back to the previous editable point.
        int found = -1;
        if (selectedIndex >= 0
                && selectedIndex < points.size()
                && points.get(selectedIndex) != null
                && !isPointLocked(selectedIndex)) {
            found = selectedIndex;
        } else {
            int start = selectedIndex - 1;
            if (start < 0) start = points.size() - 1;

            for (int step = 0; step < points.size(); step++) {
                int i = (start - step + points.size()) % points.size();
                if (points.get(i) != null && !isPointLocked(i)) {
                    found = i;
                    break;
                }
            }
        }

        if (found >= 0) {
            points.set(found, null);
            pointLocks.set(found, false);
            selectedIndex = found;
        }

        notifyProgress();
        invalidate();
    }
'''
text = replace_once(text, old_undo, new_undo, "MeasurementView undo")

new_touch = r'''    @Override
    public boolean onTouchEvent(MotionEvent event) {
        if (bitmap == null || landmarkLabels.isEmpty()) return true;

        scaleDetector.onTouchEvent(event);

        if (calibrationMode) {
            return handleCalibrationTouch(event);
        }

        if (event.getPointerCount() >= 2) {
            cancelLongPress();

            if (editingPoint) {
                restoreEditingPoint();
                editingPoint = false;
            }

            moved = true;
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
                lastPanX = downX;
                lastPanY = downY;
                lastFineTouchX = downX;
                lastFineTouchY = downY;
                moved = false;
                editingPoint = false;
                editingPointOriginal = null;
                editingPointWasMissing = false;
                magnifierActive = false;

                scheduleLongPressForSelectedPoint();
                invalidate();
                return true;

            case MotionEvent.ACTION_MOVE:
                float x = event.getX();
                float y = event.getY();

                if (editingPoint) {
                    PointF current = points.get(selectedIndex);

                    if (current != null) {
                        float scale = getCurrentMatrixScale();
                        float dxImage =
                                (x - lastFineTouchX)
                                        / scale
                                        * FINE_DRAG_FACTOR;
                        float dyImage =
                                (y - lastFineTouchY)
                                        / scale
                                        * FINE_DRAG_FACTOR;

                        PointF adjusted =
                                new PointF(
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

                if (Math.hypot(x - downX, y - downY) > dp(7)) {
                    moved = true;
                    cancelLongPress();
                }

                if (moved && !scaleDetector.isInProgress()) {
                    matrix.postTranslate(x - lastPanX, y - lastPanY);
                    constrainImageToViewport();
                    updateInverse();
                    magnifierActive = false;
                }

                lastPanX = x;
                lastPanY = y;
                invalidate();
                return true;

            case MotionEvent.ACTION_UP:
                cancelLongPress();

                if (editingPoint) {
                    performClick();
                    editingPoint = false;
                    editingPointOriginal = null;
                    editingPointWasMissing = false;
                    magnifierActive = false;
                    notifyProgress();
                    invalidate();
                    return true;
                }

                PointF upPoint = screenToImage(event.getX(), event.getY());

                // A short tap places only a missing selected landmark. Once a
                // point exists, moving it requires a long press on that point.
                if (!moved
                        && !locked
                        && insideImage(upPoint)
                        && selectedIndex >= 0
                        && selectedIndex < points.size()
                        && points.get(selectedIndex) == null
                        && !isPointLocked(selectedIndex)) {
                    performClick();
                    points.set(selectedIndex, new PointF(upPoint.x, upPoint.y));
                    notifyProgress();
                }

                // Deliberately keep selectedIndex unchanged: the operator must
                // explicitly choose the next landmark chip/button.
                magnifierActive = false;
                invalidate();
                return true;

            case MotionEvent.ACTION_CANCEL:
                cancelLongPress();
                if (editingPoint) {
                    restoreEditingPoint();
                    editingPoint = false;
                    editingPointOriginal = null;
                    editingPointWasMissing = false;
                }
                magnifierActive = false;
                invalidate();
                return true;
        }

        return true;
    }

    private void scheduleLongPressForSelectedPoint() {
        cancelLongPress();

        if (locked
                || selectedIndex < 0
                || selectedIndex >= points.size()
                || points.get(selectedIndex) == null
                || isPointLocked(selectedIndex)) {
            return;
        }

        PointF selected = points.get(selectedIndex);
        PointF selectedScreen = imageToScreen(selected);

        if (Math.hypot(selectedScreen.x - downX, selectedScreen.y - downY) > dp(38)) {
            return;
        }

        final int targetIndex = selectedIndex;
        longPressRunnable = () -> {
            if (moved
                    || locked
                    || targetIndex != selectedIndex
                    || targetIndex < 0
                    || targetIndex >= points.size()
                    || points.get(targetIndex) == null
                    || isPointLocked(targetIndex)) {
                return;
            }

            PointF current = points.get(targetIndex);
            editingPoint = true;
            editingPointWasMissing = false;
            editingPointOriginal = new PointF(current.x, current.y);
            lastFineTouchX = downX;
            lastFineTouchY = downY;
            magnifierImagePoint = new PointF(current.x, current.y);
            magnifierActive = true;
            invalidate();
        };

        postDelayed(longPressRunnable, ViewConfiguration.getLongPressTimeout());
    }

    private void cancelLongPress() {
        if (longPressRunnable != null) {
            removeCallbacks(longPressRunnable);
            longPressRunnable = null;
        }
    }

'''
text = replace_between(
    text,
    "    @Override\n    public boolean onTouchEvent(MotionEvent event) {",
    "    private void restoreEditingPoint() {",
    new_touch,
    "MeasurementView touch behavior",
)

# Add the Runnable field near touch state.
text = replace_once(
    text,
    "    private float lastFineTouchX;\n    private float lastFineTouchY;\n    private static final float FINE_DRAG_FACTOR = 0.34f;",
    "    private float lastFineTouchX;\n    private float lastFineTouchY;\n    private Runnable longPressRunnable;\n    private static final float FINE_DRAG_FACTOR = 0.34f;",
    "MeasurementView long press field",
)
write(view_path, text)


# -----------------------------------------------------------------------------
# PointGuide: reproducible definitions for every landmark currently used.
# -----------------------------------------------------------------------------
point_guide = r'''package com.cefalo.angulos;

import java.util.HashMap;
import java.util.Map;

/**
 * Landmark placement guide. Definitions are intentionally operational: they
 * describe a reproducible radiographic location rather than a diagnosis.
 */
public final class PointGuide {
    private static final Map<String, String> GUIDE = new HashMap<>();

    static {
        // Craniofacial hard-tissue landmarks.
        GUIDE.put("S", "Sella (S): centro geométrico de la fosa hipofisaria/silla turca.");
        GUIDE.put("N", "Nasion (N): punto más anterior de la sutura frontonasal en el plano medio.");
        GUIDE.put("A", "Punto A (subespinal): punto más profundo de la concavidad anterior del maxilar entre la espina nasal anterior y el reborde alveolar del incisivo superior.");
        GUIDE.put("B", "Punto B (supramental): punto más profundo de la concavidad anterior de la sínfisis mandibular entre el reborde alveolar inferior y el pogonion óseo.");
        GUIDE.put("D", "Punto D de Steiner: centro geométrico del cuerpo de la sínfisis mandibular; úselo como referencia interna de la sínfisis, no como punto del contorno.");
        GUIDE.put("Po", "Porion (Po): punto más superior del contorno radiográfico del conducto auditivo externo utilizado para construir el plano de Frankfort.");
        GUIDE.put("Or", "Orbitale (Or): punto más inferior del reborde orbitario.");
        GUIDE.put("ENA", "Espina nasal anterior (ENA/ANS): extremo más anterior de la espina nasal anterior.");
        GUIDE.put("ENP", "Espina nasal posterior (ENP/PNS): extremo más posterior del paladar duro, en la espina nasal posterior.");
        GUIDE.put("Ba", "Basion (Ba): punto medio del borde anterior del foramen magno, sobre la línea media; seleccione el punto más inferior de ese borde visible en la telerradiografía.");
        GUIDE.put("Ar", "Articulare (Ar): punto construido en la intersección del borde posterior de la rama mandibular con el contorno inferior de la base craneal.");
        GUIDE.put("Go", "Gonion (Go): punto construido sobre el ángulo mandibular, en la bisectriz entre la tangente al borde posterior de la rama y la tangente al borde inferior del cuerpo mandibular.");
        GUIDE.put("Me", "Menton (Me): punto más inferior del contorno de la sínfisis mandibular.");
        GUIDE.put("Gn", "Gnathion (Gn): punto construido a mitad del arco entre Pogonion y Menton; corresponde a la región más anteroinferior de la sínfisis.");

        // Dental landmarks and Steiner occlusal plane.
        GUIDE.put("IS borde", "Incisivo superior, borde: centro del borde incisal del incisivo central superior que se está trazando.");
        GUIDE.put("IS ápice", "Incisivo superior, ápice: ápice radicular del mismo incisivo central superior usado para el borde incisal; ambos puntos forman su eje largo.");
        GUIDE.put("II borde", "Incisivo inferior, borde: centro del borde incisal del incisivo central inferior que se está trazando.");
        GUIDE.put("II ápice", "Incisivo inferior, ápice: ápice radicular del mismo incisivo central inferior; junto con el borde incisal forma su eje largo.");
        GUIDE.put("Oclusal 1", "Plano oclusal de Steiner, punto anterior: punto equidistante entre los bordes incisales superior e inferior (bisecte el espacio entre ambos incisivos en oclusión).");
        GUIDE.put("Oclusal 2", "Plano oclusal de Steiner, punto posterior: punto medio de la zona de intercuspidación/superposición de los primeros molares. Únalo con el punto anterior para construir el plano oclusal.");

        // Solow/Siersbæk-Nielsen cervical tangents.
        GUIDE.put("Cv2tg", "Cv2tg: punto de tangencia sobre el contorno dorsal de la apófisis odontoides de C2. Es el punto superior común usado por las tangentes OPT y CVT.");
        GUIDE.put("Cv2ip", "Cv2ip: punto más posteroinferior del cuerpo de C2. Junto con Cv2tg define la tangente OPT.");
        GUIDE.put("Cv4ip", "Cv4ip: punto más posteroinferior del cuerpo de C4. Junto con Cv2tg define la tangente CVT.");
        // Aliases retained only so older saved studies still show a useful guide.
        GUIDE.put("CVT sup.", "Referencia cervical histórica de la app. Use preferentemente Cv2tg: punto de tangencia dorsal de la odontoides de C2.");
        GUIDE.put("CVT inf.", "Referencia cervical histórica de la app. Use preferentemente Cv4ip: punto más posteroinferior del cuerpo de C4.");
        GUIDE.put("OPT sup.", "Referencia cervical histórica de la app. Use preferentemente Cv2tg: punto de tangencia dorsal de la odontoides de C2.");
        GUIDE.put("OPT inf.", "Referencia cervical histórica de la app. Use preferentemente Cv2ip: punto más posteroinferior del cuerpo de C2.");

        // Rocabado / hyoid triangle.
        GUIDE.put("Occipital", "C0 / referencia occipital de McGregor: punto del borde inferior del occipital usado como extremo posterior de la línea de McGregor; únalo con ENP.");
        GUIDE.put("C1 posterior", "C1 posterior: punto del arco posterior del atlas enfrentado al borde inferior del occipital para medir el espacio C0–C1.");
        GUIDE.put("Odontoides ápice", "Ápice de la odontoides: punto más superior del proceso odontoideo de C2.");
        GUIDE.put("C2 anteroinf.", "C2 anteroinferior: ángulo más anteroinferior del cuerpo del axis (C2); con el ápice odontoideo define la referencia odontoidea usada por el módulo Rocabado.");
        GUIDE.put("C3", "C3: ángulo más anteroinferior del cuerpo de la tercera vértebra cervical.");
        GUIDE.put("RGn", "RGn (retrognathion): punto más posteroinferior de la sínfisis mandibular.");
        GUIDE.put("H", "Hyoidale (H): punto más superior y anterior del cuerpo del hueso hioides.");
        GUIDE.put("AA", "AA: punto más anterior del cuerpo/arco anterior del atlas (C1) visible en la telerradiografía.");
        GUIDE.put("C2 post-sup.", "C2 posterosuperior: referencia posterosuperior de la odontoides/C2 utilizada como extremo superior de la tangente posterior C2–C7 para valorar profundidad cervical.");
        GUIDE.put("C7 post-inf.", "C7 posteroinferior: punto más posteroinferior del cuerpo de C7; constituye el extremo inferior de la tangente posterior C2–C7.");
        GUIDE.put("Profundidad cervical", "Profundidad cervical: punto de máxima concavidad posterior de la columna cervical, aproximadamente a nivel de C4; la app mide su distancia perpendicular a la tangente C2–C7.");

        // Powell soft tissue profile.
        GUIDE.put("G'", "Glabela de tejidos blandos (G'): punto más prominente de la frente en el perfil blando.");
        GUIDE.put("N'", "Nasion de tejidos blandos (N'): punto de mayor concavidad en la raíz nasal del perfil blando.");
        GUIDE.put("Pr", "Pronasale (Pr): punto más anterior y prominente de la punta de la nariz.");
        GUIDE.put("Pg'", "Pogonion de tejidos blandos (Pg'): punto más anterior del contorno blando del mentón.");
        GUIDE.put("Me'", "Menton de tejidos blandos (Me'): punto más inferior del contorno blando del mentón.");
        GUIDE.put("C", "Punto cervical (C): punto más profundo de la concavidad entre la región submandibular y el cuello.");

        // Adenoid / airway landmarks. Adopted convention: PNS/ENP as anterior anchor.
        GUIDE.put("AD1", "AD1: punto del tejido adenoideo/pared faríngea posterior que intersecta la línea ENP–Ba. Para PNS–AD1 seleccione el punto más cercano a ENP sobre esa misma línea.");
        GUIDE.put("AD2", "AD2: punto del tejido adenoideo/pared faríngea posterior intersectado por una línea que pasa por ENP y es perpendicular a S–Ba. Seleccione el punto más cercano a ENP sobre esa perpendicular.");
        GUIDE.put("Faringe sup ant.", "Faringe superior anterior de McNamara: punto en el contorno posterior del paladar blando desde el que se obtiene la distancia mínima hacia la pared faríngea posterior.");
        GUIDE.put("Faringe sup post.", "Faringe superior posterior de McNamara: punto de la pared faríngea posterior más cercano al punto anterior del paladar blando; la medida debe ser la distancia mínima.");
        GUIDE.put("Faringe inf ant.", "Faringe inferior anterior de McNamara: punto donde el contorno posterior de la lengua cruza el borde inferior de la mandíbula.");
        GUIDE.put("Faringe inf post.", "Faringe inferior posterior de McNamara: punto más cercano de la pared faríngea posterior al punto anterior inferior; mida la distancia mínima.");

        // Levandoski panoramic analysis.
        GUIDE.put("LM sup.", "Levandoski, línea 1: marque un punto superior sobre la línea media vertical maxilar que atraviesa el septum nasal. No use una desviación mandibular para definir esta línea.");
        GUIDE.put("LM inf.", "Levandoski, línea 1: marque un segundo punto, bien separado del primero, sobre la misma línea media vertical maxilar/septal para construir la línea 1.");
        GUIDE.put("LM mandibular", "Línea media mandibular: punto medio de la sínfisis mandibular; puede compararse visualmente con la línea media maxilar, pero no redefine la línea 1 de Levandoski.");
        GUIDE.put("Cd der.", "Condylion derecho (Cd): punto más superior de la cabeza condilar derecha en la panorámica.");
        GUIDE.put("Cd izq.", "Condylion izquierdo (Cd): punto más superior de la cabeza condilar izquierda en la panorámica.");
        GUIDE.put("Go der.", "Gonion derecho (Go): punto del ángulo mandibular derecho definido de forma equivalente al lado contralateral.");
        GUIDE.put("Go izq.", "Gonion izquierdo (Go): punto del ángulo mandibular izquierdo definido de forma equivalente al lado contralateral.");
        GUIDE.put("Kr der.", "Koronion derecho (Kr/Cor): punto más superior de la punta de la apófisis coronoides derecha.");
        GUIDE.put("Kr izq.", "Koronion izquierdo (Kr/Cor): punto más superior de la punta de la apófisis coronoides izquierda.");
        GUIDE.put("IC max der.", "Incisivo central maxilar derecho: centro del borde incisal del incisivo central derecho, usando el mismo criterio en ambos lados.");
        GUIDE.put("IC max izq.", "Incisivo central maxilar izquierdo: centro del borde incisal del incisivo central izquierdo, usando el mismo criterio en ambos lados.");
        GUIDE.put("IC mand der.", "Incisivo central mandibular derecho: centro del borde incisal del incisivo central derecho, usando el mismo criterio en ambos lados.");
        GUIDE.put("IC mand izq.", "Incisivo central mandibular izquierdo: centro del borde incisal del incisivo central izquierdo, usando el mismo criterio en ambos lados.");
        GUIDE.put("Cuerpo Md der.", "Cuerpo mandibular derecho: seleccione el mismo punto anatómico reproducible del borde corporal que usará en el lado izquierdo y a una altura comparable; esta es una comparación derecha/izquierda.");
        GUIDE.put("Cuerpo Md izq.", "Cuerpo mandibular izquierdo: seleccione el punto homólogo al marcado en el lado derecho y a una altura comparable; esta es una comparación derecha/izquierda.");
        GUIDE.put("M2 distal der.", "Segundo molar derecho: punto más distal de la corona del segundo molar usado para la comparación con la línea media.");
        GUIDE.put("M2 distal izq.", "Segundo molar izquierdo: punto más distal de la corona del segundo molar usado para la comparación con la línea media.");
        GUIDE.put("Rama ant der.", "Rama derecha, borde anterior: punto del borde anterior elegido al mismo nivel vertical que el punto posterior para medir el ancho de la rama.");
        GUIDE.put("Rama post der.", "Rama derecha, borde posterior: punto del borde posterior a la misma altura que el punto anterior.");
        GUIDE.put("Rama ant izq.", "Rama izquierda, borde anterior: punto homólogo al derecho y al mismo nivel vertical que el punto posterior.");
        GUIDE.put("Rama post izq.", "Rama izquierda, borde posterior: punto homólogo al derecho y a la misma altura que el punto anterior.");
    }

    private PointGuide() {}

    public static String description(String label) {
        String value = GUIDE.get(label);
        if (value != null) return value;
        return label + ": no hay una definición validada cargada para este rótulo. Revise la guía del análisis antes de marcarlo.";
    }
}
'''
write("app/src/main/java/com/cefalo/angulos/PointGuide.java", point_guide)


# -----------------------------------------------------------------------------
# Original, copyright-free schematic locator shown in the landmark help dialog.
# It is explicitly orientative and never used for measurement/calculation.
# -----------------------------------------------------------------------------
diagram = r'''package com.cefalo.angulos;

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
'''
write("app/src/main/java/com/cefalo/angulos/LandmarkDiagramView.java", diagram)


# -----------------------------------------------------------------------------
# Measurement catalogs: shared cervical points, remove unsupported AD3 and the
# vague McGregor-C4 construction, clarify airway angle nomenclature.
# -----------------------------------------------------------------------------
cat_path = "app/src/main/java/com/cefalo/angulos/MeasurementCatalog.java"
text = read(cat_path)
text = text.replace('p("S","N","CVT sup.","CVT inf.")', 'p("S","N","Cv2tg","Cv4ip")')
text = text.replace(
    '"Marque S-N y luego dos puntos de la tangente cervical CVT."',
    '"Marque S-N; después Cv2tg y Cv4ip para construir la tangente CVT."'
)
text = text.replace('p("S","N","OPT sup.","OPT inf.")', 'p("S","N","Cv2tg","Cv2ip")')
text = text.replace(
    '"Marque S-N y luego dos puntos de la tangente del proceso odontoideo OPT."',
    '"Marque S-N; después Cv2tg y Cv2ip para construir la tangente OPT."'
)
# Remove the non-reproducible McGregor-C4 block while keeping the Rocabado API.
text = re.sub(
    r'\n        list\.add\(m\(\n                "McGregor–C4",.*?\n        \)\);\n',
    '\n',
    text,
    count=1,
    flags=re.S,
)
text = text.replace('"Ba-S-NA",', '"Ba-S-N",')
text = text.replace(
    '"Tabla docente aportada: 126° · sin umbral diagnóstico automático",',
    '"Ángulo de base craneal · referencia descriptiva, sin umbral diagnóstico automático",'
)
text = text.replace(
    '"Tabla docente aportada: 63° · sin umbral diagnóstico automático",',
    '"Medida estructural · referencia descriptiva, sin umbral diagnóstico automático",'
)
text = text.replace(
    '"Medida estructural cefalométrica. No se encontró evidencia suficiente para convertir 63° en un umbral diagnóstico de vía aérea adecuada/inadecuada; se muestra solo como referencia docente.",',
    '"Medida estructural cefalométrica. No se usa un valor aislado como umbral diagnóstico de vía aérea adecuada o inadecuada.",'
)
write(cat_path, text)

lin_path = "app/src/main/java/com/cefalo/angulos/LinearMeasurementCatalog.java"
text = read(lin_path)
text = replace_once(
    text,
    '''        list.add(m("AD1 · ENP-AD1", DISTANCE, RANGE,
                p("ENP", "AD1"), Double.NaN, Double.NaN,
                "Referencia docente aportada para 6 y 16 años", "",
                "Se muestra como referencia tabular; no usar como diagnóstico de obstrucción/adenoides.", ""));

        list.add(m("AD2 · ENP-AD2", DISTANCE, RANGE,
                p("ENP", "AD2"), Double.NaN, Double.NaN,
                "Referencia docente aportada para 6 y 16 años", "",
                "Se muestra como referencia tabular; no usar como diagnóstico de obstrucción/adenoides.", ""));

        list.add(m("AD3 · Uptp-Adenoides", DISTANCE, RANGE,
                p("Uptp", "Adenoides"), Double.NaN, Double.NaN,
                "Tabla aportada: 6 a 7.02±3.70 · 16 a 14.56±4.70 mm", "",
                "Se muestra como referencia tabular; no usar como diagnóstico respiratorio.", ""));
''',
    '''        list.add(m("AD1 · ENP-AD1", DISTANCE, RANGE,
                p("ENP", "AD1"), Double.NaN, Double.NaN,
                "ENP–AD1 sobre la línea ENP–Ba · sin umbral diagnóstico automático", "",
                "Medida geométrica publicada; interpretar con edad y contexto clínico, no como diagnóstico de obstrucción/adenoides.", ""));

        list.add(m("AD2 · ENP-AD2", DISTANCE, RANGE,
                p("ENP", "AD2"), Double.NaN, Double.NaN,
                "ENP–AD2 sobre la perpendicular a S–Ba por ENP · sin umbral diagnóstico automático", "",
                "Medida geométrica publicada; interpretar con edad y contexto clínico, no como diagnóstico de obstrucción/adenoides.", ""));
''',
    "Linear airway AD1 AD2 AD3",
)
write(lin_path, text)


# -----------------------------------------------------------------------------
# AnalysisActivity: auto image prompt, partial analyses, separate exports,
# schematic guide, and remove references to a missing airway table.
# -----------------------------------------------------------------------------
act_path = "app/src/main/java/com/cefalo/angulos/AnalysisActivity.java"
text = read(act_path)

text = replace_once(
    text,
    '''        if (tracingFullscreen && btnTraceMode != null) {
            setTracingFullscreen(true);
        }
    }
''',
    '''        if (tracingFullscreen && btnTraceMode != null) {
            setTracingFullscreen(true);
        }

        // New-study flow: analysis -> image -> identification -> calibration -> points.
        if (savedInstanceState == null
                && restoredStudy == null
                && imageUriString == null) {
            measurementView.post(this::openImage);
        }
    }
''',
    "AnalysisActivity auto open image",
)

text = replace_once(
    text,
    '''        txtInstruction.setText(
                "Un dedo: coloca y arrastra el punto con precisión fina. Dos dedos: mueve o amplía la radiografía."
        );
''',
    '''        txtInstruction.setText(
                "Toque para colocar el punto seleccionado. Arrastre con un dedo para navegar; pellizque para zoom. Mantenga presionado un punto ya colocado para moverlo con lupa."
        );
''',
    "AnalysisActivity initial gesture hint",
)

old_guide_image = '''        ImageView image = new ImageView(this);
        image.setImageResource(
                R.drawable.tooth_ruler_mascot
        );
        image.setScaleType(
                ImageView.ScaleType.CENTER_INSIDE
        );

        box.addView(
                image,
                new LinearLayout.LayoutParams(
                        dp(96),
                        dp(74)
                )
        );
'''
new_guide_image = '''        LandmarkDiagramView diagram = new LandmarkDiagramView(this);
        diagram.setLandmark(label);
        box.addView(
                diagram,
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        dp(190)
                )
        );

        TextView diagramNotice = new TextView(this);
        diagramNotice.setText("Esquema orientativo y no a escala. Use la definición anatómica escrita para colocar el punto sobre la radiografía.");
        diagramNotice.setTextSize(11.5f);
        diagramNotice.setTextColor(getColor(R.color.text_secondary));
        diagramNotice.setGravity(Gravity.CENTER);
        diagramNotice.setTextAlignment(View.TEXT_ALIGNMENT_CENTER);
        diagramNotice.setPadding(0, dp(6), 0, dp(4));
        box.addView(diagramNotice);
'''
text = replace_once(text, old_guide_image, new_guide_image, "AnalysisActivity landmark diagram")

new_calculate = r'''    private void calculateFullAnalysis() {
        if (!measurementView.hasBitmap()) {
            Toast.makeText(
                    this,
                    "Primero abra una radiografía.",
                    Toast.LENGTH_SHORT
            ).show();
            return;
        }

        int available = countAvailableMeasurements();

        if (available == 0) {
            if (!linearDefinitions.isEmpty()
                    && definitions.isEmpty()
                    && (Double.isNaN(mmPerPixel) || mmPerPixel <= 0)) {
                Toast.makeText(
                        this,
                        "Este análisis necesita calibración para calcular medidas lineales.",
                        Toast.LENGTH_LONG
                ).show();
                startCalibrationFlow();
                return;
            }

            Toast.makeText(
                    this,
                    "Aún no hay suficientes puntos para formar una medida. Coloque los puntos de al menos un ángulo o distancia y vuelva a generar el análisis.",
                    Toast.LENGTH_LONG
            ).show();
            return;
        }

        if (!measurementView.isComplete()) {
            Toast.makeText(
                    this,
                    "Análisis parcial: se incluirán " + available +
                    (available == 1 ? " medida disponible." : " medidas disponibles.") +
                    " Las que aún no tengan todos sus puntos se omitirán.",
                    Toast.LENGTH_LONG
            ).show();
        }

        saveStudy(true);
        showResultsDialog();
    }

    private int countAvailableMeasurements() {
        int count = 0;

        for (MeasurementDefinition def : definitions) {
            if (measurementView.calculate(def) != null) {
                count++;
            }
        }

        if (!Double.isNaN(mmPerPixel) && mmPerPixel > 0) {
            for (LinearMeasurementDefinition def : linearDefinitions) {
                if (calculateLinear(def) != null) {
                    count++;
                }
            }
        }

        return count;
    }

'''
text = replace_between(
    text,
    "    private void calculateFullAnalysis() {",
    "    private void showResultsDialog() {",
    new_calculate,
    "AnalysisActivity partial calculation",
)

old_export = '''        TextView saveAnnotated =
                createDialogButton(
                        getString(R.string.export_annotated),
                        R.drawable.button_soft_mint,
                        getColor(R.color.mint_text)
                );

        saveAnnotated.setOnClickListener(v -> {
            Bitmap annotated =
                    measurementView
                            .renderAnnotatedBitmap(definitions, linearDefinitions);

            if (annotated == null) {
                Toast.makeText(
                        this,
                        "No se pudo preparar la imagen.",
                        Toast.LENGTH_SHORT
                ).show();

                return;
            }

            startSaveImage(
                    annotated,
                    safeFileName(
                            studyName +
                            "_puntos.png"
                    ),
                    REQ_SAVE_ANNOTATED
            );
        });

        container.addView(saveAnnotated);
'''
new_export = '''        TextView savePoints =
                createDialogButton(
                        getString(R.string.export_points),
                        R.drawable.button_soft_mint,
                        getColor(R.color.mint_text)
                );

        savePoints.setOnClickListener(v -> {
            Bitmap pointsOnly = measurementView.renderAnnotatedBitmap();

            if (pointsOnly == null) {
                Toast.makeText(this, "No se pudo preparar la imagen.", Toast.LENGTH_SHORT).show();
                return;
            }

            startSaveImage(
                    pointsOnly,
                    safeFileName(studyName + "_puntos.png"),
                    REQ_SAVE_ANNOTATED
            );
        });
        container.addView(savePoints);

        TextView saveTracing =
                createDialogButton(
                        getString(R.string.export_tracing),
                        R.drawable.button_soft_purple,
                        getColor(R.color.brand_purple)
                );

        saveTracing.setOnClickListener(v -> {
            Bitmap tracing = measurementView.renderAnnotatedBitmap(definitions, linearDefinitions);

            if (tracing == null) {
                Toast.makeText(this, "No se pudo preparar el trazado.", Toast.LENGTH_SHORT).show();
                return;
            }

            startSaveImage(
                    tracing,
                    safeFileName(studyName + "_trazado.png"),
                    REQ_SAVE_ANNOTATED
            );
        });
        container.addView(saveTracing);
'''
text = replace_once(text, old_export, new_export, "AnalysisActivity separate exports")

text = text.replace(
    'return "Interpretación cefalométrica orientativa. La telerradiografía lateral es una imagen 2D tomada despierto y no puede confirmar ni excluir obstrucción de vía aérea o apnea del sueño. Los valores se comparan con referencias publicadas o, cuando se indica, con la tabla docente aportada.";',
    'return "Interpretación cefalométrica orientativa. La telerradiografía lateral es una imagen 2D tomada despierto y no puede confirmar ni excluir obstrucción de vía aérea o apnea del sueño. AD1 y AD2 se presentan como medidas geométricas publicadas sin umbral diagnóstico automático.";'
)

new_airway_helpers = r'''    private String linearSectionTitle() {
        if ("VERTEBRAL".equals(mode)) return "Medidas lineales · Rocabado";
        if ("LEVANDOSKI".equals(mode)) return "Medidas lineales · Levandoski";
        if ("AIRWAY".equals(mode)) return "Medidas lineales · Vía aérea";
        return "Medidas lineales";
    }

    private String linearNormText(
            LinearMeasurementDefinition def,
            double value
    ) {
        if (!"AIRWAY".equals(mode)) {
            return def.normText;
        }

        if (def.name.startsWith("AD1") || def.name.startsWith("AD2")) {
            return def.normText;
        }

        AirwayRef ref = airwayReference(def.name);

        if (ref == null) {
            if (def.name.startsWith("Faringe superior")) {
                int age = patientAgeYears();

                if (age > 0 && age < 18) {
                    return "McNamara: ≤5 mm se describió como indicador de posible compromiso; la dimensión cambia con la edad";
                }

                return "McNamara adulto: mujeres 17.4±3.4 mm · hombres 17.4±4.3 mm; ≤5 mm = posible compromiso";
            }

            if (def.name.startsWith("Faringe posterior")) {
                return "McNamara adulto: mujeres 11.3±3.3 mm · hombres 13.5±4.3 mm; >15 mm puede asociarse con lengua anterior/tonsilas aumentadas";
            }

            return def.normText;
        }

        return String.format(
                Locale.US,
                "%.2f ± %.2f mm · referencia McNamara",
                ref.mean,
                ref.sd
        );
    }

    private String linearDiagnosis(
            LinearMeasurementDefinition def,
            double value
    ) {
        if (!"AIRWAY".equals(mode)) {
            return def.diagnosis(value);
        }

        if (def.name.startsWith("AD1") || def.name.startsWith("AD2")) {
            return "Medida geométrica obtenida. YomCeph no aplica un umbral automático a AD1/AD2 porque su dimensión depende de edad, población y protocolo; correlacione con la evaluación clínica.";
        }

        AirwayRef ref = airwayReference(def.name);

        if (def.name.startsWith("Faringe superior")) {
            if (value <= 5.0) {
                return "≤5 mm: McNamara lo describió únicamente como indicador de posible compromiso de vía aérea superior. Requiere valoración clínica/otorrinolaringológica; no es un diagnóstico.";
            }

            return "Mayor de 5 mm. Esta medida aislada no diagnostica normalidad respiratoria; una telerradiografía 2D tampoco confirma ni excluye apnea del sueño.";
        }

        if (def.name.startsWith("Faringe posterior")) {
            if (value > 15.0) {
                return ">15 mm: puede asociarse con posición anterior de la lengua y/o aumento tonsilar según la descripción de McNamara. Es una asociación cefalométrica, no un diagnóstico.";
            }

            return "≤15 mm. Una medida aislada en esta región no establece un diagnóstico respiratorio. Correlacionar clínicamente.";
        }

        if (ref == null) {
            return "Medida obtenida; no hay una referencia aplicable con los datos actuales. No se realiza clasificación diagnóstica.";
        }

        double min = ref.mean - ref.sd;
        double max = ref.mean + ref.sd;

        if (value >= min && value <= max) {
            return "Dentro de ±1 DE de la referencia disponible. Esto no descarta un trastorno respiratorio.";
        }

        return (value < min ? "Por debajo" : "Por encima") +
                " de ±1 DE de la referencia disponible. Una telerradiografía lateral 2D no establece un diagnóstico respiratorio.";
    }

    private int patientAgeYears() {
        try {
            int age = Integer.parseInt(patientAge.trim());
            return age >= 1 && age <= 120 ? age : -1;
        } catch (Exception e) {
            return -1;
        }
    }

    private AirwayRef airwayReference(String name) {
        int age = patientAgeYears();
        boolean female = "Femenino".equals(patientSex);
        boolean male = "Masculino".equals(patientSex);

        // Adult descriptive values from McNamara. Pediatric AD1/AD2 are not
        // assigned automatic thresholds in YomCeph.
        if (name.startsWith("Faringe superior")) {
            if (age < 18) return null;
            if (male) return new AirwayRef(17.4, 4.3);
            if (female) return new AirwayRef(17.4, 3.4);
            return null;
        }

        if (name.startsWith("Faringe posterior")) {
            if (age < 18) return null;
            if (male) return new AirwayRef(13.5, 4.3);
            if (female) return new AirwayRef(11.3, 3.3);
            return null;
        }

        return null;
    }

    private static class AirwayRef {
        final double mean;
        final double sd;

        AirwayRef(double mean, double sd) {
            this.mean = mean;
            this.sd = sd;
        }
    }

'''
text = replace_between(
    text,
    "    private boolean isProvidedAirwayTableReference(String name) {",
    "    private void addTweedSummary(LinearLayout container) {",
    new_airway_helpers,
    "AnalysisActivity airway reference helpers",
)

text = text.replace(
    '"Líneas medias: la tabla proporcionada indica observación de coincidencia, no una medida en mm. " +',
    '"Líneas medias: este módulo compara referencias homólogas derecha/izquierda y no asigna por sí solo un umbral diagnóstico. " +'
)

# Report size should reflect only measurements that can actually be calculated.
text = replace_once(
    text,
    '''        int linearCount =
                (!linearDefinitions.isEmpty()
                        && !Double.isNaN(mmPerPixel)
                        && mmPerPixel > 0)
                        ? linearDefinitions.size()
                        : 0;
''',
    '''        int angularCount = 0;
        for (MeasurementDefinition def : definitions) {
            if (measurementView.calculate(def) != null) angularCount++;
        }

        int linearCount = 0;
        if (!linearDefinitions.isEmpty()
                && !Double.isNaN(mmPerPixel)
                && mmPerPixel > 0) {
            for (LinearMeasurementDefinition def : linearDefinitions) {
                if (calculateLinear(def) != null) linearCount++;
            }
        }
''',
    "AnalysisActivity report counts",
)
text = replace_once(
    text,
    "                ((definitions.size() + linearCount) * rowHeight) +",
    "                ((angularCount + linearCount) * rowHeight) +",
    "AnalysisActivity report height",
)
write(act_path, text)


# -----------------------------------------------------------------------------
# Strings in both languages.
# -----------------------------------------------------------------------------
for rel, points, tracing, hint in [
    (
        "app/src/main/res/values/strings.xml",
        "GUARDAR RADIOGRAFÍA CON PUNTOS",
        "GUARDAR RADIOGRAFÍA CON TRAZADO",
        "Trazado: toque para colocar el punto seleccionado; arrastre con un dedo para navegar, pellizque para zoom y mantenga presionado un punto para moverlo con lupa.",
    ),
    (
        "app/src/main/res/values-en/strings.xml",
        "SAVE RADIOGRAPH WITH POINTS",
        "SAVE RADIOGRAPH WITH TRACING",
        "Tracing: tap to place the selected landmark; drag with one finger to pan, pinch to zoom, and long-press a placed landmark to move it with the magnifier.",
    ),
]:
    s = read(rel)
    marker = '    <string name="export_annotated">'
    idx = s.find(marker)
    if idx < 0:
        raise RuntimeError(f"Missing export marker in {rel}")
    line_end = s.find("\n", idx)
    insertion = (
        f'    <string name="export_points">{points}</string>\n'
        f'    <string name="export_tracing">{tracing}</string>\n'
    )
    s = s[:line_end+1] + insertion + s[line_end+1:]
    s = re.sub(
        r'<string name="trace_mode_hint">.*?</string>',
        f'<string name="trace_mode_hint">{hint}</string>',
        s,
        count=1,
    )
    write(rel, s)


# -----------------------------------------------------------------------------
# Documentation / clinical audit trail.
# -----------------------------------------------------------------------------
guide_md = '''# YomCeph — Guía reproducible de colocación de puntos

Actualización: 2026-09-10.

Esta guía documenta las convenciones que usa la app. Los dibujos integrados son **esquemas orientativos, no a escala**, y nunca intervienen en los cálculos. La ubicación final debe hacerse sobre la anatomía radiográfica visible.

## Flujo de trabajo

1. Elegir análisis.
2. Seleccionar radiografía.
3. Asignar nombre/número del estudio y datos diferenciadores del paciente.
4. Calibrar solo cuando el módulo necesite distancias lineales y exista una referencia válida.
5. Seleccionar explícitamente cada punto y colocarlo con un toque. La selección no avanza sola.
6. Un dedo arrastra la radiografía; pellizco amplía/reduce. Para corregir un punto ya colocado, mantener presionado el punto y arrastrarlo con la lupa.
7. El informe puede ser parcial: solo aparecen las medidas para las que estén presentes todos los puntos necesarios.

## Steiner / Tweed

Los puntos S, N, A, B, Po, Or, ENA/PNS, Ar, Go, Me y Gn siguen las definiciones cefalométricas convencionales. Para el plano oclusal de Steiner, YomCeph adopta un punto anterior equidistante entre los bordes incisales superior/inferior y un punto posterior en la intercuspidación/superposición de los primeros molares.

Referencia sobre plano oclusal de Steiner:
- https://www.scielo.cl/scielo.php?pid=S0719-01072015000300010&script=sci_arttext

## Postura cervical / Solow

YomCeph usa puntos compartidos para no marcar dos veces el mismo sitio:
- **Cv2tg**: punto de tangencia sobre el contorno dorsal de la odontoides de C2.
- **Cv2ip**: punto más posteroinferior del cuerpo de C2.
- **Cv4ip**: punto más posteroinferior del cuerpo de C4.
- **OPT** = Cv2tg–Cv2ip.
- **CVT** = Cv2tg–Cv4ip.

Referencias:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC5676314/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC4792970/

La antigua medición “McGregor–C4” se retiró porque la implementación existente dependía de dos puntos C4-1/C4-2 sin definición anatómica reproducible ni respaldo suficiente para el rango usado.

## Rocabado / triángulo hioideo

- H: punto más superior y anterior del cuerpo del hioides.
- C3: punto anteroinferior del cuerpo de C3.
- RGn: punto posteroinferior de la sínfisis.
- C0/Occipital + ENP: línea de McGregor.
- La profundidad cervical se obtiene respecto de la tangente posterior C2–C7, con la concavidad medida cerca de C4.

## Vía aérea

Convención adoptada por la app:
- **AD1**: punto del tejido adenoideo/pared posterior sobre la línea ENP(PNS)–Ba; PNS–AD1 es la distancia desde ENP al punto más cercano de tejido adenoideo sobre esa línea.
- **AD2**: punto sobre la línea que pasa por ENP y es perpendicular a S–Ba; PNS–AD2 es la distancia desde ENP al tejido adenoideo más cercano sobre esa perpendicular.
- **McNamara superior**: distancia mínima desde el contorno posterior del paladar blando a la pared faríngea posterior.
- **McNamara inferior**: distancia mínima desde el punto donde el contorno posterior de la lengua cruza el borde inferior mandibular a la pared faríngea posterior.

Referencias:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC9128391/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC5035718/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC3520347/

**AD3 Uptp–Adenoides se retiró.** No se mantuvo una medida cuya construcción y valores dependían de una “tabla aportada” que no forma parte de la app y cuya geometría no pudo verificarse de manera reproducible con las fuentes revisadas.

## Levandoski

La línea 1 es la línea media vertical maxilar que pasa por el septum nasal. Las líneas horizontales clásicas son perpendiculares a esa línea y pasan/tangencian el borde inferior de la sínfisis, la punta condilar y la punta coronoidea. Cd, Go y Kr/Cor se marcan de forma homóloga en ambos lados.

Referencias:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC5052233/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC9157585/

## Powell

Los puntos de tejidos blandos G', N', Pr, Pg', Me' y C se conservan como referencias del perfil. El esquema de la app es solo un localizador aproximado y no sustituye la identificación del contorno blando real.
'''
write("LANDMARK_PLACEMENT_GUIDE.md", guide_md)

audit_path = "CLINICAL_REFERENCE_AUDIT.md"
audit = read(audit_path)
audit = audit.replace("Última revisión: 2026-09-09.", "Última revisión: 2026-09-10.")
audit = audit.replace(
    "Los valores AD1/AD2/AD3 de YomCeph permanecen identificados explícitamente como tabla docente aportada y no se convierten en umbrales diagnósticos automáticos.",
    "AD1 y AD2 permanecen como medidas geométricas sin umbral diagnóstico automático. Se retiró AD3 Uptp–Adenoides porque la construcción previa dependía de una tabla no incluida en la app y no pudo verificarse de forma reproducible con las fuentes revisadas. Las convenciones de colocación se documentan en LANDMARK_PLACEMENT_GUIDE.md."
)
audit += "\n\n## Revisión de puntos y flujo 2026-09-10\n\n- OPT se construye con Cv2tg–Cv2ip y CVT con Cv2tg–Cv4ip, compartiendo Cv2tg para evitar duplicación del mismo punto anatómico.\n- Se retiró la medición McGregor–C4 que dependía de C4-1/C4-2 sin definición reproducible.\n- El análisis parcial ahora omite únicamente las medidas cuyos puntos estén incompletos.\n- Se separan las exportaciones de radiografía con puntos y radiografía con trazado.\n- La guía visual integrada es un esquema original, no a escala y no interviene en los cálculos.\n"
write(audit_path, audit)


# -----------------------------------------------------------------------------
# Integrity test: prevent the removed ambiguous airway/cervical landmarks from
# silently returning later.
# -----------------------------------------------------------------------------
test = r'''package com.cefalo.angulos;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public class LandmarkCatalogIntegrityTest {
    @Test
    public void airwayDoesNotExposeUnverifiedAd3() {
        for (LinearMeasurementDefinition def : LinearMeasurementCatalog.airway()) {
            assertFalse(def.name.startsWith("AD3"));
            for (String p : def.pointLabels) {
                assertFalse("Uptp".equals(p));
            }
        }
    }

    @Test
    public void cervicalTangentsUseSharedReproduciblePoints() {
        boolean cvt = false;
        boolean opt = false;
        for (MeasurementDefinition def : MeasurementCatalog.vertebral()) {
            if ("SN / CVT".equals(def.name)) {
                cvt = contains(def.pointLabels, "Cv2tg") && contains(def.pointLabels, "Cv4ip");
            }
            if ("SN / OPT".equals(def.name)) {
                opt = contains(def.pointLabels, "Cv2tg") && contains(def.pointLabels, "Cv2ip");
            }
            assertFalse("McGregor–C4".equals(def.name));
        }
        assertTrue(cvt);
        assertTrue(opt);
    }

    private boolean contains(String[] values, String expected) {
        for (String value : values) {
            if (expected.equals(value)) return true;
        }
        return false;
    }
}
'''
write("app/src/test/java/com/cefalo/angulos/LandmarkCatalogIntegrityTest.java", test)

print("YomCeph redesign patch applied successfully")
