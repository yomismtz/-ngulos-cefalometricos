from pathlib import Path
import re

ROOT = Path('.')
JAVA = ROOT / 'app/src/main/java/com/cefalo/angulos'

# -----------------------------------------------------------------------------
# 1) Home: add an independent CARPAL RADIOGRAPH section to the complete app.
#    The standalone lateral-skull workflow does not execute this script.
# -----------------------------------------------------------------------------
carpal_block = '''        <TextView
            android:id="@+id/sectionCarpal"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="@string/section_carpal"
            android:textColor="@color/brand_purple"
            android:textStyle="bold"
            android:textSize="16sp"
            android:gravity="center"
            android:textAlignment="center"
            android:paddingTop="2dp"
            android:paddingBottom="8dp" />

        <TextView
            android:id="@+id/btnCarpal"
            style="@style/HomeSecondaryButton"
            android:text="@string/analysis_carpal"
            android:layout_marginBottom="16dp" />

'''

for layout in [
    ROOT / 'app/src/main/res/layout/activity_main.xml',
    ROOT / 'app/src/main/res/layout-sw600dp/activity_main.xml',
]:
    if not layout.exists():
        continue
    s = layout.read_text(encoding='utf-8')
    if '@+id/btnCarpal' not in s:
        marker = '<TextView\n            android:id="@+id/sectionPanoramic"'
        index = s.find(marker)
        if index < 0:
            raise RuntimeError(f'Could not find panoramic section in {layout}')
        s = s[:index] + carpal_block + s[index:]
        layout.write_text(s, encoding='utf-8')

# Strings.
def add_string(path: Path, key: str, value: str):
    if not path.exists():
        return
    s = path.read_text(encoding='utf-8')
    if f'name="{key}"' in s:
        s = re.sub(
            rf'<string name="{re.escape(key)}">.*?</string>',
            f'<string name="{key}">{value}</string>',
            s,
            count=1,
            flags=re.S,
        )
    else:
        s = s.replace('</resources>', f'    <string name="{key}">{value}</string>\n</resources>')
    path.write_text(s, encoding='utf-8')

add_string(ROOT / 'app/src/main/res/values/strings.xml', 'section_carpal', 'RADIOGRAFÍA CARPAL')
add_string(ROOT / 'app/src/main/res/values/strings.xml', 'analysis_carpal', 'EDAD ÓSEA CARPAL · FISHMAN SMI 1–11')
add_string(ROOT / 'app/src/main/res/values-en/strings.xml', 'section_carpal', 'HAND-WRIST RADIOGRAPH')
add_string(ROOT / 'app/src/main/res/values-en/strings.xml', 'analysis_carpal', 'SKELETAL MATURITY · FISHMAN SMI 1–11')

# -----------------------------------------------------------------------------
# 2) Launcher wiring.
# -----------------------------------------------------------------------------
main = JAVA / 'MainActivity.java'
m = main.read_text(encoding='utf-8')
if 'btnCarpal' not in m:
    decl = '        TextView btnCvm = findViewById(R.id.btnCvm);\n'
    if decl not in m:
        raise RuntimeError('Could not find CVM button declaration in MainActivity')
    m = m.replace(decl, decl + '        TextView btnCarpal = findViewById(R.id.btnCarpal);\n', 1)

    click = '        setSafeClick(btnCvm, v -> openAssessment(RadiographicAssessmentActivity.MODE_CVM));\n'
    if click not in m:
        raise RuntimeError('Could not find CVM launcher binding in MainActivity')
    m = m.replace(
        click,
        click + '        setSafeClick(btnCarpal, v -> openAssessment(RadiographicAssessmentActivity.MODE_CARPAL));\n',
        1,
    )
main.write_text(m, encoding='utf-8')

# -----------------------------------------------------------------------------
# 3) Independent hand-wrist assessment screen using Fishman SMI 1-11.
# -----------------------------------------------------------------------------
assessment = JAVA / 'RadiographicAssessmentActivity.java'
r = assessment.read_text(encoding='utf-8')

if 'MODE_CARPAL' not in r:
    r = r.replace(
        '    public static final String MODE_CVM = "CVM";\n',
        '    public static final String MODE_CVM = "CVM";\n'
        '    public static final String MODE_CARPAL = "CARPAL";\n',
        1,
    )

if 'private Spinner spCarpalSmi;' not in r:
    r = r.replace(
        '    // CVM\n',
        '    // Hand-wrist / Fishman\n'
        '    private Spinner spCarpalSmi;\n\n'
        '    // CVM\n',
        1,
    )

render_anchor = '''        if (MODE_CVM.equals(mode)) {
            renderCvm();
        } else if (MODE_NOLLA.equals(mode)) {'''
if render_anchor not in r:
    raise RuntimeError('Could not locate assessment render dispatch')
r = r.replace(
    render_anchor,
    '''        if (MODE_CVM.equals(mode)) {
            renderCvm();
        } else if (MODE_CARPAL.equals(mode)) {
            renderCarpal();
        } else if (MODE_NOLLA.equals(mode)) {''',
    1,
)

if 'private void renderCarpal()' not in r:
    marker = '    private void renderNolla() {\n'
    if marker not in r:
        raise RuntimeError('Could not locate Nolla method insertion point')
    methods = r'''    private void renderCarpal() {
        addSection("Edad ósea / maduración esquelética carpal");
        addSmallText(
                "Método de Fishman (SMI 1–11). Observe la radiografía de mano-muñeca y seleccione el evento de osificación más avanzado que esté claramente presente. No requiere calibración métrica."
        );

        String[] stages = {
                "Seleccione un indicador",
                "SMI 1 · PP3: epífisis = diáfisis",
                "SMI 2 · MP3: epífisis = diáfisis",
                "SMI 3 · MP5: epífisis = diáfisis",
                "SMI 4 · sesamoideo aductor del pulgar",
                "SMI 5 · DP3: capping",
                "SMI 6 · MP3: capping",
                "SMI 7 · MP5: capping",
                "SMI 8 · DP3: fusión",
                "SMI 9 · PP3: fusión",
                "SMI 10 · MP3: fusión",
                "SMI 11 · radio: fusión"
        };
        spCarpalSmi = addSpinnerRow("Fishman", stages);

        TextView guide = makeButton("VER GUÍA SMI 1–11", true);
        guide.setOnClickListener(v -> showCarpalGuide());
        content.addView(guide, fullButtonParams());

        TextView calculate = makeButton("DETERMINAR MADURACIÓN CARPAL", false);
        calculate.setOnClickListener(v -> calculateCarpal());
        content.addView(calculate, fullButtonParams());

        txtResult = addResultCard();
        txtResult.setText(
                "Seleccione el indicador que corresponda a la radiografía. YOM informará SMI y fase de crecimiento; no convertirá el estadio a una edad exacta en años sin una referencia poblacional específica."
        );

        addInfoCard(
                "Sitios de Fishman: falanges del 3.er y 5.º dedo, sesamoideo aductor del pulgar y radio. " +
                "La secuencia progresa desde igualdad epífisis-diáfisis, aparición del sesamoideo, capping y finalmente fusión epífisis-diáfisis."
        );
    }

    private void showCarpalGuide() {
        StringBuilder b = new StringBuilder();
        for (int smi = 1; smi <= 11; smi++) {
            if (smi > 1) b.append("\n\n");
            b.append(CarpalFishmanLogic.stageDescription(smi));
        }
        new androidx.appcompat.app.AlertDialog.Builder(this)
                .setTitle("Fishman · SMI 1–11")
                .setMessage(b.toString())
                .setPositiveButton("Cerrar", null)
                .show();
    }

    private void calculateCarpal() {
        if (spCarpalSmi == null || spCarpalSmi.getSelectedItemPosition() == 0) {
            Toast.makeText(this, "Seleccione un indicador SMI 1–11.", Toast.LENGTH_LONG).show();
            return;
        }
        int smi = spCarpalSmi.getSelectedItemPosition();
        txtResult.setText(CarpalFishmanLogic.report(smi));
    }

'''
    r = r.replace(marker, methods + marker, 1)

# Titles and introductions.
r = r.replace(
    '    private String modeTitle() {\n        if (MODE_NOLLA.equals(mode)) return "Desarrollo dental · Nolla";\n',
    '    private String modeTitle() {\n'
    '        if (MODE_CARPAL.equals(mode)) return "Edad ósea carpal · Fishman";\n'
    '        if (MODE_NOLLA.equals(mode)) return "Desarrollo dental · Nolla";\n',
    1,
)

r = r.replace(
    '    private String modeIntro() {\n        if (MODE_NOLLA.equals(mode)) {\n',
    '    private String modeIntro() {\n'
    '        if (MODE_CARPAL.equals(mode)) {\n'
    '            return "Radiografía carpal (mano-muñeca) · Fishman SMI 1–11 para valorar maduración esquelética y fase de crecimiento. No requiere calibración y no equivale por sí sola a una edad cronológica exacta.";\n'
    '        }\n'
    '        if (MODE_NOLLA.equals(mode)) {\n',
    1,
)

assessment.write_text(r, encoding='utf-8')

# -----------------------------------------------------------------------------
# 4) Version and guardrails.
# -----------------------------------------------------------------------------
gradle = ROOT / 'app/build.gradle'
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 34', g, count=1)
g = re.sub(r"versionName\s+'[^']+'", "versionName '1.33'", g, count=1)
gradle.write_text(g, encoding='utf-8')

checks = {
    'carpal home button': '@+id/btnCarpal' in (ROOT / 'app/src/main/res/layout/activity_main.xml').read_text(encoding='utf-8'),
    'carpal launcher': 'MODE_CARPAL' in main.read_text(encoding='utf-8'),
    'carpal assessment mode': 'renderCarpal()' in assessment.read_text(encoding='utf-8'),
    'Fishman logic': (JAVA / 'CarpalFishmanLogic.java').exists(),
    'v1.33': "versionName '1.33'" in gradle.read_text(encoding='utf-8'),
}
missing = [name for name, ok in checks.items() if not ok]
if missing:
    raise RuntimeError('Carpal module integration incomplete: ' + ', '.join(missing))

print('Independent hand-wrist skeletal maturity module added: Fishman SMI 1-11, no calibration, v1.33.')
