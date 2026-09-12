from pathlib import Path

# This script runs after prepare-test-build.py in the redesign branch.
# It adds clinically-audited complementary measurements, a safe C2-C5 fallback,
# richer airway guidance, and schematic visual help without copying published figures.

# -----------------------------------------------------------------------------
# 1) Angular catalog: Bjork-Jarabak complements + soft-palate angle
# -----------------------------------------------------------------------------
measurement_catalog = Path('app/src/main/java/com/cefalo/angulos/MeasurementCatalog.java')
m = measurement_catalog.read_text(encoding='utf-8')

steiner_return = '''        return list;\n    }\n\n    /** Módulo: Postura cráneo-cervical. */'''
if 'Ángulo de la silla · N-S-Ar' not in m and steiner_return in m:
    additions = '''        // Complementos Björk-Jarabak. Reutilizan N, S, Ar, Go y Me,\n        // por lo que añaden información vertical sin multiplicar landmarks difíciles.\n        list.add(m(\n                "Ángulo de la silla · N-S-Ar",\n                THREE_POINTS,\n                p("N", "S", "Ar"),\n                117, 129,\n                "123° ± 6° · referencia Björk-Jarabak",\n                "Marque N, S y Ar. S es el vértice. Este ángulo forma parte de la suma de Björk-Jarabak.",\n                "Por debajo del intervalo: contribuye a una suma posterior menor; puede acompañar una tendencia de rotación mandibular más anterior, pero debe interpretarse junto con los ángulos articular y goníaco.",\n                "Dentro del intervalo 123° ± 6° de la referencia adoptada.",\n                "Por encima del intervalo: contribuye a una suma posterior mayor; puede acompañar una tendencia de rotación mandibular más posterior, pero no se interpreta de forma aislada.",\n                false\n        ));\n\n        list.add(m(\n                "Ángulo articular · S-Ar-Go",\n                THREE_POINTS,\n                p("S", "Ar", "Go"),\n                138, 148,\n                "143° ± 5° · referencia Björk-Jarabak",\n                "Marque S, Ar y Go. Ar es el vértice. Forma parte de la suma de Björk-Jarabak.",\n                "Por debajo del intervalo: reduce la suma de Björk-Jarabak y describe una relación posterior base craneal-rama más cerrada; correlacione con patrón vertical y goníaco.",\n                "Dentro del intervalo 143° ± 5° de la referencia adoptada.",\n                "Por encima del intervalo: aumenta la suma de Björk-Jarabak y describe una relación posterior base craneal-rama más abierta; correlacione con el resto del patrón vertical.",\n                false\n        ));\n\n        list.add(m(\n                "Ángulo goníaco superior · Ar-Go-N",\n                THREE_POINTS,\n                p("Ar", "Go", "N"),\n                49, 55,\n                "52° ± 3° · referencia Björk-Jarabak",\n                "Marque Ar, Go y N. Go es el vértice; representa el componente superior del ángulo goníaco.",\n                "Por debajo del intervalo: componente goníaco superior relativamente cerrado; describir junto con el componente inferior y la suma de Björk-Jarabak.",\n                "Dentro del intervalo 52° ± 3° de la referencia adoptada.",\n                "Por encima del intervalo: componente goníaco superior relativamente abierto; describir junto con el componente inferior y la suma de Björk-Jarabak.",\n                false\n        ));\n\n        list.add(m(\n                "Ángulo goníaco inferior · N-Go-Me",\n                THREE_POINTS,\n                p("N", "Go", "Me"),\n                68, 72,\n                "70° ± 2° · referencia Björk-Jarabak",\n                "Marque N, Go y Me. Go es el vértice; representa el componente inferior del ángulo goníaco.",\n                "Por debajo del intervalo: componente inferior relativamente cerrado, compatible con una tendencia mandibular más horizontal dentro del conjunto del análisis.",\n                "Dentro del intervalo 70° ± 2° de la referencia adoptada.",\n                "Por encima del intervalo: componente inferior relativamente abierto, compatible con una tendencia vertical/rotación posterior mayor dentro del conjunto del análisis.",\n                false\n        ));\n\n'''
    m = m.replace(steiner_return, additions + steiner_return, 1)

old_airway_angles = '''    public static List<MeasurementDefinition> airwayAngles() {\n        return new ArrayList<>();\n    }'''
if old_airway_angles in m:
    new_airway_angles = '''    public static List<MeasurementDefinition> airwayAngles() {\n        List<MeasurementDefinition> list = new ArrayList<>();\n\n        list.add(m(\n                "Ángulo del paladar blando · ENA-ENP-P",\n                THREE_POINTS,\n                p("ENA", "ENP", "P"),\n                Double.NaN,\n                Double.NaN,\n                "Medida descriptiva; el valor depende de edad, postura y población",\n                "Marque ENA, ENP/PNS y P (punta de la úvula/paladar blando). ENP es el vértice; se compara el paladar duro ENA-ENP con el eje del paladar blando ENP-P.",\n                "",\n                "Un ángulo mayor indica una inclinación relativamente más caudal/posterior del paladar blando respecto al paladar duro; uno menor indica una disposición relativamente más horizontal. No existe un umbral universal que diagnostique obstrucción o apnea en una telerradiografía 2D.",\n                "",\n                false\n        ));\n\n        return list;\n    }'''
    m = m.replace(old_airway_angles, new_airway_angles, 1)

measurement_catalog.write_text(m, encoding='utf-8')

# -----------------------------------------------------------------------------
# 2) Linear definition: partial cervical interpretation
# -----------------------------------------------------------------------------
linear_def = Path('app/src/main/java/com/cefalo/angulos/LinearMeasurementDefinition.java')
ld = linear_def.read_text(encoding='utf-8')
if 'CERVICAL_PARTIAL' not in ld:
    ld = ld.replace(
        '''        HYOID_TRIANGLE,\n        CERVICAL_DEPTH,\n        COMPARATIVE''',
        '''        HYOID_TRIANGLE,\n        CERVICAL_DEPTH,\n        CERVICAL_PARTIAL,\n        COMPARATIVE'''
    )

    branch_anchor = '''        if (interpretation == Interpretation.CERVICAL_DEPTH) {'''
    partial_branch = '''        if (interpretation == Interpretation.CERVICAL_PARTIAL) {\n            if (valueMm < 0.0) {\n                return "Evaluación parcial C2-C5: la curvatura superior se proyecta hacia el lado opuesto de la referencia anterior. Describir como inversión/cifosis del segmento visible, sin aplicar los umbrales de Penning C2-C7.";\n            }\n            return "Evaluación parcial C2-C5: se informa la profundidad del segmento cervical visible. No es equivalente a Penning C2-C7 y no debe clasificarse con sus límites de 8-12 mm.";\n        }\n\n'''
    ld = ld.replace(branch_anchor, partial_branch + branch_anchor, 1)

linear_def.write_text(ld, encoding='utf-8')

# -----------------------------------------------------------------------------
# 3) Linear catalog: C2-C5 fallback + clearer airway measure
# -----------------------------------------------------------------------------
linear_catalog = Path('app/src/main/java/com/cefalo/angulos/LinearMeasurementCatalog.java')
l = linear_catalog.read_text(encoding='utf-8')
if 'CERVICAL_PARTIAL' not in l.split('public final class')[0]:
    l = l.replace(
        'import static com.cefalo.angulos.LinearMeasurementDefinition.Interpretation.CERVICAL_DEPTH;\n',
        'import static com.cefalo.angulos.LinearMeasurementDefinition.Interpretation.CERVICAL_DEPTH;\nimport static com.cefalo.angulos.LinearMeasurementDefinition.Interpretation.CERVICAL_PARTIAL;\n'
    )

penning_block = '''        list.add(m(\n                "Profundidad de la columna cervical · Penning",\n                SIGNED_PERPENDICULAR,\n                CERVICAL_DEPTH,\n                p("C2 post-sup.", "C7 post-inf.", "Profundidad cervical"),\n                8.0,\n                12.0,\n                "10 ± 2 mm · rectificada <8 · cifótica si negativa · lordosis aumentada >12",\n                "",\n                "",\n                ""\n        ));\n'''
if 'Evaluación parcial C2-C5' not in l and penning_block in l:
    partial = '''\n        list.add(m(\n                "Evaluación parcial C2-C5 · si C6/C7 no son visibles",\n                SIGNED_PERPENDICULAR,\n                CERVICAL_PARTIAL,\n                p("C2 post-sup.", "C5 post-inf.", "Profundidad cervical C2-C5"),\n                Double.NaN,\n                Double.NaN,\n                "Alternativa descriptiva del segmento visible; NO usar los límites de Penning C2-C7",\n                "",\n                "Evaluación parcial C2-C5. Úsela solo cuando C6/C7 estén fuera del campo o tapadas por los hombros. El resultado describe el segmento visible y no sustituye una radiografía cervical completa.",\n                ""\n        ));\n'''
    l = l.replace(penning_block, penning_block + partial, 1)

# Rename McNamara measures to make the construction obvious.
l = l.replace('"Faringe superior", DISTANCE, RANGE,', '"McNamara · vía aérea superior mínima", DISTANCE, RANGE,')
l = l.replace('"Faringe posterior o inferior", DISTANCE, RANGE,', '"McNamara · vía aérea inferior mínima", DISTANCE, RANGE,')

# Add a C2-level posterior airway space that is easy to reproduce and explain.
airway_insert = '''        list.add(m("MP-H · hioides a plano mandibular", PERPENDICULAR_ABS, RANGE,'''
if 'PAS a nivel de C2' not in l and airway_insert in l:
    pas = '''        list.add(m("PAS a nivel de C2 · espacio aéreo posterior", DISTANCE, RANGE,\n                p("PAS ant.", "PAS post."), Double.NaN, Double.NaN,\n                "Distancia base de lengua-pared faríngea posterior a la altura de C2; usar referencia por edad/población",\n                "",\n                "Un valor menor representa un espacio aéreo anteroposterior más estrecho en ese nivel; un valor mayor representa un espacio más amplio. La medida 2D no diagnostica apnea, obstrucción ni hipertrofia por sí sola.",\n                ""));\n\n'''
    l = l.replace(airway_insert, pas + airway_insert, 1)

linear_catalog.write_text(l, encoding='utf-8')

# -----------------------------------------------------------------------------
# 4) Point guide: optional C5 and detailed airway landmarks
# -----------------------------------------------------------------------------
guide = Path('app/src/main/java/com/cefalo/angulos/PointGuide.java')
g = guide.read_text(encoding='utf-8')

c7_anchor = '        GUIDE.put("C7 post-inf.", "C7 posteroinferior para Penning: landmark inferior de la tangente posterior C2-C7. Debe marcarse junto con C2 post-sup.; ambos puntos forman la línea sobre la que se calcula la profundidad cervical.");\n'
if 'GUIDE.put("C5 post-inf."' not in g and c7_anchor in g:
    g = g.replace(c7_anchor, c7_anchor +
        '        GUIDE.put("C5 post-inf.", "C5 posteroinferior: punto más posterior e inferior del cuerpo de C5 visible. Úselo únicamente para la evaluación parcial C2-C5 cuando C6/C7 no puedan identificarse; no lo sustituya por C7 dentro de Penning.");\n'
        '        GUIDE.put("Profundidad cervical C2-C5", "Punto de máxima profundidad posterior del segmento cervical visible, habitualmente alrededor de C3-C4, medido perpendicularmente a la línea de referencia C2-C5. Es una alternativa descriptiva cuando C6/C7 no se ven y no comparte los límites diagnósticos de Penning C2-C7.");\n')

# More explicit adenoid and airway instructions.
repls = {
    'GUIDE.put("AD1", "AD1: punto más prominente del tejido adenoideo o de la pared faríngea posterior sobre la línea que une ENP/PNS con Basion. Se mide ENP-AD1 siguiendo esa misma dirección.");':
    'GUIDE.put("AD1", "AD1: primero imagine/trace la línea ENP/PNS-Ba. AD1 es exactamente el punto donde esa línea encuentra el contorno anterior del tejido adenoideo o, si éste no es distinguible, la pared faríngea posterior. No elija el punto más grueso de la adenoides fuera de esa línea. La medida resultante es ENP-AD1.");',
    'GUIDE.put("AD2", "AD2: punto más prominente del tejido adenoideo o de la pared faríngea posterior sobre la línea que parte de ENP/PNS y es perpendicular a S-Ba.");':
    'GUIDE.put("AD2", "AD2: trace mentalmente S-Ba; desde ENP/PNS construya una perpendicular a S-Ba. AD2 es el punto donde esa perpendicular toca el contorno anterior adenoideo/pared faríngea posterior. La dirección la determina la perpendicular; no coloque AD2 libremente sobre cualquier parte de la adenoides.");',
    'GUIDE.put("AD3", "ad3: punto del tejido adenoideo o pared faríngea dorsal más cercano a tu en el protocolo de Solow. La medición tu-ad3 es la distancia mínima entre ambos puntos.");':
    'GUIDE.put("AD3", "AD3/ad3: después de identificar tu en la tuberosidad maxilar/pterigomaxilar, busque el punto del contorno adenoideo o pared faríngea dorsal que quede a la MENOR distancia de tu. Ese punto más cercano es ad3; la app mide tu-ad3. Si tu o el contorno adenoideo no son claros, no fuerce la medición.");',
    'GUIDE.put("Faringe sup ant.", "Faringe superior anterior de McNamara: punto del contorno posterior del paladar blando desde el cual se obtiene la menor distancia hacia la pared faríngea posterior.");':
    'GUIDE.put("Faringe sup ant.", "McNamara superior, punto anterior: en el borde posterior del paladar blando, busque el sitio cuya distancia a la pared faríngea posterior sea mínima. Marque ese punto en el paladar blando; después marque su contraparte más cercana en la pared posterior.");',
    'GUIDE.put("Faringe sup post.", "Faringe superior posterior de McNamara: punto más cercano de la pared faríngea posterior al punto anterior de la vía aérea superior.");':
    'GUIDE.put("Faringe sup post.", "McNamara superior, punto posterior: punto de la pared faríngea posterior más próximo al punto anterior marcado sobre el paladar blando. El segmento entre ambos debe representar la distancia mínima, no una línea horizontal arbitraria.");',
    'GUIDE.put("Faringe inf ant.", "Faringe inferior anterior de McNamara: punto donde el contorno posterior de la lengua cruza el borde inferior de la mandíbula; desde aquí se obtiene la menor distancia a la pared faríngea posterior.");':
    'GUIDE.put("Faringe inf ant.", "McNamara inferior, punto anterior: localice donde el contorno posterior de la lengua cruza o coincide con el borde inferior mandibular; desde ese punto busque la menor distancia hacia la pared faríngea posterior.");',
    'GUIDE.put("Faringe inf post.", "Faringe inferior posterior de McNamara: punto más cercano de la pared faríngea posterior a la altura del punto anterior inferior.");':
    'GUIDE.put("Faringe inf post.", "McNamara inferior, punto posterior: punto de la pared faríngea posterior más cercano al punto anterior inferior. Marque el extremo que produzca la distancia mínima entre lengua y pared posterior.");',
    'GUIDE.put("PAS ant.", "PAS anterior: punto de la base/posterior de la lengua sobre la dirección usada para medir el espacio aéreo posterior hacia la pared faríngea. La construcción exacta debe permanecer vinculada al protocolo elegido.");':
    'GUIDE.put("PAS ant.", "PAS anterior a nivel de C2: marque el punto de la base/posterior de la lengua sobre una línea que cruza la vía aérea a la altura de C2. Debe quedar enfrentado a la pared faríngea posterior en ese mismo nivel.");',
    'GUIDE.put("PAS post.", "PAS posterior: punto correspondiente de la pared faríngea posterior sobre la misma dirección que PAS anterior.");':
    'GUIDE.put("PAS post.", "PAS posterior a nivel de C2: marque en la pared faríngea posterior el punto enfrentado a PAS anterior, manteniendo el mismo nivel de C2. La distancia entre ambos representa el espacio aéreo posterior 2D en ese nivel.");'
}
for old, new in repls.items():
    if old in g:
        g = g.replace(old, new, 1)

guide.write_text(g, encoding='utf-8')

# -----------------------------------------------------------------------------
# 5) Visual reference diagrams drawn inside the app (original schematic artwork)
# -----------------------------------------------------------------------------
reference_view = Path('app/src/main/java/com/cefalo/angulos/ReferenceDiagramView.java')
reference_view.write_text(r'''package com.cefalo.angulos;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Path;
import android.view.View;

/**
 * Original schematic landmark guide drawn at runtime.
 * It intentionally avoids reproducing any published figure or patient radiograph.
 */
public class ReferenceDiagramView extends View {
    private final Paint line = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint accent = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint text = new Paint(Paint.ANTI_ALIAS_FLAG);
    private String label = "";

    public ReferenceDiagramView(Context context) {
        super(context);
        line.setColor(Color.rgb(115, 120, 132));
        line.setStyle(Paint.Style.STROKE);
        line.setStrokeWidth(dp(2));
        accent.setColor(Color.rgb(126, 87, 194));
        accent.setStyle(Paint.Style.FILL);
        text.setColor(Color.rgb(52, 58, 68));
        text.setTextSize(dp(11));
        text.setFakeBoldText(true);
        setMinimumHeight((int) dp(210));
    }

    public void setLandmark(String label) {
        this.label = label == null ? "" : label;
        invalidate();
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        canvas.drawColor(Color.rgb(247, 248, 250));
        if (isCervical()) drawCervical(canvas);
        else if (isAirway()) drawAirway(canvas);
        else if (isHyoid()) drawHyoid(canvas);
        else drawCephalometric(canvas);
    }

    private boolean isCervical() {
        return label.startsWith("C1") || label.startsWith("C2") || label.startsWith("C3")
                || label.startsWith("C4") || label.startsWith("C5") || label.startsWith("C6")
                || label.startsWith("C7") || label.startsWith("CV") || label.startsWith("OPT")
                || label.contains("Profundidad cervical") || label.contains("Odontoides");
    }

    private boolean isHyoid() {
        return label.equals("H") || label.equals("RGn") || label.equals("AA");
    }

    private boolean isAirway() {
        return label.startsWith("AD") || label.equals("Ba") || label.equals("tu")
                || label.equals("P") || label.startsWith("Faringe") || label.startsWith("PAS")
                || label.equals("ENP") || label.equals("ENA");
    }

    private void drawCephalometric(Canvas c) {
        float w = getWidth(), h = getHeight();
        Path skull = new Path();
        skull.moveTo(w*.18f,h*.55f); skull.cubicTo(w*.18f,h*.18f,w*.68f,h*.08f,w*.78f,h*.34f);
        skull.cubicTo(w*.86f,h*.55f,w*.70f,h*.72f,w*.58f,h*.78f);
        skull.cubicTo(w*.50f,h*.90f,w*.29f,h*.86f,w*.26f,h*.69f);
        c.drawPath(skull,line);
        c.drawLine(w*.37f,h*.30f,w*.55f,h*.25f,line); // SN
        c.drawLine(w*.48f,h*.58f,w*.64f,h*.67f,line); // mandibular
        point(c,w*.38f,h*.30f,"S"); point(c,w*.55f,h*.25f,"N");
        point(c,w*.63f,h*.44f,"A"); point(c,w*.62f,h*.57f,"B");
        point(c,w*.45f,h*.50f,"Ar"); point(c,w*.48f,h*.67f,"Go");
        point(c,w*.64f,h*.67f,"Me"); point(c,w*.66f,h*.60f,"Pg");
        c.drawText("Esquema lateral · use la anatomía real de su radiografía", dp(10), h-dp(10), text);
    }

    private void drawCervical(Canvas c) {
        float w = getWidth(), h = getHeight();
        float x = w*.56f;
        // odontoid
        c.drawRoundRect(x-dp(8), h*.10f, x+dp(8), h*.27f, dp(6), dp(6), line);
        // C2-C7 bodies
        for (int i=0;i<6;i++) {
            float top = h*(.24f + i*.105f);
            c.drawRoundRect(x-dp(28), top, x+dp(28), top+h*.07f, dp(5), dp(5), line);
            c.drawText("C"+(i+2), x+dp(36), top+h*.05f, text);
        }
        float topX=x-dp(22), bottomX=x-dp(30);
        c.drawLine(topX,h*.18f,bottomX,h*.84f,line);
        c.drawText("C2–C7", dp(10), h*.18f, text);
        c.drawText("Si C6/C7 no se ven → use solo la alternativa C2–C5", dp(10), h*.92f, text);
        // highlight approximate level
        if (label.startsWith("C5")) point(c,x-dp(28),h*(.24f+3*.105f)+h*.07f,"C5");
        else if (label.startsWith("C7")) point(c,x-dp(28),h*(.24f+5*.105f)+h*.07f,"C7");
        else point(c,x-dp(22),h*.18f,"CV2tg/C2");
    }

    private void drawHyoid(Canvas c) {
        float w=getWidth(), h=getHeight();
        point(c,w*.25f,h*.40f,"C3");
        point(c,w*.72f,h*.42f,"RGn");
        point(c,w*.50f,h*.68f,"H");
        c.drawLine(w*.25f,h*.40f,w*.72f,h*.42f,line);
        c.drawLine(w*.25f,h*.40f,w*.50f,h*.68f,line);
        c.drawLine(w*.50f,h*.68f,w*.72f,h*.42f,line);
        c.drawText("Triángulo hioideo C3–RGn–H", dp(10), h*.88f, text);
    }

    private void drawAirway(Canvas c) {
        float w=getWidth(), h=getHeight();
        // simplified craniofacial outline
        Path face = new Path();
        face.moveTo(w*.18f,h*.22f); face.cubicTo(w*.38f,h*.08f,w*.70f,h*.12f,w*.73f,h*.28f);
        face.cubicTo(w*.78f,h*.40f,w*.70f,h*.50f,w*.72f,h*.67f);
        c.drawPath(face,line);
        // hard + soft palate
        c.drawLine(w*.33f,h*.40f,w*.57f,h*.40f,line);
        c.drawLine(w*.57f,h*.40f,w*.66f,h*.57f,line);
        // posterior pharyngeal wall
        c.drawLine(w*.78f,h*.31f,w*.78f,h*.80f,line);
        // tongue
        Path tongue = new Path(); tongue.moveTo(w*.45f,h*.69f); tongue.cubicTo(w*.58f,h*.58f,w*.69f,h*.64f,w*.70f,h*.77f); c.drawPath(tongue,line);
        point(c,w*.33f,h*.40f,"ENA"); point(c,w*.57f,h*.40f,"ENP"); point(c,w*.66f,h*.57f,"P");
        point(c,w*.78f,h*.39f,"AD1/2"); point(c,w*.72f,h*.71f,"PAS");
        c.drawLine(w*.57f,h*.40f,w*.78f,h*.39f,line);
        c.drawLine(w*.70f,h*.71f,w*.78f,h*.71f,line);
        c.drawText("Vía aérea: cada punto depende de una línea/nivel anatómico", dp(10), h*.90f, text);
    }

    private void point(Canvas c, float x, float y, String name) {
        c.drawCircle(x,y,dp(4),accent);
        c.drawText(name,x+dp(7),y-dp(5),text);
    }

    private float dp(float v) { return v * getResources().getDisplayMetrics().density; }
}
''', encoding='utf-8')

# -----------------------------------------------------------------------------
# 6) Analysis UI: visual guide dialog, explicit range status, partial cervical sign
# -----------------------------------------------------------------------------
analysis = Path('app/src/main/java/com/cefalo/angulos/AnalysisActivity.java')
a = analysis.read_text(encoding='utf-8')

# The compact help card should open the same complete visual guide as a long-press on a chip.
a = a.replace(
    'txtInstruction.setOnClickListener(v -> showFullPointDescription());',
    'txtInstruction.setOnClickListener(v -> showCurrentPointGuide());'
)

# Replace mascot-only help with a schematic diagram tied to the selected point.
old_mascot = '''        ImageView image = new ImageView(this);\n        image.setImageResource(\n                R.drawable.tooth_ruler_mascot\n        );\n        image.setScaleType(\n                ImageView.ScaleType.CENTER_INSIDE\n        );\n\n        box.addView(\n                image,\n                new LinearLayout.LayoutParams(\n                        dp(96),\n                        dp(74)\n                )\n        );\n'''
if old_mascot in a:
    new_diagram = '''        ReferenceDiagramView diagram = new ReferenceDiagramView(this);\n        diagram.setLandmark(label);\n        box.addView(\n                diagram,\n                new LinearLayout.LayoutParams(\n                        ViewGroup.LayoutParams.MATCH_PARENT,\n                        dp(220)\n                )\n        );\n'''
    a = a.replace(old_mascot, new_diagram, 1)

# Update status text in the point-help dialog to match long-press editing behavior.
a = a.replace(
    '"\\n\\n✓ Ya está colocado. Para corregirlo, seleccione su recuadro y toque la nueva posición en la radiografía."',
    '"\\n\\n✓ Ya está colocado. Para corregirlo, mantenga el dedo sobre el punto y arrástrelo, o use 🎯 AJUSTE FINO."'
)

# Orientation for the partial C2-C5 signed depth must be consistent with Penning.
a = a.replace(
    '''        if (def.interpretation\n                == LinearMeasurementDefinition.Interpretation.CERVICAL_DEPTH) {''',
    '''        if (def.interpretation\n                == LinearMeasurementDefinition.Interpretation.CERVICAL_DEPTH\n                || def.interpretation\n                == LinearMeasurementDefinition.Interpretation.CERVICAL_PARTIAL) {'''
)

# Explicit range-state label for every angular result with validated limits.
helper_anchor = '''    private void showResultsDialog() {\n'''
if 'private String angularRangeStatus(' not in a and helper_anchor in a:
    helper = '''    private String angularRangeStatus(MeasurementDefinition def, double value) {\n        if (def == null || Double.isNaN(def.normalMin) || Double.isNaN(def.normalMax)) {\n            return "DESCRIPTIVA · sin rango universal automático";\n        }\n        if (value < def.normalMin) return "POR DEBAJO DEL RANGO";\n        if (value > def.normalMax) return "POR ENCIMA DEL RANGO";\n        return "EN RANGO DE REFERENCIA";\n    }\n\n'''
    a = a.replace(helper_anchor, helper + helper_anchor, 1)

old_angular_text = '''                    "   ·   Referencia: " +\n                    def.normText +\n                    "\\n" +\n                    def.diagnosis(value)\n'''
if old_angular_text in a:
    new_angular_text = '''                    "   ·   Referencia: " +\n                    def.normText +\n                    "\\nEstado: " +\n                    angularRangeStatus(def, value) +\n                    "\\nSignificado clínico: " +\n                    def.diagnosis(value)\n'''
    a = a.replace(old_angular_text, new_angular_text, 1)

# Compact chip names for new optional cervical point and PAS.
a = a.replace(
    'case "C7 post-inf.": return "C7pi";',
    'case "C7 post-inf.": return "C7pi";\n            case "C5 post-inf.": return "C5pi";\n            case "Profundidad cervical C2-C5": return "PC5";\n            case "PAS ant.": return "PASa";\n            case "PAS post.": return "PASp";'
)

analysis.write_text(a, encoding='utf-8')

# -----------------------------------------------------------------------------
# 7) Build-time tests for the new clinical extensions
# -----------------------------------------------------------------------------
test = Path('app/src/test/java/com/cefalo/angulos/ClinicalExtensionTest.java')
test.parent.mkdir(parents=True, exist_ok=True)
test.write_text(r'''package com.cefalo.angulos;

import static org.junit.Assert.assertTrue;
import org.junit.Test;

public class ClinicalExtensionTest {
    @Test
    public void cephalometricComplementsArePresent() {
        boolean saddle = false, articular = false, upper = false, lower = false;
        for (MeasurementDefinition d : MeasurementCatalog.steiner()) {
            saddle |= d.name.contains("silla");
            articular |= d.name.contains("articular");
            upper |= d.name.contains("goníaco superior");
            lower |= d.name.contains("goníaco inferior");
        }
        assertTrue(saddle && articular && upper && lower);
    }

    @Test
    public void airwaySoftPalateAngleIsPresent() {
        assertTrue(!MeasurementCatalog.airwayAngles().isEmpty());
    }

    @Test
    public void c2c5FallbackIsSeparateFromPenning() {
        boolean found = false;
        for (LinearMeasurementDefinition d : LinearMeasurementCatalog.rocabado()) {
            if (d.name.contains("C2-C5")) {
                found = d.interpretation == LinearMeasurementDefinition.Interpretation.CERVICAL_PARTIAL;
            }
        }
        assertTrue(found);
    }
}
''', encoding='utf-8')

print('Clinical extension build patches applied.')
