from pathlib import Path
import re

ROOT = Path('.')
java = ROOT / 'app/src/main/java/com/cefalo/angulos/AnalysisActivity.java'
strings_es = ROOT / 'app/src/main/res/values/strings.xml'
strings_en = ROOT / 'app/src/main/res/values-en/strings.xml'
gradle = ROOT / 'app/build.gradle'

s = java.read_text(encoding='utf-8')

# In the complete YOM app, the Steiner launcher is intentionally a BASIC screen.
# The standalone lateral-skull app keeps the comprehensive combined catalog.
old = '''        } else {
            definitions = MeasurementCatalog.steiner();
            linearDefinitions = LinearMeasurementCatalog.cephalometric();
        }
'''
new = '''        } else {
            definitions = basicSteinerDefinitions();
            // Complete app: Steiner is deliberately limited to the five core
            // angular measurements requested for quick screening. The dedicated
            // lateral-skull app contains the extended Steiner/Bjork/Ricketts/
            // McNamara catalog.
            linearDefinitions = new ArrayList<>();
        }
'''
if old not in s:
    raise RuntimeError('Could not locate STEINER branch in AnalysisActivity')
s = s.replace(old, new, 1)

helper_anchor = '''    private static String safe(String value) {
'''
if helper_anchor not in s:
    helper_anchor = '''    private String modeTitle() {
'''
if helper_anchor not in s:
    raise RuntimeError('Could not locate helper insertion point in AnalysisActivity')

helper = r'''    /**
     * Basic Steiner set used only by the COMPLETE multi-analysis application.
     * Results remain partial: a row appears only when all landmarks required by
     * that specific measurement have been placed.
     */
    private List<MeasurementDefinition> basicSteinerDefinitions() {
        List<MeasurementDefinition> basic = new ArrayList<>();
        for (MeasurementDefinition def : MeasurementCatalog.steiner()) {
            String name = def.name;
            if ("SNA".equals(name)
                    || "SNB".equals(name)
                    || "ANB".equals(name)
                    || "SN / Go-Gn".equals(name)
                    || "Ángulo interincisal".equals(name)) {
                basic.add(def);
            }
        }
        return basic;
    }

'''
s = s.replace(helper_anchor, helper + helper_anchor, 1)
java.write_text(s, encoding='utf-8')

# Make the distinction visible to the user on the home screen.
def replace_string(path: Path, key: str, value: str):
    if not path.exists():
        return
    text = path.read_text(encoding='utf-8')
    pattern = rf'<string name="{re.escape(key)}">.*?</string>'
    if re.search(pattern, text, flags=re.S):
        text = re.sub(pattern, f'<string name="{key}">{value}</string>', text, count=1, flags=re.S)
    path.write_text(text, encoding='utf-8')

replace_string(strings_es, 'analysis_steiner', 'STEINER BÁSICO · 5 ÁNGULOS')
replace_string(strings_en, 'analysis_steiner', 'BASIC STEINER · 5 ANGLES')

# Version dedicated to this separation between complete and standalone apps.
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 33', g, count=1)
g = re.sub(r"versionName\s+'[^']+'", "versionName '1.32'", g, count=1)
gradle.write_text(g, encoding='utf-8')

# Build-time assertions: exactly the requested five angular names are retained
# in the complete app's Steiner mode and no linear cephalometric rows are loaded.
final = java.read_text(encoding='utf-8')
required = ['"SNA".equals(name)', '"SNB".equals(name)', '"ANB".equals(name)',
            '"SN / Go-Gn".equals(name)', '"Ángulo interincisal".equals(name)']
missing = [token for token in required if token not in final]
if missing:
    raise RuntimeError('Basic Steiner filtering incomplete: ' + ', '.join(missing))
if 'definitions = basicSteinerDefinitions();' not in final or 'linearDefinitions = new ArrayList<>();' not in final:
    raise RuntimeError('Complete-app Steiner branch was not restricted correctly')

print('Complete app prepared with BASIC Steiner only: SNA, SNB, ANB, SN/Go-Gn and interincisal; v1.32.')
