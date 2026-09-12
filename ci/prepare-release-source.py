from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(script: str) -> None:
    path = ROOT / 'ci' / script
    if not path.exists():
        raise RuntimeError(f'Missing generation step: {path}')
    print(f'\n=== {script} ===', flush=True)
    subprocess.run([sys.executable, str(path)], cwd=ROOT, check=True)


def normalize_tangent_help() -> None:
    path = ROOT / 'app/src/main/java/com/cefalo/angulos/PointGuide.java'
    text = path.read_text(encoding='utf-8')
    replacements = {
        'GUIDE.put("Go", "Gonion (Go): punto construido sobre el ángulo mandibular, en la bisectriz formada por la tangente al borde posterior de la rama y la tangente al borde inferior del cuerpo mandibular.");':
            'GUIDE.put("Go", "Gonion (Go): punto construido sobre el ángulo mandibular. Para construirlo geométricamente trace 2 tangentes: una al borde posterior de la rama y otra al borde inferior del cuerpo mandibular. Cada tangente se define con 2 puntos de apoyo/contacto sobre su contorno; después se obtiene la bisectriz del ángulo formado por ambas tangentes y se localiza Go según el protocolo cefalométrico.");',
        'GUIDE.put("CVT sup.", "CVT superior (etiqueta heredada): corresponde a CV2tg, punto de tangencia superoposterior de la odontoides de C2.");':
            'GUIDE.put("CVT sup.", "CVT superior (etiqueta heredada): corresponde a CV2tg. Es un landmark, no una tangente completa. En el protocolo adoptado, CVT se forma con 2 puntos: CV2tg + CV4ip.");',
        'GUIDE.put("CVT inf.", "CVT inferior (etiqueta heredada): corresponde a CV4ip, punto más inferoposterior del cuerpo de C4.");':
            'GUIDE.put("CVT inf.", "CVT inferior (etiqueta heredada): corresponde a CV4ip, segundo landmark de CVT. La línea CVT se forma con 2 puntos: CV2tg + CV4ip.");',
        'GUIDE.put("OPT sup.", "OPT superior (etiqueta heredada): corresponde a CV2tg, punto de tangencia superoposterior de la odontoides de C2.");':
            'GUIDE.put("OPT sup.", "OPT superior (etiqueta heredada): corresponde a CV2tg. Es un landmark, no una tangente completa. OPT se forma con 2 puntos: CV2tg + CV2ip.");',
        'GUIDE.put("OPT inf.", "OPT inferior (etiqueta heredada): corresponde a CV2ip, punto más inferoposterior del cuerpo de C2.");':
            'GUIDE.put("OPT inf.", "OPT inferior (etiqueta heredada): corresponde a CV2ip, segundo landmark de OPT. La línea OPT se forma con 2 puntos: CV2tg + CV2ip.");',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    path.write_text(text, encoding='utf-8')
    print('\n=== tangent help normalized ===', flush=True)


def verify_final_source() -> None:
    activity = (ROOT / 'app/src/main/java/com/cefalo/angulos/RadiographicAssessmentActivity.java').read_text(encoding='utf-8')
    store = (ROOT / 'app/src/main/java/com/cefalo/angulos/SavedStudyStore.java').read_text(encoding='utf-8')
    database = (ROOT / 'app/src/main/java/com/cefalo/angulos/StudyDatabase.java').read_text(encoding='utf-8')
    gradle = (ROOT / 'app/build.gradle').read_text(encoding='utf-8')

    checks = {
        'explicit CVM selection': 'AssessmentInputValidator.cvmSelectionsComplete' in activity,
        'explicit Nolla selection': 'AssessmentInputValidator.nollaSelectionsComplete' in activity,
        'explicit resorption selection': 'AssessmentInputValidator.resorptionSelectionsComplete' in activity,
        'panoramic no-findings confirmation': 'PANO_NO_FINDINGS' in activity,
        'CVM reference state': 'CVM_SEX' in activity,
        'radiograph requirement': 'private boolean requireRadiograph()' in activity,
        'mirrored EXIF': 'exif.isFlipped()' in activity,
        'checked SQLite save': 'boolean databaseSaved = StudyDatabase.save' in store,
        'SQLite boolean save': 'public static boolean save(Context context' in database,
        'schema version': 'SCHEMA_VERSION = 2' in store,
        'v1.34': "versionName '1.34'" in gradle,
        'versionCode 35': 'versionCode 35' in gradle,
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError('Generated source verification failed: ' + ', '.join(missing))


# Order is part of the build contract. Each step operates on the output of the
# preceding one; running this single file reproduces the exact source CI builds.
run('prepare-test-build.py')
normalize_tangent_help()
run('extend-clinical-build.py')
run('augment-mcgregor-guide.py')
run('fix-result-diagnostics.py')
run('final-radiographic-audit.py')
run('refine-radiographic-logic.py')
run('mobile-brand-calibration.py')
run('mobile-fine-adjust.py')
run('mobile-guide-polish.py')
run('patch-adaptive-store-compat.py')
run('mobile-responsive-layouts.py')
run('full-app-basic-steiner.py')
run('add-carpal-fishman.py')
run('audit-integrity-fixes.py')
run('post-generation-safety.py')
verify_final_source()

print('\nRelease source generation completed and verified: YOM 1.34 (35).', flush=True)
