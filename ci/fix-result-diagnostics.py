from pathlib import Path

# Partial-results reliability patch.
# The results screen and exported report must show ONLY measurements that can
# actually be calculated from the landmarks already placed. Missing/unavailable
# measurements are intentionally omitted instead of being rendered as empty or
# pending rows.

analysis = Path('app/src/main/java/com/cefalo/angulos/AnalysisActivity.java')
a = analysis.read_text(encoding='utf-8')

# Partial analysis is supported, so the calculate button should not look disabled
# merely because unrelated landmarks are still missing.
a = a.replace(
    '            btnCalculate.setAlpha(0.55f);',
    '            btnCalculate.setAlpha(placed >= 2 ? 1f : 0.55f);'
)

# Do not block all-linear modules before opening the results screen. With no
# calibration there simply will be no calculable linear measurements yet.
old_linear_only_block = '''        if (definitions.isEmpty()\n                && !linearDefinitions.isEmpty()\n                && (Double.isNaN(mmPerPixel) || mmPerPixel <= 0)) {\n            Toast.makeText(\n                    this,\n                    "Este análisis necesita calibración para obtener medidas en mm.",\n                    Toast.LENGTH_LONG\n            ).show();\n            startCalibrationFlow();\n            return;\n        }\n\n'''
if old_linear_only_block in a:
    a = a.replace(old_linear_only_block, '', 1)

# Clinical-extension names changed from legacy prefixes. Keep reference and
# interpretation lookup compatible with the new names.
a = a.replace(
    'return name.startsWith("AD1")\n                || name.startsWith("AD2")\n                || name.startsWith("AD3");',
    'return name.contains("AD1")\n                || name.contains("AD2")\n                || name.contains("AD3");'
)
a = a.replace('if (name.startsWith("AD1")) {', 'if (name.contains("AD1")) {')
a = a.replace('if (name.startsWith("AD2")) {', 'if (name.contains("AD2")) {')
a = a.replace('if (name.startsWith("AD3")) {', 'if (name.contains("AD3")) {')
a = a.replace(
    'if (name.startsWith("Faringe superior")) {',
    'if (name.startsWith("Faringe superior") || name.contains("vía aérea superior mínima")) {'
)
a = a.replace(
    'if (name.startsWith("Faringe posterior")) {',
    'if (name.startsWith("Faringe posterior") || name.contains("vía aérea inferior mínima")) {'
)
a = a.replace(
    'if (def.name.startsWith("Faringe superior")) {',
    'if (def.name.startsWith("Faringe superior") || def.name.contains("vía aérea superior mínima")) {'
)
a = a.replace(
    'if (def.name.startsWith("Faringe posterior")) {',
    'if (def.name.startsWith("Faringe posterior") || def.name.contains("vía aérea inferior mínima")) {'
)

# Count only measurements that are valid with the currently placed landmarks.
helper_anchor = '''    private void showResultsDialog() {\n'''
if 'private int countCalculableAngularResults()' not in a and helper_anchor in a:
    helpers = '''    private int countCalculableAngularResults() {\n        int count = 0;\n        for (MeasurementDefinition def : definitions) {\n            Double value = measurementView.calculate(def);\n            if (value != null && Double.isFinite(value)) count++;\n        }\n        return count;\n    }\n\n    private int countCalculableLinearResults() {\n        if (Double.isNaN(mmPerPixel) || mmPerPixel <= 0) return 0;\n\n        int count = 0;\n        for (LinearMeasurementDefinition def : linearDefinitions) {\n            Double value = calculateLinear(def);\n            if (value != null && Double.isFinite(value)) count++;\n        }\n        return count;\n    }\n\n'''
    a = a.replace(helper_anchor, helpers + helper_anchor, 1)

# Add compact counts to the results dialog so the user knows this is an
# intentionally partial report, not a failed full analysis.
intro_anchor = '''        intro.setText(\n                "Resultados calculados con los mismos puntos anatómicos. " +\n                "Puede cerrar esta ventana, desbloquear el trazado, corregir un punto y volver a calcular."\n        );'''
if intro_anchor in a:
    a = a.replace(
        intro_anchor,
        '''        final int angularResultCount = countCalculableAngularResults();\n        final int linearResultCount = countCalculableLinearResults();\n        final int totalResultCount = angularResultCount + linearResultCount;\n\n        intro.setText(\n                "Resultados disponibles con los puntos colocados: " +\n                totalResultCount +\n                ". Solo se muestran las mediciones que pueden calcularse ahora. " +\n                "Puede corregir o agregar puntos y volver a calcular."\n        );''',
        1
    )

# Angular measurements: silently omit anything that cannot yet be formed.
a = a.replace(
    '''            if (value == null) continue;\n\n            TextView row = new TextView(this);''',
    '''            if (value == null || !Double.isFinite(value)) continue;\n\n            TextView row = new TextView(this);''',
    1
)

# Show the linear section only when at least one linear result is actually
# calculable. This also removes calibration warnings from otherwise-clean partial
# reports such as S+N+A -> SNA only.
a = a.replace(
    '        if (!linearDefinitions.isEmpty()) {\n            TextView linearTitle = new TextView(this);',
    '        if (linearResultCount > 0) {\n            TextView linearTitle = new TextView(this);',
    1
)

# Once linearResultCount > 0, calibration is necessarily valid. Keep the existing
# code structure but make null/invalid values disappear instead of creating rows.
a = a.replace(
    '''                    Double value = calculateLinear(def);\n                    if (value == null) continue;''',
    '''                    Double value = calculateLinear(def);\n                    if (value == null || !Double.isFinite(value)) continue;''',
    1
)

# If no angle or linear measurement can be formed at all, show one general note
# rather than a list of every missing measurement.
no_result_anchor = '''        if ("TWEED".equals(mode)) {\n            addTweedSummary(container);\n        }\n\n        TextView saveAnnotated ='''
if no_result_anchor in a:
    a = a.replace(
        no_result_anchor,
        '''        if ("TWEED".equals(mode)) {\n            addTweedSummary(container);\n        }\n\n        if (totalResultCount == 0) {\n            TextView none = new TextView(this);\n            none.setText("Aún no hay una medición completa con los puntos colocados. Agregue los landmarks necesarios y vuelva a calcular.");\n            none.setTextSize(13.5f);\n            none.setTextColor(getColor(R.color.text_primary));\n            none.setGravity(Gravity.CENTER);\n            none.setTextAlignment(android.view.View.TEXT_ALIGNMENT_CENTER);\n            none.setBackgroundResource(R.drawable.card_white);\n            none.setPadding(dp(14), dp(12), dp(14), dp(12));\n            container.addView(none);\n        }\n\n        TextView saveAnnotated =''',
        1
    )

# Exported PNG/PDF report: size the document from calculable results only. This
# prevents large blank spaces caused by definitions whose landmarks were not set.
old_report_count = '''        int linearCount =\n                (!linearDefinitions.isEmpty()\n                        && !Double.isNaN(mmPerPixel)\n                        && mmPerPixel > 0)\n                        ? linearDefinitions.size()\n                        : 0;'''
new_report_count = '''        int angularCount = countCalculableAngularResults();\n        int linearCount = countCalculableLinearResults();'''
if old_report_count in a:
    a = a.replace(old_report_count, new_report_count, 1)

a = a.replace(
    '                ((definitions.size() + linearCount) * rowHeight) +',
    '                ((angularCount + linearCount) * rowHeight) +',
    1
)

a = a.replace(
    '''        if (!linearDefinitions.isEmpty()\n                && !Double.isNaN(mmPerPixel)\n                && mmPerPixel > 0) {\n            canvas.drawText(''',
    '''        if (linearCount > 0) {\n            canvas.drawText(''',
    1
)

# Report rows also skip non-finite geometry.
a = a.replace(
    '''            Double value = measurementView.calculate(def);\n            if (value == null) continue;''',
    '''            Double value = measurementView.calculate(def);\n            if (value == null || !Double.isFinite(value)) continue;''',
    1
)

a = a.replace(
    '''        if (!linearDefinitions.isEmpty()\n                && !Double.isNaN(mmPerPixel)\n                && mmPerPixel > 0) {\n            y += 45;''',
    '''        if (linearCount > 0) {\n            y += 45;''',
    1
)

a = a.replace(
    '''                Double value = calculateLinear(def);\n                if (value == null) continue;''',
    '''                Double value = calculateLinear(def);\n                if (value == null || !Double.isFinite(value)) continue;''',
    1
)

analysis.write_text(a, encoding='utf-8')

# Degenerate angular geometry is not a real 0-degree measurement. It is omitted
# from partial reports until the points form a valid angle.
view = Path('app/src/main/java/com/cefalo/angulos/MeasurementView.java')
v = view.read_text(encoding='utf-8')
v = v.replace(
    '        if (m1 == 0 || m2 == 0) return 0;',
    '        if (m1 == 0 || m2 == 0) return Double.NaN;'
)
view.write_text(v, encoding='utf-8')

# Build-time assertions guard the requested UX.
prepared = analysis.read_text(encoding='utf-8')
assert 'countCalculableAngularResults()' in prepared
assert 'countCalculableLinearResults()' in prepared
assert 'PENDIENTE / NO CALCULADO' not in prepared
assert '((angularCount + linearCount) * rowHeight)' in prepared

print('Partial-results-only patch applied.')
