from pathlib import Path
import re

# Branding shared by the complete and Steiner-only builds.
for rel in ['app/src/main/res/values/strings.xml', 'app/src/main/res/values-en/strings.xml']:
    path = Path(rel)
    if not path.exists():
        continue
    s = path.read_text(encoding='utf-8')
    s = re.sub(r'<string name="app_name">.*?</string>', '<string name="app_name">Yom Análisis Radiográficos</string>', s)
    if 'values-en' in rel:
        s = re.sub(r'<string name="app_slogan">.*?</string>', '<string name="app_slogan">Cephalometrics and radiographic analysis</string>', s)
    else:
        s = re.sub(r'<string name="app_slogan">.*?</string>', '<string name="app_slogan">Cefalometría y análisis radiográfico</string>', s)
    if 'name="verify_calibration"' not in s:
        s = s.replace('</resources>',
            '    <string name="verify_calibration">VERIFICAR</string>\n'
            '    <string name="where_is_point">¿DÓNDE ESTÁ?</string>\n'
            '    <string name="fine_adjust">🎯 AJUSTE FINO</string>\n'
            '</resources>')
    path.write_text(s, encoding='utf-8')

# Distinct build version for this mobile polish.
gradle = Path('app/build.gradle')
if gradle.exists():
    g = gradle.read_text(encoding='utf-8')
    g = re.sub(r'versionCode\s+\d+', 'versionCode 25', g, count=1)
    g = re.sub(r"versionName\s+'[^']+'", "versionName '1.24'", g, count=1)
    gradle.write_text(g, encoding='utf-8')

# Portrait layout: add a separate calibration verification action and a visible
# "¿Dónde está?" button. Angle-only modules keep calibrationRow hidden.
layout = Path('app/src/main/res/layout/activity_analysis.xml')
x = layout.read_text(encoding='utf-8')
x = x.replace('android:id="@+id/btnCalibrate"\n            android:layout_width="108dp"',
              'android:id="@+id/btnCalibrate"\n            android:layout_width="92dp"')
if '@+id/btnVerifyCalibration' not in x:
    marker = '''        <TextView
            android:id="@+id/btnCalibrate"'''
    start = x.find(marker)
    if start != -1:
        end = x.find('/>', start)
        if end != -1:
            end += 2
            verify = '''

        <TextView
            android:id="@+id/btnVerifyCalibration"
            android:layout_width="88dp"
            android:layout_height="48dp"
            android:layout_marginLeft="4dp"
            android:gravity="center"
            android:textAlignment="center"
            android:includeFontPadding="false"
            android:text="@string/verify_calibration"
            android:textStyle="bold"
            android:textSize="9.5sp"
            android:textColor="@color/brand_purple"
            android:background="@drawable/button_soft_purple_centered"
            android:clickable="true"
            android:focusable="true" />'''
            x = x[:end] + verify + x[end:]

if '@+id/btnWhereIs' not in x:
    pattern = re.compile(r'''    <TextView
        android:id="@\+id/txtInstruction".*?
        android:paddingBottom="4dp" />''', re.S)
    m = pattern.search(x)
    if m:
        row = '''    <LinearLayout
        android:id="@+id/helpRow"
        android:layout_width="match_parent"
        android:layout_height="56dp"
        android:orientation="horizontal"
        android:gravity="center_vertical"
        android:layout_marginLeft="8dp"
        android:layout_marginRight="8dp">

        <TextView
            android:id="@+id/txtInstruction"
            android:layout_width="0dp"
            android:layout_height="52dp"
            android:layout_weight="1"
            android:background="@drawable/card_point_help"
            android:text="@string/instruction_placeholder"
            android:textSize="10.5sp"
            android:textColor="@color/text_primary"
            android:gravity="center"
            android:textAlignment="center"
            android:includeFontPadding="false"
            android:maxLines="2"
            android:ellipsize="end"
            android:clickable="true"
            android:focusable="true"
            android:paddingLeft="8dp"
            android:paddingRight="8dp" />

        <TextView
            android:id="@+id/btnWhereIs"
            android:layout_width="92dp"
            android:layout_height="48dp"
            android:layout_marginLeft="5dp"
            android:gravity="center"
            android:textAlignment="center"
            android:includeFontPadding="false"
            android:text="@string/where_is_point"
            android:textStyle="bold"
            android:textSize="9.5sp"
            android:textColor="@color/mint_text"
            android:background="@drawable/button_soft_mint_centered"
            android:clickable="true"
            android:focusable="true" />
    </LinearLayout>'''
        x = x[:m.start()] + row + x[m.end():]
x = x.replace('android:text="🎯 AJUSTE FINO"', 'android:text="@string/fine_adjust"')
layout.write_text(x, encoding='utf-8')

activity = Path('app/src/main/java/com/cefalo/angulos/AnalysisActivity.java')
a = activity.read_text(encoding='utf-8')

# Hook new actions after the standard calibration action.
anchor = '        btnCalibrate.setOnClickListener(v -> startCalibrationFlow());\n'
if anchor in a and 'startCalibrationVerification()' not in a:
    a = a.replace(anchor, anchor + '''
        View btnVerifyCalibration = findViewById(R.id.btnVerifyCalibration);
        if (btnVerifyCalibration != null) {
            btnVerifyCalibration.setOnClickListener(v -> startCalibrationVerification());
        }

        View btnWhereIs = findViewById(R.id.btnWhereIs);
        if (btnWhereIs != null) {
            btnWhereIs.setOnClickListener(v -> showCurrentPointGuide());
        }
''', 1)

# Keep all static labels centered on every layout variant.
a = a.replace('                R.id.btnCalibrate,\n',
              '                R.id.btnCalibrate,\n                R.id.btnVerifyCalibration,\n', 1)
a = a.replace('                R.id.txtInstruction,\n',
              '                R.id.txtInstruction,\n                R.id.btnWhereIs,\n', 1)

# Calibration status now exposes the actual conversion factor.
status = re.compile(r'''    private void updateCalibrationStatus\(\) \{.*?\n    \}\n\n(?=    private )''', re.S)
m = status.search(a)
if m:
    replacement = '''    private void updateCalibrationStatus() {
        if (txtCalibration == null) return;

        View verify = findViewById(R.id.btnVerifyCalibration);
        boolean calibrated = !Double.isNaN(mmPerPixel) && mmPerPixel > 0.0;
        if (!calibrated) {
            txtCalibration.setText("SIN CALIBRAR · marque 2 extremos de una referencia conocida");
            if (btnCalibrate != null) btnCalibrate.setText("CALIBRAR");
            if (verify != null) {
                verify.setEnabled(false);
                verify.setAlpha(0.45f);
            }
            return;
        }

        String label = calibrationLabel == null ? "" : calibrationLabel.trim();
        String numeric = String.format(Locale.US, "%.6f mm/px", mmPerPixel);
        txtCalibration.setText(label.isEmpty() ? numeric : label + " · " + numeric);
        if (btnCalibrate != null) btnCalibrate.setText("RECALIBRAR");
        if (verify != null) {
            verify.setEnabled(true);
            verify.setAlpha(1f);
        }
    }

'''
    a = a[:m.start()] + replacement + a[m.end():]

# Verification reuses the same two-point calibration overlay, but compares the
# active scale against a second known length. No arbitrary pass/fail threshold.
verify_anchor = '    private void updateCalibrationStatus() {'
if 'private void startCalibrationVerification()' not in a and verify_anchor in a:
    methods = '''    private void startCalibrationVerification() {
        if (measurementView == null || Double.isNaN(mmPerPixel) || mmPerPixel <= 0.0) {
            Toast.makeText(this, "Calibre primero la radiografía.", Toast.LENGTH_SHORT).show();
            return;
        }
        new AlertDialog.Builder(this)
                .setTitle("Verificar calibración")
                .setMessage("Marque nuevamente los dos extremos de una distancia conocida. Después introduzca su longitud real. La app comparará lo esperado con lo medido sin imponer un umbral clínico arbitrario.")
                .setNegativeButton("Cancelar", null)
                .setPositiveButton("MARCAR 2 PUNTOS", (dialog, which) ->
                        measurementView.startCalibration((first, second, pixelDistance) ->
                                showCalibrationVerificationDialog(pixelDistance)))
                .show();
    }

    private void showCalibrationVerificationDialog(double pixelDistance) {
        if (pixelDistance <= 0.0) return;
        EditText input = new EditText(this);
        input.setHint("Longitud real de verificación (mm)");
        input.setGravity(Gravity.CENTER);
        input.setInputType(InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_DECIMAL);

        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(dp(20), dp(8), dp(20), 0);
        TextView detail = new TextView(this);
        detail.setText(String.format(Locale.US,
                "Distancia marcada: %.2f px\\nEscala activa: %.6f mm/px",
                pixelDistance, mmPerPixel));
        detail.setGravity(Gravity.CENTER);
        detail.setTextAlignment(View.TEXT_ALIGNMENT_CENTER);
        detail.setTextSize(13f);
        box.addView(detail);
        box.addView(input);

        AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle("Longitud conocida")
                .setView(box)
                .setNegativeButton("Cancelar", null)
                .setPositiveButton("COMPARAR", null)
                .create();
        dialog.setOnShowListener(ignored ->
                dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
                    double expected;
                    try {
                        expected = Double.parseDouble(input.getText().toString().trim().replace(',', '.'));
                    } catch (Exception e) {
                        input.setError("Introduzca una longitud válida en mm");
                        return;
                    }
                    if (expected <= 0.0) {
                        input.setError("La longitud debe ser mayor que 0");
                        return;
                    }
                    double measured = pixelDistance * mmPerPixel;
                    double difference = measured - expected;
                    double percent = Math.abs(difference) / expected * 100.0;
                    dialog.dismiss();
                    new AlertDialog.Builder(this)
                            .setTitle("Resultado de verificación")
                            .setMessage(String.format(Locale.US,
                                    "Esperado: %.3f mm\\nMedido: %.3f mm\\nDiferencia: %+.3f mm\\nError absoluto: %.2f %%\\n\\nNo se aplica un límite de aceptación automático. Si la discrepancia no es adecuada para su protocolo, recalibre.",
                                    expected, measured, difference, percent))
                            .setNegativeButton("Cerrar", null)
                            .setPositiveButton("RECALIBRAR", (d, w) -> startCalibrationFlow())
                            .show();
                }));
        dialog.show();
    }

'''
    a = a.replace(verify_anchor, methods + verify_anchor, 1)

activity.write_text(a, encoding='utf-8')

# Fix the existing Lint WrongConstant in the radiographic assessment picker.
ra = Path('app/src/main/java/com/cefalo/angulos/RadiographicAssessmentActivity.java')
if ra.exists():
    s = ra.read_text(encoding='utf-8')
    s = s.replace(
        '''            int flags = data.getFlags() & (Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
            getContentResolver().takePersistableUriPermission(uri, flags & Intent.FLAG_GRANT_READ_URI_PERMISSION);''',
        '''            int flags = data.getFlags();
            if ((flags & Intent.FLAG_GRANT_READ_URI_PERMISSION) != 0) {
                getContentResolver().takePersistableUriPermission(
                        uri, Intent.FLAG_GRANT_READ_URI_PERMISSION
                );
            }''')
    ra.write_text(s, encoding='utf-8')

print('Yom branding and improved calibration assistant applied.')
