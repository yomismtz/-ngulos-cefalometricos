from pathlib import Path

TARGET_PACKAGE = 'yom.Analisis'
BASE_PACKAGE = 'com.yomceph.app'

gradle_path = Path('app/build.gradle')
text = gradle_path.read_text(encoding='utf-8')

old = f"applicationId '{BASE_PACKAGE}'"
new = f"applicationId '{TARGET_PACKAGE}'"

if old not in text and new not in text:
    raise RuntimeError('Could not locate Radiográficos applicationId in app/build.gradle')

text = text.replace(old, new, 1)
gradle_path.write_text(text, encoding='utf-8')

final_text = gradle_path.read_text(encoding='utf-8')
if new not in final_text:
    raise RuntimeError(f'Google Play package was not set to {TARGET_PACKAGE}')

print(f'Radiográficos Google Play package: {TARGET_PACKAGE}')
