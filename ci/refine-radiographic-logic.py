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

# Keep the small labelsUpdater declaration until the final integrity pass.
# The final pass replaces the full Nolla selector block (including this line)
# with explicit "Seleccione" placeholders. Removing it here made the safety
# patch depend on a missing textual anchor.

cvm_anchor = '''        addSmallText("Observe solamente C2, C3 y C4. Marque «presente» solo cuando la concavidad inferior sea clara.");\n'''
if 'CvmStageGuideView stageGuide' not in a and cvm_anchor in a:
    cvm_visual = '''        addSmallText("Observe solamente C2, C3 y C4. Marque «presente» solo cuando la concavidad inferior sea clara.");\n\n        CvmStageGuideView stageGuide = new CvmStageGuideView(this);\n        LinearLayout.LayoutParams stageGuideLp = new LinearLayout.LayoutParams(\n                ViewGroup.LayoutParams.MATCH_PARENT,\n                dp(325)\n        );\n        stageGuideLp.setMargins(0, dp(4), 0, dp(10));\n        content.addView(stageGuide, stageGuideLp);\n'''
    a = a.replace(cvm_anchor, cvm_visual, 1)

activity.write_text(a, encoding='utf-8')

print('Radiographic assessment logic and CVM visual guide refined.')
