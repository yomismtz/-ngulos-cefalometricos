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

# -----------------------------------------------------------------------------
# Dedicated launcher identity for the lateral-skull / Steiner edition.
# This deliberately does NOT reuse the tooth-and-rulers icon of the complete app.
# The symbol is an original vector: lateral skull silhouette + cephalometric angle.
# -----------------------------------------------------------------------------
foreground = '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">

    <!-- Perfil lateral de cráneo -->
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M34,75 C29,69 27,61 28,52 C26,45 28,36 34,29 C40,22 49,19 59,20 C69,21 77,27 80,36 C82,41 81,46 79,50 L87,54 L80,58 L81,63 L75,64 C73,74 67,82 58,86 C49,90 40,86 34,75 Z" />

    <!-- Órbita -->
    <path
        android:fillColor="#2C7E86"
        android:pathData="M57,37 C52,37 49,40 49,44 C49,48 52,51 57,51 C62,51 65,48 65,44 C65,40 62,37 57,37 Z" />

    <!-- Cavidad nasal simplificada -->
    <path
        android:fillColor="#B9F3E6"
        android:pathData="M72,46 L82,53 L74,55 L68,52 Z" />

    <!-- Plano SN y línea NA como guía cefalométrica -->
    <path
        android:fillColor="@android:color/transparent"
        android:strokeColor="#B9F3E6"
        android:strokeWidth="2.2"
        android:strokeLineCap="round"
        android:pathData="M43,35 L68,32 M68,32 L75,58" />

    <!-- Arco angular -->
    <path
        android:fillColor="@android:color/transparent"
        android:strokeColor="#FFFFFF"
        android:strokeWidth="1.8"
        android:strokeLineCap="round"
        android:pathData="M61,33 C64,37 67,40 69,45" />

    <!-- Landmarks S, N, A -->
    <path android:fillColor="#6842B8" android:pathData="M40.5,35 A2.5,2.5 0,1 0,45.5,35 A2.5,2.5 0,1 0,40.5,35" />
    <path android:fillColor="#6842B8" android:pathData="M65.5,32 A2.5,2.5 0,1 0,70.5,32 A2.5,2.5 0,1 0,65.5,32" />
    <path android:fillColor="#6842B8" android:pathData="M72.5,58 A2.5,2.5 0,1 0,77.5,58 A2.5,2.5 0,1 0,72.5,58" />

    <!-- Regla cefalométrica corta -->
    <path android:fillColor="#B9F3E6" android:pathData="M24,30 L29,30 L29,78 L24,78 Z" />
    <path
        android:fillColor="@android:color/transparent"
        android:strokeColor="#FFFFFF"
        android:strokeWidth="1.2"
        android:strokeLineCap="round"
        android:pathData="M25,36 L28,36 M25,43 L27,43 M25,50 L28,50 M25,57 L27,57 M25,64 L28,64 M25,71 L27,71" />
</vector>
'''

monochrome = '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path android:fillColor="#000000" android:pathData="M34,75 C29,69 27,61 28,52 C26,45 28,36 34,29 C40,22 49,19 59,20 C69,21 77,27 80,36 C82,41 81,46 79,50 L87,54 L80,58 L81,63 L75,64 C73,74 67,82 58,86 C49,90 40,86 34,75 Z" />
    <path android:fillColor="#000000" android:pathData="M24,30 L29,30 L29,78 L24,78 Z" />
    <path android:fillColor="#000000" android:pathData="M40.5,35 A2.5,2.5 0,1 0,45.5,35 A2.5,2.5 0,1 0,40.5,35" />
    <path android:fillColor="#000000" android:pathData="M65.5,32 A2.5,2.5 0,1 0,70.5,32 A2.5,2.5 0,1 0,65.5,32" />
    <path android:fillColor="#000000" android:pathData="M72.5,58 A2.5,2.5 0,1 0,77.5,58 A2.5,2.5 0,1 0,72.5,58" />
</vector>
'''

legacy = '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path android:fillColor="#2C7E86" android:pathData="M20,8 L88,8 C95,8 100,13 100,20 L100,88 C100,95 95,100 88,100 L20,100 C13,100 8,95 8,88 L8,20 C8,13 13,8 20,8 Z" />
    <path android:fillColor="#FFFFFF" android:pathData="M34,75 C29,69 27,61 28,52 C26,45 28,36 34,29 C40,22 49,19 59,20 C69,21 77,27 80,36 C82,41 81,46 79,50 L87,54 L80,58 L81,63 L75,64 C73,74 67,82 58,86 C49,90 40,86 34,75 Z" />
    <path android:fillColor="#2C7E86" android:pathData="M57,37 C52,37 49,40 49,44 C49,48 52,51 57,51 C62,51 65,48 65,44 C65,40 62,37 57,37 Z" />
    <path android:fillColor="#B9F3E6" android:pathData="M72,46 L82,53 L74,55 L68,52 Z" />
    <path android:fillColor="@android:color/transparent" android:strokeColor="#B9F3E6" android:strokeWidth="2.2" android:strokeLineCap="round" android:pathData="M43,35 L68,32 M68,32 L75,58" />
    <path android:fillColor="@android:color/transparent" android:strokeColor="#FFFFFF" android:strokeWidth="1.8" android:strokeLineCap="round" android:pathData="M61,33 C64,37 67,40 69,45" />
    <path android:fillColor="#6842B8" android:pathData="M40.5,35 A2.5,2.5 0,1 0,45.5,35 A2.5,2.5 0,1 0,40.5,35" />
    <path android:fillColor="#6842B8" android:pathData="M65.5,32 A2.5,2.5 0,1 0,70.5,32 A2.5,2.5 0,1 0,65.5,32" />
    <path android:fillColor="#6842B8" android:pathData="M72.5,58 A2.5,2.5 0,1 0,77.5,58 A2.5,2.5 0,1 0,72.5,58" />
    <path android:fillColor="#B9F3E6" android:pathData="M24,30 L29,30 L29,78 L24,78 Z" />
    <path android:fillColor="@android:color/transparent" android:strokeColor="#FFFFFF" android:strokeWidth="1.2" android:strokeLineCap="round" android:pathData="M25,36 L28,36 M25,43 L27,43 M25,50 L28,50 M25,57 L27,57 M25,64 L28,64 M25,71 L27,71" />
</vector>
'''

adaptive = '''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/brand_teal" />
    <foreground android:drawable="@drawable/ic_lateral_skull_foreground" />
    <monochrome android:drawable="@drawable/ic_lateral_skull_monochrome" />
</adaptive-icon>
'''

Path('app/src/main/res/drawable/ic_lateral_skull_foreground.xml').write_text(foreground, encoding='utf-8')
Path('app/src/main/res/drawable/ic_lateral_skull_monochrome.xml').write_text(monochrome, encoding='utf-8')
Path('app/src/main/res/mipmap-anydpi/ic_launcher.xml').write_text(legacy, encoding='utf-8')
for rel in [
    'app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml',
    'app/src/main/res/mipmap-anydpi-v33/ic_launcher.xml',
]:
    icon = Path(rel)
    icon.parent.mkdir(parents=True, exist_ok=True)
    icon.write_text(adaptive, encoding='utf-8')

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

print('Steiner-only Yom análisis de lateral de cráneo transform applied with dedicated launcher icon.')
