from pathlib import Path

land = Path('app/src/main/res/layout-land/activity_analysis.xml')
tablet = Path('app/src/main/res/layout-sw600dp/activity_analysis.xml')
if not land.exists():
    raise RuntimeError('Landscape tracing layout is missing')

s = land.read_text(encoding='utf-8')
# Tablet keeps the radiograph on the left and gives the right-side controls
# more room than a phone in landscape.
s = s.replace('android:layout_width="250dp"', 'android:layout_width="360dp"', 1)
s = s.replace('android:textSize="9sp" android:textColor="@color/text_primary"',
              'android:textSize="10.5sp" android:textColor="@color/text_primary"', 1)
tablet.parent.mkdir(parents=True, exist_ok=True)
tablet.write_text(s, encoding='utf-8')

# mobile-fine-adjust.py writes a human-readable line break into its generated
# Java template. Normalize it to a Java escape sequence before compilation.
activity = Path('app/src/main/java/com/cefalo/angulos/AnalysisActivity.java')
a = activity.read_text(encoding='utf-8')
bad = '''help.setText("Punto: " + measurementView.getCurrentLabel() +
                "
El paso se expresa en píxeles de la imagen y no cambia con el zoom.");'''
good = '''help.setText("Punto: " + measurementView.getCurrentLabel() +
                "\\nEl paso se expresa en píxeles de la imagen y no cambia con el zoom.");'''
if bad in a:
    a = a.replace(bad, good, 1)
activity.write_text(a, encoding='utf-8')

# Keep the new radiographic home strings complete in English so Lint can verify
# both language sets. These are generated earlier by final-radiographic-audit.py.
en = Path('app/src/main/res/values-en/strings.xml')
if en.exists():
    e = en.read_text(encoding='utf-8')
    translations = {
        'section_lateral': 'LATERAL SKULL RADIOGRAPH',
        'section_panoramic': 'PANORAMIC RADIOGRAPH',
        'analysis_cvm': 'CERVICAL MATURATION · C2–C4 · CS1–CS6',
        'analysis_nolla': 'DENTAL DEVELOPMENT · NOLLA',
        'analysis_resorption': 'PRIMARY ROOT RESORPTION',
        'analysis_panoramic_review': 'COMPREHENSIVE PANORAMIC REVIEW',
    }
    additions = []
    for key, value in translations.items():
        if f'name="{key}"' not in e:
            additions.append(f'    <string name="{key}">{value}</string>')
    if additions:
        e = e.replace('</resources>', '\n'.join(additions) + '\n</resources>')
    en.write_text(e, encoding='utf-8')

# Android Lint rejects passing a masked integer that may evaluate to 0 into
# takePersistableUriPermission(). The app only needs persistent READ access, so
# call the API with the explicit allowed constant when the provider granted it.
assessment = Path('app/src/main/java/com/cefalo/angulos/RadiographicAssessmentActivity.java')
if assessment.exists():
    r = assessment.read_text(encoding='utf-8')
    old = '''        try {
            int flags = data.getFlags() & (Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
            getContentResolver().takePersistableUriPermission(uri, flags & Intent.FLAG_GRANT_READ_URI_PERMISSION);
        } catch (Exception ignored) {'''
    new = '''        try {
            int flags = data.getFlags();
            if ((flags & Intent.FLAG_GRANT_READ_URI_PERMISSION) == Intent.FLAG_GRANT_READ_URI_PERMISSION) {
                getContentResolver().takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION);
            }
        } catch (Exception ignored) {'''
    if old in r:
        r = r.replace(old, new, 1)
    assessment.write_text(r, encoding='utf-8')

# Distinct installable build after the per-app launcher identity revision.
gradle = Path('app/build.gradle')
if gradle.exists():
    g = gradle.read_text(encoding='utf-8')
    g = g.replace('versionCode 26', 'versionCode 28', 1)
    g = g.replace("versionName '1.25'", "versionName '1.27'", 1)
    gradle.write_text(g, encoding='utf-8')

# Apply the final phone/tablet navigation pass after all layouts above exist.
navigation = Path('ci/mobile-radiograph-navigation.py')
if navigation.exists():
    namespace = {'__name__': '__main__'}
    exec(compile(navigation.read_text(encoding='utf-8'), str(navigation), 'exec'), namespace)

# The vertical SeekBar needs a post-navigation correction because its custom
# touch handler changes progress programmatically. This pass also compacts the
# landmark buttons and advances the UI build to 1.28.
vertical_fix = Path('ci/fix-vertical-pan-and-compact-points.py')
if vertical_fix.exists():
    namespace = {'__name__': '__main__'}
    exec(compile(vertical_fix.read_text(encoding='utf-8'), str(vertical_fix), 'exec'), namespace)

# Final adaptive pass: small/medium/large phones, 7–10+ inch tablets,
# low-RAM image policy, indexed offline study database and in-app PDF viewer.
adaptive = Path('ci/adaptive-device-db-pdf.py')
if adaptive.exists():
    namespace = {'__name__': '__main__'}
    exec(compile(adaptive.read_text(encoding='utf-8'), str(adaptive), 'exec'), namespace)

# Embed the project owner's exact Nolla radiographic reference in the complete
# application. Students can open it from Nolla, zoom/pan it, return, and enter
# the observed stages into the existing analysis form.
nolla_reference = Path('ci/integrate-nolla-reference.py')
if nolla_reference.exists():
    namespace = {'__name__': '__main__'}
    exec(compile(nolla_reference.read_text(encoding='utf-8'), str(nolla_reference), 'exec'), namespace)

# Add literature-verified complementary cephalometric/craniocervical angles and
# CVM age-reference context. This runs after all earlier catalog/UI generators.
complementary = Path('ci/add-complementary-ceph-cvm-age.py')
if complementary.exists():
    namespace = {'__name__': '__main__'}
    exec(compile(complementary.read_text(encoding='utf-8'), str(complementary), 'exec'), namespace)

print('Responsive phone/tablet layouts, corrected navigation, local database, PDF viewer, Nolla image, complementary cephalometric angles, and CVM age-reference context applied; build version set to 1.31.')
