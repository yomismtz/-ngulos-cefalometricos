from pathlib import Path

path = Path('app/src/main/java/com/cefalo/angulos/AnalysisActivity.java')
s = path.read_text(encoding='utf-8')

bad = '''help.setText("Punto: " + measurementView.getCurrentLabel() +
                "
El paso se expresa en píxeles de la imagen y no cambia con el zoom.");'''
good = '''help.setText("Punto: " + measurementView.getCurrentLabel() +
                "\\nEl paso se expresa en píxeles de la imagen y no cambia con el zoom.");'''

if bad not in s:
    raise RuntimeError('Generated fine-adjust help string pattern was not found')

path.write_text(s.replace(bad, good, 1), encoding='utf-8')
print('Generated fine-adjust Java string corrected.')
