from pathlib import Path
import re

gradle = Path('app/build.gradle')
g = gradle.read_text(encoding='utf-8')
g = g.replace("applicationId 'com.yomceph.app'", "applicationId 'com.yomceph.cefalometrico'")
gradle.write_text(g, encoding='utf-8')

for rel in ['app/src/main/res/values/strings.xml', 'app/src/main/res/values-en/strings.xml']:
    path = Path(rel)
    if not path.exists():
        continue
    s = path.read_text(encoding='utf-8')
    s = re.sub(r'<string name="app_name">.*?</string>',
               '<string name="app_name">Yom Análisis Radiográficos</string>', s)
    if 'values-en' in rel:
        s = re.sub(r'<string name="app_slogan">.*?</string>',
                   '<string name="app_slogan">Cephalometrics and radiographic analysis</string>', s)
        s = re.sub(r'<string name="analysis_steiner">.*?</string>',
                   '<string name="analysis_steiner">CEPHALOMETRIC ANALYSIS · STEINER</string>', s)
    else:
        s = re.sub(r'<string name="app_slogan">.*?</string>',
                   '<string name="app_slogan">Cefalometría y análisis radiográfico</string>', s)
        s = re.sub(r'<string name="analysis_steiner">.*?</string>',
                   '<string name="analysis_steiner">ANÁLISIS CEFALOMÉTRICO · STEINER</string>', s)
    path.write_text(s, encoding='utf-8')

main = Path('app/src/main/java/com/cefalo/angulos/MainActivity.java')
m = main.read_text(encoding='utf-8')
anchor = '        updateThemeButton(btnTheme);\n'
hide = '''        // Steiner-only edition: keep the same mobile tracing engine and utilities,
        // but expose only the cephalometric lateral-skull analysis.
        btnVertebral.setVisibility(android.view.View.GONE);
        btnPowell.setVisibility(android.view.View.GONE);
        btnTweed.setVisibility(android.view.View.GONE);
        btnLevandoski.setVisibility(android.view.View.GONE);
        btnAirway.setVisibility(android.view.View.GONE);
        btnCvm.setVisibility(android.view.View.GONE);
        btnNolla.setVisibility(android.view.View.GONE);
        btnResorption.setVisibility(android.view.View.GONE);
        btnPanoramicReview.setVisibility(android.view.View.GONE);
        android.view.View panoSection = findViewById(R.id.sectionPanoramic);
        if (panoSection != null) panoSection.setVisibility(android.view.View.GONE);

        updateThemeButton(btnTheme);
'''
if anchor not in m:
    raise RuntimeError('Could not locate standalone visibility anchor')
m = m.replace(anchor, hide, 1)
main.write_text(m, encoding='utf-8')

print('Steiner-only Yom Análisis Radiográficos transform applied.')
