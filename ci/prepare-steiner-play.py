from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

# Start from the existing Steiner-only transformation.
subprocess.run([sys.executable, str(ROOT / 'ci' / 'prepare-steiner-only.py')], cwd=ROOT, check=True)

# Keep a stable, separate package identity for the dedicated Steiner app.
gradle = ROOT / 'app' / 'build.gradle'
g = gradle.read_text(encoding='utf-8')
g = g.replace("applicationId 'yom.Analisis'", "applicationId 'com.yomceph.cefalometrico'")
g = g.replace("applicationId 'com.yomceph.app'", "applicationId 'com.yomceph.cefalometrico'")
if "applicationId 'com.yomceph.cefalometrico'" not in g:
    raise RuntimeError('Could not set Steiner package identity')
gradle.write_text(g, encoding='utf-8')

# Match the Play Store product name in both supported locales.
for rel in ['app/src/main/res/values/strings.xml', 'app/src/main/res/values-en/strings.xml']:
    path = ROOT / rel
    if not path.exists():
        continue
    s = path.read_text(encoding='utf-8')
    s = re.sub(r'<string name="app_name">.*?</string>',
               '<string name="app_name">YOM Steiner</string>', s)
    path.write_text(s, encoding='utf-8')

# The dedicated edition must expose Steiner only. The older transform already
# hides the other lateral and panoramic analyses; explicitly hide the carpal
# module and its section as well.
main = ROOT / 'app/src/main/java/com/cefalo/angulos/MainActivity.java'
m = main.read_text(encoding='utf-8')
anchor = '''        android.view.View panoSection = findViewById(R.id.sectionPanoramic);\n        if (panoSection != null) panoSection.setVisibility(android.view.View.GONE);\n\n        updateThemeButton(btnTheme);\n'''
replacement = '''        android.view.View panoSection = findViewById(R.id.sectionPanoramic);\n        if (panoSection != null) panoSection.setVisibility(android.view.View.GONE);\n        if (btnCarpal != null) btnCarpal.setVisibility(android.view.View.GONE);\n        android.view.View carpalSection = findViewById(R.id.sectionCarpal);\n        if (carpalSection != null) carpalSection.setVisibility(android.view.View.GONE);\n\n        updateThemeButton(btnTheme);\n'''
if anchor not in m:
    raise RuntimeError('Could not locate Steiner visibility block')
m = m.replace(anchor, replacement, 1)
main.write_text(m, encoding='utf-8')

# Final verification.
checks = {
    'package': "applicationId 'com.yomceph.cefalometrico'" in gradle.read_text(encoding='utf-8'),
    'product name': '<string name="app_name">YOM Steiner</string>' in (ROOT / 'app/src/main/res/values/strings.xml').read_text(encoding='utf-8'),
    'carpal hidden': 'if (btnCarpal != null) btnCarpal.setVisibility(android.view.View.GONE);' in main.read_text(encoding='utf-8'),
}
missing = [name for name, ok in checks.items() if not ok]
if missing:
    raise RuntimeError('Steiner Play transformation verification failed: ' + ', '.join(missing))

print('Steiner Play edition finalized: YOM Steiner, package com.yomceph.cefalometrico, Steiner-only UI.')
