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
    # Keep the requested product name stable regardless of device language.
    s = re.sub(r'<string name="app_name">.*?</string>',
               '<string name="app_name">Yom análisis de lateral de cráneo</string>', s)
    if 'values-en' in rel:
        s = re.sub(r'<string name="app_slogan">.*?</string>',
                   '<string name="app_slogan">Lateral cephalometric analysis · Steiner</string>', s)
        s = re.sub(r'<string name="analysis_steiner">.*?</string>',
                   '<string name="analysis_steiner">CEPHALOMETRIC ANALYSIS · STEINER</string>', s)
    else:
        s = re.sub(r'<string name="app_slogan">.*?</string>',
                   '<string name="app_slogan">Cefalometría lateral · Steiner</string>', s)
        s = re.sub(r'<string name="analysis_steiner">.*?</string>',
                   '<string name="analysis_steiner">ANÁLISIS CEFALOMÉTRICO · STEINER</string>', s)
    path.write_text(s, encoding='utf-8')

main = Path('app/src/main/java/com/cefalo/angulos/MainActivity.java')
m = main.read_text(encoding='utf-8')
anchor = '        updateThemeButton(btnTheme);\n'
hide = '''        // Steiner-only edition: keep the same tracing engine and utilities,
        // but expose only lateral-skull cephalometry.
        if (btnVertebral != null) btnVertebral.setVisibility(android.view.View.GONE);
        if (btnPowell != null) btnPowell.setVisibility(android.view.View.GONE);
        if (btnTweed != null) btnTweed.setVisibility(android.view.View.GONE);
        if (btnLevandoski != null) btnLevandoski.setVisibility(android.view.View.GONE);
        if (btnAirway != null) btnAirway.setVisibility(android.view.View.GONE);
        if (btnCvm != null) btnCvm.setVisibility(android.view.View.GONE);
        if (btnNolla != null) btnNolla.setVisibility(android.view.View.GONE);
        if (btnResorption != null) btnResorption.setVisibility(android.view.View.GONE);
        if (btnPanoramicReview != null) btnPanoramicReview.setVisibility(android.view.View.GONE);
        android.view.View panoSection = findViewById(R.id.sectionPanoramic);
        if (panoSection != null) panoSection.setVisibility(android.view.View.GONE);

        updateThemeButton(btnTheme);
'''
if anchor not in m:
    raise RuntimeError('Could not locate standalone visibility anchor')
m = m.replace(anchor, hide, 1)
main.write_text(m, encoding='utf-8')

print('Steiner-only Yom análisis de lateral de cráneo transform applied.')
