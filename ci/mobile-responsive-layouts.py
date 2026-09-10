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
print('Dedicated tablet two-column tracing layout generated.')
