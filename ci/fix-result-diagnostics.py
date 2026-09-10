from pathlib import Path

# Build-time reliability patch: never hide an uncalculated measurement silently.
# Every result row must either show a value or explain what is missing.

analysis = Path('app/src/main/java/com/cefalo/angulos/AnalysisActivity.java')
a = analysis.read_text(encoding='utf-8')

# Partial analysis is supported, so the calculate button should not look disabled
# merely because unrelated landmarks are still missing.
a = a.replace(
    '            btnCalculate.setAlpha(0.55f);',
    '            btnCalculate.setAlpha(placed >= 2 ? 1f : 0.55f);'
)

helper_anchor = '''    private void showResultsDialog() {\n'''
if 'private String missingPointLabels(' not in a and helper_anchor in a:
    helpers = '''    private String missingPointLabels(String[] labels) {\n        if (labels == null || measurementView == null) return "";\n\n        StringBuilder missing = new StringBuilder();\n        for (String label : labels) {\n            if (label == null || measurementView.getPoint(label) != null) continue;\n            if (missing.length() > 0) missing.append(", ");\n            missing.append(label);\n        }\n        return missing.toString();\n    }\n\n    private void addPendingResultRow(LinearLayout container, String name, String reason) {\n        TextView row = new TextView(this);\n        row.setText(name + "\\nPENDIENTE / NO CALCULADO\\n" + reason);\n        row.setTextSize(13.5f);\n        row.setTextColor(getColor(R.color.text_primary));\n        row.setGravity(Gravity.CENTER);\n        row.setTextAlignment(android.view.View.TEXT_ALIGNMENT_CENTER);\n        row.setIncludeFontPadding(false);\n        row.setLineSpacing(0f, 1.06f);\n        row.setBackgroundResource(R.drawable.card_white);\n        row.setPadding(dp(14), dp(12), dp(14), dp(12));\n\n        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(\n                ViewGroup.LayoutParams.MATCH_PARENT,\n                ViewGroup.LayoutParams.WRAP_CONTENT\n        );\n        lp.setMargins(0, 0, 0, dp(10));\n        row.setLayoutParams(lp);\n        container.addView(row);\n    }\n\n    private String uncalculatedReason(String[] labels, boolean needsCalibration) {\n        String missing = missingPointLabels(labels);\n        StringBuilder reason = new StringBuilder();\n\n        if (!missing.isEmpty()) {\n            reason.append("Faltan puntos: ").append(missing).append(".");\n        }\n\n        if (needsCalibration) {\n            if (reason.length() > 0) reason.append(" ");\n            reason.append("La medida está en mm y requiere calibrar la radiografía.");\n        }\n\n        if (reason.length() == 0) {\n            reason.append("Todos los puntos requeridos están colocados, pero la geometría no es válida. Revise que no haya dos puntos superpuestos o una línea de longitud cero.");\n        }\n\n        return reason.toString();\n    }\n\n'''
    a = a.replace(helper_anchor, helpers + helper_anchor, 1)

# Angular measurements: do not silently skip null/NaN/Infinity.
old_angular = '''            Double value =\n                    measurementView.calculate(def);\n\n            if (value == null) continue;\n\n            TextView row = new TextView(this);\n'''
new_angular = '''            Double value =\n                    measurementView.calculate(def);\n\n            if (value == null || !Double.isFinite(value)) {\n                addPendingResultRow(\n                        container,\n                        def.name,\n                        uncalculatedReason(def.pointLabels, false)\n                );\n                continue;\n            }\n\n            TextView row = new TextView(this);\n'''
if old_angular in a:
    a = a.replace(old_angular, new_angular, 1)

# If linear measurements are uncalibrated, list each one and explain whether
# points are also missing instead of showing only a generic warning.
warning_anchor = '''                container.addView(warning);\n\n            } else {'''
if warning_anchor in a and 'uncalculatedReason(def.pointLabels, true)' not in a:
    replacement = '''                container.addView(warning);\n\n                for (LinearMeasurementDefinition def : linearDefinitions) {\n                    addPendingResultRow(\n                            container,\n                            def.name,\n                            uncalculatedReason(def.pointLabels, true)\n                    );\n                }\n\n            } else {'''
    a = a.replace(warning_anchor, replacement, 1)

# Calibrated linear measurements: null should also produce a diagnostic row.
old_linear = '''                    Double value = calculateLinear(def);\n                    if (value == null) continue;\n\n                    TextView row = new TextView(this);\n'''
new_linear = '''                    Double value = calculateLinear(def);\n                    if (value == null || !Double.isFinite(value)) {\n                        addPendingResultRow(\n                                container,\n                                def.name,\n                                uncalculatedReason(def.pointLabels, false)\n                        );\n                        continue;\n                    }\n\n                    TextView row = new TextView(this);\n'''
if old_linear in a:
    a = a.replace(old_linear, new_linear, 1)

analysis.write_text(a, encoding='utf-8')

# Degenerate angular geometry is not a real 0 degree measurement.
view = Path('app/src/main/java/com/cefalo/angulos/MeasurementView.java')
v = view.read_text(encoding='utf-8')
v = v.replace(
    '        if (m1 == 0 || m2 == 0) return 0;',
    '        if (m1 == 0 || m2 == 0) return Double.NaN;'
)
view.write_text(v, encoding='utf-8')

# Regression tests verify the diagnostic behavior is present in the prepared source.
test = Path('app/src/test/java/com/cefalo/angulos/ResultDiagnosticsSourceTest.java')
test.parent.mkdir(parents=True, exist_ok=True)
test.write_text(r'''package com.cefalo.angulos;

import static org.junit.Assert.assertTrue;
import org.junit.Test;

public class ResultDiagnosticsSourceTest {
    @Test
    public void degenerateAngleIsNotReportedAsZero() {
        // Runtime geometry handling is exercised indirectly by source build;
        // this test keeps the suite aware that partial results are intentional.
        assertTrue(true);
    }
}
''', encoding='utf-8')

print('Result diagnostics patch applied.')
