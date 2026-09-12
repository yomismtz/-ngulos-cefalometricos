from pathlib import Path
import subprocess
import sys

subprocess.run([sys.executable, 'ci/prepare-steiner-only.py'], check=True)

path = Path('app/build.gradle')
text = path.read_text(encoding='utf-8')
text = text.replace("applicationId 'yom.Analisis'", "applicationId 'com.yomceph.cefalometrico'", 1)
path.write_text(text, encoding='utf-8')

if "applicationId 'com.yomceph.cefalometrico'" not in path.read_text(encoding='utf-8'):
    raise RuntimeError('Could not set Steiner package')

print('Steiner package: com.yomceph.cefalometrico')
