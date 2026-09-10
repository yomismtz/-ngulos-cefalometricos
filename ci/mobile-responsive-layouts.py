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

print('Dedicated tablet layout generated and mobile Java template normalized.')
