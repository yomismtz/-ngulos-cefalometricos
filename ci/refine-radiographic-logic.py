from pathlib import Path

logic = Path('app/src/main/java/com/cefalo/angulos/RadiographicAssessmentLogic.java')
s = logic.read_text(encoding='utf-8')

old_cs5 = '''        if (c2Concave && c3Concave && c4Concave
                && (c3Shape == VertebralShape.SQUARE || c4Shape == VertebralShape.SQUARE)
                && c3Shape != VertebralShape.RECTANGULAR_VERTICAL
                && c4Shape != VertebralShape.RECTANGULAR_VERTICAL) {
'''
new_cs5 = '''        if (c2Concave && c3Concave && c4Concave
                && (c3Shape == VertebralShape.SQUARE || c4Shape == VertebralShape.SQUARE)
                && isOneOf(c3Shape, VertebralShape.SQUARE, VertebralShape.RECTANGULAR_HORIZONTAL)
                && isOneOf(c4Shape, VertebralShape.SQUARE, VertebralShape.RECTANGULAR_HORIZONTAL)) {
'''
if old_cs5 in s:
    s = s.replace(old_cs5, new_cs5, 1)

old_cs6 = '''        if (c2Concave && c3Concave && c4Concave
                && (c3Shape == VertebralShape.RECTANGULAR_VERTICAL
                || c4Shape == VertebralShape.RECTANGULAR_VERTICAL)) {
'''
new_cs6 = '''        if (c2Concave && c3Concave && c4Concave
                && (c3Shape == VertebralShape.RECTANGULAR_VERTICAL
                || c4Shape == VertebralShape.RECTANGULAR_VERTICAL)
                && isOneOf(c3Shape, VertebralShape.RECTANGULAR_VERTICAL, VertebralShape.SQUARE)
                && isOneOf(c4Shape, VertebralShape.RECTANGULAR_VERTICAL, VertebralShape.SQUARE)) {
'''
if old_cs6 in s:
    s = s.replace(old_cs6, new_cs6, 1)

logic.write_text(s, encoding='utf-8')

activity = Path('app/src/main/java/com/cefalo/angulos/RadiographicAssessmentActivity.java')
a = activity.read_text(encoding='utf-8')
a = a.replace('''        View.OnClickListener labelsUpdater = v -> updateNollaLabels();\n''', '')
activity.write_text(a, encoding='utf-8')

print('Radiographic assessment logic refined.')
