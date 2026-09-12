from pathlib import Path
import re

ROOT = Path('.')
JAVA = ROOT / 'app/src/main/java/com/cefalo/angulos'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f'Could not apply audit fix: {label}')
    return text.replace(old, new, 1)


def add_string(path: Path, key: str, value: str) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding='utf-8')
    if f'name="{key}"' in text:
        text = re.sub(
            rf'<string name="{re.escape(key)}">.*?</string>',
            f'<string name="{key}">{value}</string>',
            text,
            count=1,
            flags=re.S,
        )
    else:
        text = text.replace(
            '</resources>',
            f'    <string name="{key}">{value}</string>\n</resources>'
        )
    path.write_text(text, encoding='utf-8')


# -----------------------------------------------------------------------------
# 1) Persistence: never report a successful autosave when commit() failed.
# -----------------------------------------------------------------------------
analysis_path = JAVA / 'AnalysisActivity.java'
analysis = analysis_path.read_text(encoding='utf-8')

old_save_tail = '''        SavedStudyStore.save(
                this,
                study
        );

        updateAutosaveStatus(R.string.autosave_saved);

        if (!silent) {
            Toast.makeText(
                    this,
                    "Estudio guardado en Mis análisis.",
                    Toast.LENGTH_LONG
            ).show();
        }

        return true;
'''
new_save_tail = '''        boolean saved = SavedStudyStore.save(
                this,
                study
        );

        if (!saved) {
            updateAutosaveStatus(R.string.autosave_failed);
            if (!silent) {
                Toast.makeText(
                        this,
                        "No se pudo guardar el estudio. Inténtelo de nuevo.",
                        Toast.LENGTH_LONG
                ).show();
            }
            return false;
        }

        updateAutosaveStatus(R.string.autosave_saved);

        if (!silent) {
            Toast.makeText(
                    this,
                    "Estudio guardado en Mis análisis.",
                    Toast.LENGTH_LONG
            ).show();
        }

        return true;
'''
analysis = replace_once(
    analysis,
    old_save_tail,
    new_save_tail,
    'propagate study save failures'
)

old_dialog_save = '''                updateStudyInfo();
                saveStudy(false);
                dialog.dismiss();

                if (firstTime) {
                    promptCalibrationBeforePoints();
                }
'''
new_dialog_save = '''                updateStudyInfo();
                if (!saveStudy(false)) {
                    return;
                }
                dialog.dismiss();

                if (firstTime) {
                    promptCalibrationBeforePoints();
                }
'''
analysis = replace_once(
    analysis,
    old_dialog_save,
    new_dialog_save,
    'keep study dialog open when persistence fails'
)

analysis = analysis.replace(
    '                        ? "Paciente sin nombre"\n',
    '                        ? "Sin identificador"\n',
    1,
)
analysis = analysis.replace(
    '                formLabel("Nombre del paciente");',
    '                formLabel("Identificador o pseudónimo (opcional)");',
    1,
)
analysis = analysis.replace(
    '        editPatient.setHint("Nombre para identificar el estudio");',
    '        editPatient.setHint("Evite datos identificables si no son necesarios");',
    1,
)

old_age_capture = '''                patientAge =
                        editAge.getText()
                                .toString()
                                .trim();

                String selectedSex =
'''
new_age_capture = '''                String enteredAge =
                        editAge.getText()
                                .toString()
                                .trim();

                if (!enteredAge.isEmpty()) {
                    try {
                        int parsedAge = Integer.parseInt(enteredAge);
                        if (parsedAge < 0 || parsedAge > 120) {
                            editAge.setError("Ingrese una edad válida (0–120 años).");
                            return;
                        }
                    } catch (NumberFormatException e) {
                        editAge.setError("Ingrese una edad válida.");
                        return;
                    }
                }
                patientAge = enteredAge;

                String selectedSex =
'''
analysis = replace_once(
    analysis,
    old_age_capture,
    new_age_capture,
    'validate optional patient age'
)

analysis_path.write_text(analysis, encoding='utf-8')

add_string(
    ROOT / 'app/src/main/res/values/strings.xml',
    'autosave_failed',
    'No se pudo guardar · revise el almacenamiento'
)
add_string(
    ROOT / 'app/src/main/res/values-en/strings.xml',
    'autosave_failed',
    'Could not save · check storage'
)


# -----------------------------------------------------------------------------
# 2) Assessment screens: no result may be produced from untouched defaults.
# -----------------------------------------------------------------------------
assessment_path = JAVA / 'RadiographicAssessmentActivity.java'
r = assessment_path.read_text(encoding='utf-8')

if 'private CheckBox cbPanoNoFindings;' not in r:
    r = replace_once(
        r,
        '    private EditText edtPanoNotes;\n',
        '    private EditText edtPanoNotes;\n    private CheckBox cbPanoNoFindings;\n',
        'panoramic no-findings confirmation field'
    )

old_oncreate_tail = '''        buildUi();
        if (imageUriString != null) restoreImage(Uri.parse(imageUriString));
'''
new_oncreate_tail = '''        buildUi();
        if (savedInstanceState != null) {
            restoreAssessmentState(savedInstanceState);
        }
        if (imageUriString != null) restoreImage(Uri.parse(imageUriString));
'''
r = replace_once(r, old_oncreate_tail, new_oncreate_tail, 'restore assessment state')

old_save_state = '''        outState.putString("IMAGE_URI", imageUriString);
    }

    private void buildUi() {
'''
new_save_state = '''        outState.putString("IMAGE_URI", imageUriString);
        saveAssessmentState(outState);
    }

    private void saveAssessmentState(Bundle outState) {
        if (MODE_CVM.equals(mode)) {
            if (spC2Concavity != null) outState.putInt("CVM_C2C", spC2Concavity.getSelectedItemPosition());
            if (spC3Concavity != null) outState.putInt("CVM_C3C", spC3Concavity.getSelectedItemPosition());
            if (spC4Concavity != null) outState.putInt("CVM_C4C", spC4Concavity.getSelectedItemPosition());
            if (spC3Shape != null) outState.putInt("CVM_C3S", spC3Shape.getSelectedItemPosition());
            if (spC4Shape != null) outState.putInt("CVM_C4S", spC4Shape.getSelectedItemPosition());
            return;
        }

        if (MODE_CARPAL.equals(mode)) {
            if (spCarpalSmi != null) outState.putInt("CARPAL_SMI", spCarpalSmi.getSelectedItemPosition());
            return;
        }

        if (MODE_NOLLA.equals(mode)) {
            if (spNollaSex != null) outState.putInt("NOLLA_SEX", spNollaSex.getSelectedItemPosition());
            if (spNollaArch != null) outState.putInt("NOLLA_ARCH", spNollaArch.getSelectedItemPosition());
            if (spNollaSide != null) outState.putInt("NOLLA_SIDE", spNollaSide.getSelectedItemPosition());
            ArrayList<String> scores = new ArrayList<>();
            for (EditText field : nollaScores) scores.add(field.getText().toString());
            outState.putStringArrayList("NOLLA_SCORES", scores);
            if (edtChronYears != null) outState.putString("NOLLA_YEARS", edtChronYears.getText().toString());
            if (edtChronMonths != null) outState.putString("NOLLA_MONTHS", edtChronMonths.getText().toString());
            return;
        }

        if (MODE_RESORPTION.equals(mode)) {
            if (spPrimaryTooth != null) outState.putInt("RES_TOOTH", spPrimaryTooth.getSelectedItemPosition());
            if (spResorption != null) outState.putInt("RES_STAGE", spResorption.getSelectedItemPosition());
            outState.putStringArrayList("RES_KEYS", new ArrayList<>(resorptionRecords.keySet()));
            outState.putStringArrayList("RES_VALUES", new ArrayList<>(resorptionRecords.values()));
            return;
        }

        ArrayList<String> checked = new ArrayList<>();
        for (Map.Entry<String, CheckBox> e : panoChecks.entrySet()) {
            if (e.getValue().isChecked()) checked.add(e.getKey());
        }
        outState.putStringArrayList("PANO_CHECKED", checked);
        if (edtPanoNotes != null) outState.putString("PANO_NOTES", edtPanoNotes.getText().toString());
        if (cbPanoNoFindings != null) outState.putBoolean("PANO_NO_FINDINGS", cbPanoNoFindings.isChecked());
    }

    private void restoreAssessmentState(Bundle state) {
        if (MODE_CVM.equals(mode)) {
            spC2Concavity.setSelection(state.getInt("CVM_C2C", 0));
            spC3Concavity.setSelection(state.getInt("CVM_C3C", 0));
            spC4Concavity.setSelection(state.getInt("CVM_C4C", 0));
            spC3Shape.setSelection(state.getInt("CVM_C3S", 0));
            spC4Shape.setSelection(state.getInt("CVM_C4S", 0));
            return;
        }

        if (MODE_CARPAL.equals(mode)) {
            if (spCarpalSmi != null) spCarpalSmi.setSelection(state.getInt("CARPAL_SMI", 0));
            return;
        }

        if (MODE_NOLLA.equals(mode)) {
            spNollaSex.setSelection(state.getInt("NOLLA_SEX", 0));
            spNollaArch.setSelection(state.getInt("NOLLA_ARCH", 0));
            spNollaSide.setSelection(state.getInt("NOLLA_SIDE", 0));
            ArrayList<String> scores = state.getStringArrayList("NOLLA_SCORES");
            if (scores != null) {
                for (int i = 0; i < Math.min(scores.size(), nollaScores.size()); i++) {
                    nollaScores.get(i).setText(scores.get(i));
                }
            }
            edtChronYears.setText(state.getString("NOLLA_YEARS", ""));
            edtChronMonths.setText(state.getString("NOLLA_MONTHS", ""));
            updateNollaLabels();
            return;
        }

        if (MODE_RESORPTION.equals(mode)) {
            spPrimaryTooth.setSelection(state.getInt("RES_TOOTH", 0));
            spResorption.setSelection(state.getInt("RES_STAGE", 0));
            ArrayList<String> keys = state.getStringArrayList("RES_KEYS");
            ArrayList<String> values = state.getStringArrayList("RES_VALUES");
            if (keys != null && values != null) {
                for (int i = 0; i < Math.min(keys.size(), values.size()); i++) {
                    resorptionRecords.put(keys.get(i), values.get(i));
                }
            }
            updateResorptionResult();
            return;
        }

        ArrayList<String> checked = state.getStringArrayList("PANO_CHECKED");
        if (checked != null) {
            for (String key : checked) {
                CheckBox box = panoChecks.get(key);
                if (box != null) box.setChecked(true);
            }
        }
        if (edtPanoNotes != null) edtPanoNotes.setText(state.getString("PANO_NOTES", ""));
        if (cbPanoNoFindings != null) cbPanoNoFindings.setChecked(state.getBoolean("PANO_NO_FINDINGS", false));
    }

    private boolean requireRadiograph() {
        if (imageView != null && imageView.hasBitmap()) return true;
        Toast.makeText(
                this,
                "Abra la radiografía antes de generar una interpretación.",
                Toast.LENGTH_LONG
        ).show();
        return false;
    }

    private void buildUi() {
'''
r = replace_once(r, old_save_state, new_save_state, 'persist assessment controls across rotation')

old_cvm_inputs = '''        spC2Concavity = addSpinnerRow("C2", new String[]{"Plano / sin concavidad", "Concavidad presente"});
        spC3Concavity = addSpinnerRow("C3", new String[]{"Plano / sin concavidad", "Concavidad presente"});
        spC4Concavity = addSpinnerRow("C4", new String[]{"Plano / sin concavidad", "Concavidad presente"});

        addSection("2 · Forma del cuerpo vertebral");
        String[] shapes = {
                "Trapezoidal",
                "Rectangular horizontal",
                "Cuadrada",
                "Rectangular vertical",
                "No concluyente"
        };
'''
new_cvm_inputs = '''        String[] concavityOptions = {
                "— Seleccione —",
                "Plano / sin concavidad",
                "Concavidad presente"
        };
        spC2Concavity = addSpinnerRow("C2", concavityOptions);
        spC3Concavity = addSpinnerRow("C3", concavityOptions);
        spC4Concavity = addSpinnerRow("C4", concavityOptions);

        addSection("2 · Forma del cuerpo vertebral");
        String[] shapes = {
                "— Seleccione —",
                "Trapezoidal",
                "Rectangular horizontal",
                "Cuadrada",
                "Rectangular vertical",
                "No concluyente"
        };
'''
r = replace_once(r, old_cvm_inputs, new_cvm_inputs, 'remove CVM clinical defaults')

old_cvm_calc = '''    private void calculateCvm() {
        RadiographicAssessmentLogic.CvmResult result =
                RadiographicAssessmentLogic.classifyCvm(
                        spC2Concavity.getSelectedItemPosition() == 1,
                        spC3Concavity.getSelectedItemPosition() == 1,
                        spC4Concavity.getSelectedItemPosition() == 1,
                        shapeFromPosition(spC3Shape.getSelectedItemPosition()),
                        shapeFromPosition(spC4Shape.getSelectedItemPosition())
                );
'''
new_cvm_calc = '''    private void calculateCvm() {
        if (!requireRadiograph()) return;
        if (!AssessmentInputValidator.cvmSelectionsComplete(
                spC2Concavity.getSelectedItemPosition(),
                spC3Concavity.getSelectedItemPosition(),
                spC4Concavity.getSelectedItemPosition(),
                spC3Shape.getSelectedItemPosition(),
                spC4Shape.getSelectedItemPosition()
        )) {
            Toast.makeText(this, "Seleccione todos los criterios C2–C4 antes de calcular.", Toast.LENGTH_LONG).show();
            return;
        }

        RadiographicAssessmentLogic.CvmResult result =
                RadiographicAssessmentLogic.classifyCvm(
                        spC2Concavity.getSelectedItemPosition() == 2,
                        spC3Concavity.getSelectedItemPosition() == 2,
                        spC4Concavity.getSelectedItemPosition() == 2,
                        shapeFromPosition(spC3Shape.getSelectedItemPosition()),
                        shapeFromPosition(spC4Shape.getSelectedItemPosition())
                );
'''
r = replace_once(r, old_cvm_calc, new_cvm_calc, 'validate CVM selections')

old_shape = '''        switch (position) {
            case 0: return RadiographicAssessmentLogic.VertebralShape.TRAPEZOID;
            case 1: return RadiographicAssessmentLogic.VertebralShape.RECTANGULAR_HORIZONTAL;
            case 2: return RadiographicAssessmentLogic.VertebralShape.SQUARE;
            case 3: return RadiographicAssessmentLogic.VertebralShape.RECTANGULAR_VERTICAL;
            default: return RadiographicAssessmentLogic.VertebralShape.UNKNOWN;
        }
'''
new_shape = '''        switch (position) {
            case 1: return RadiographicAssessmentLogic.VertebralShape.TRAPEZOID;
            case 2: return RadiographicAssessmentLogic.VertebralShape.RECTANGULAR_HORIZONTAL;
            case 3: return RadiographicAssessmentLogic.VertebralShape.SQUARE;
            case 4: return RadiographicAssessmentLogic.VertebralShape.RECTANGULAR_VERTICAL;
            default: return RadiographicAssessmentLogic.VertebralShape.UNKNOWN;
        }
'''
r = replace_once(r, old_shape, new_shape, 'shift CVM shape positions')

old_nolla_options = '''        spNollaSex = addSpinnerRow("Sexo", new String[]{"Masculino", "Femenino"});
        spNollaArch = addSpinnerRow("Arcada", new String[]{"Mandibular", "Maxilar"});
        spNollaSide = addSpinnerRow("Lado", new String[]{"Izquierdo", "Derecho"});

        View.OnClickListener labelsUpdater = v -> updateNollaLabels();
'''
new_nolla_options = '''        spNollaSex = addSpinnerRow("Sexo", new String[]{"— Seleccione —", "Masculino", "Femenino"});
        spNollaArch = addSpinnerRow("Arcada", new String[]{"— Seleccione —", "Mandibular", "Maxilar"});
        spNollaSide = addSpinnerRow("Lado", new String[]{"— Seleccione —", "Izquierdo", "Derecho"});

'''
r = replace_once(r, old_nolla_options, new_nolla_options, 'remove Nolla demographic defaults')

old_update_labels = '''        boolean maxillary = spNollaArch.getSelectedItemPosition() == 1;
        boolean right = spNollaSide.getSelectedItemPosition() == 1;
        int[] teeth;
        if (maxillary && !right) teeth = new int[]{21,22,23,24,25,26,27};
        else if (maxillary) teeth = new int[]{11,12,13,14,15,16,17};
        else if (!right) teeth = new int[]{31,32,33,34,35,36,37};
        else teeth = new int[]{41,42,43,44,45,46,47};
'''
new_update_labels = '''        int archPosition = spNollaArch.getSelectedItemPosition();
        int sidePosition = spNollaSide.getSelectedItemPosition();
        if (archPosition == 0 || sidePosition == 0) {
            for (int i = 0; i < nollaToothLabels.size(); i++) {
                nollaToothLabels.get(i).setText("Diente " + (i + 1));
            }
            return;
        }
        boolean maxillary = archPosition == 2;
        boolean right = sidePosition == 2;
        int[] teeth;
        if (maxillary && !right) teeth = new int[]{21,22,23,24,25,26,27};
        else if (maxillary) teeth = new int[]{11,12,13,14,15,16,17};
        else if (!right) teeth = new int[]{31,32,33,34,35,36,37};
        else teeth = new int[]{41,42,43,44,45,46,47};
'''
r = replace_once(r, old_update_labels, new_update_labels, 'defer Nolla tooth labels until arch and side are explicit')

old_nolla_calc_start = '''    private void calculateNolla() {
        double sum = 0.0;
'''
new_nolla_calc_start = '''    private void calculateNolla() {
        if (!requireRadiograph()) return;
        if (!AssessmentInputValidator.nollaSelectionsComplete(
                spNollaSex.getSelectedItemPosition(),
                spNollaArch.getSelectedItemPosition(),
                spNollaSide.getSelectedItemPosition()
        )) {
            Toast.makeText(this, "Seleccione sexo, arcada y lado antes de calcular.", Toast.LENGTH_LONG).show();
            return;
        }

        double sum = 0.0;
'''
r = replace_once(r, old_nolla_calc_start, new_nolla_calc_start, 'validate Nolla selections')
r = r.replace(
    '        boolean female = spNollaSex.getSelectedItemPosition() == 1;\n        boolean maxillary = spNollaArch.getSelectedItemPosition() == 1;\n',
    '        boolean female = spNollaSex.getSelectedItemPosition() == 2;\n        boolean maxillary = spNollaArch.getSelectedItemPosition() == 2;\n',
    1,
)

old_chronological = '''                if (!monthsRaw.isEmpty()) months = Integer.parseInt(monthsRaw);
                if (months < 0 || months > 11) throw new NumberFormatException();
                double chronological = years + months / 12.0;
'''
new_chronological = '''                if (!monthsRaw.isEmpty()) months = Integer.parseInt(monthsRaw);
                if (!AssessmentInputValidator.chronologicalAgeValid(years, months)) {
                    throw new NumberFormatException();
                }
                double chronological = years + months / 12.0;
'''
r = replace_once(r, old_chronological, new_chronological, 'validate chronological age range')

# Carpal already has a placeholder; require the radiograph itself as well.
old_carpal_calc = '''    private void calculateCarpal() {
        if (spCarpalSmi == null || spCarpalSmi.getSelectedItemPosition() == 0) {
'''
new_carpal_calc = '''    private void calculateCarpal() {
        if (!requireRadiograph()) return;
        if (spCarpalSmi == null || spCarpalSmi.getSelectedItemPosition() == 0) {
'''
r = replace_once(r, old_carpal_calc, new_carpal_calc, 'require carpal radiograph')

old_teeth = '''        String[] teeth = {
                "55","54","53","52","51","61","62","63","64","65",
                "85","84","83","82","81","71","72","73","74","75"
        };
'''
new_teeth = '''        String[] teeth = {
                "— Seleccione —",
                "55","54","53","52","51","61","62","63","64","65",
                "85","84","83","82","81","71","72","73","74","75"
        };
'''
r = replace_once(r, old_teeth, new_teeth, 'remove default primary tooth')

old_stages = '''        String[] stages = {
                "Sin reabsorción evidente",
                "Reabsorción inicial",
                "≈ 1/4 de raíz reabsorbida",
                "≈ 1/2 de raíz reabsorbida",
                "≈ 3/4 de raíz reabsorbida",
                "Reabsorción prácticamente completa / exfoliación"
        };
'''
new_stages = '''        String[] stages = {
                "— Seleccione —",
                "Sin reabsorción evidente",
                "Reabsorción inicial",
                "≈ 1/4 de raíz reabsorbida",
                "≈ 1/2 de raíz reabsorbida",
                "≈ 3/4 de raíz reabsorbida",
                "Reabsorción prácticamente completa / exfoliación"
        };
'''
r = replace_once(r, old_stages, new_stages, 'remove default resorption stage')

old_resorption_method = '''    private void addResorptionRecord() {
        String tooth = String.valueOf(spPrimaryTooth.getSelectedItem());
        String key;
        switch (spResorption.getSelectedItemPosition()) {
            case 0: key = "SIN_REABSORCION"; break;
            case 1: key = "INICIAL"; break;
            case 2: key = "R1_4"; break;
            case 3: key = "R1_2"; break;
            case 4: key = "R3_4"; break;
            default: key = "COMPLETA"; break;
        }
        resorptionRecords.put(tooth, key);
        updateResorptionResult();
    }
'''
new_resorption_method = '''    private void addResorptionRecord() {
        if (!requireRadiograph()) return;
        if (!AssessmentInputValidator.resorptionSelectionsComplete(
                spPrimaryTooth.getSelectedItemPosition(),
                spResorption.getSelectedItemPosition()
        )) {
            Toast.makeText(this, "Seleccione el diente temporal y el estadio observado.", Toast.LENGTH_LONG).show();
            return;
        }

        String tooth = String.valueOf(spPrimaryTooth.getSelectedItem());
        String key;
        switch (spResorption.getSelectedItemPosition()) {
            case 1: key = "SIN_REABSORCION"; break;
            case 2: key = "INICIAL"; break;
            case 3: key = "R1_4"; break;
            case 4: key = "R1_2"; break;
            case 5: key = "R3_4"; break;
            case 6: key = "COMPLETA"; break;
            default: return;
        }
        resorptionRecords.put(tooth, key);
        updateResorptionResult();
    }
'''
r = replace_once(r, old_resorption_method, new_resorption_method, 'validate resorption inputs')

old_pano_notes_section = '''        addSection("Notas / localización");
        edtPanoNotes = new EditText(this);
'''
new_pano_notes_section = '''        cbPanoNoFindings = new CheckBox(this);
        cbPanoNoFindings.setText("Confirmo que completé la revisión sistemática y no observo hallazgos para registrar");
        cbPanoNoFindings.setTextSize(14f);
        cbPanoNoFindings.setTextColor(getColor(R.color.text_primary));
        cbPanoNoFindings.setPadding(dp(4), dp(8), dp(4), dp(8));
        content.addView(cbPanoNoFindings, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        ));

        addSection("Notas / localización");
        edtPanoNotes = new EditText(this);
'''
r = replace_once(r, old_pano_notes_section, new_pano_notes_section, 'require explicit no-findings confirmation')

old_generate_start = '''    private void generatePanoSummary() {
        List<String> selected = new ArrayList<>();
'''
new_generate_start = '''    private void generatePanoSummary() {
        if (!requireRadiograph()) return;
        List<String> selected = new ArrayList<>();
'''
r = replace_once(r, old_generate_start, new_generate_start, 'require panoramic radiograph')

old_pano_result = '''        StringBuilder b = new StringBuilder("Evaluación panorámica integral\\n\\n");
        if (selected.isEmpty()) {
            b.append("No se marcaron alteraciones radiográficas evidentes en esta revisión guiada.");
        } else {
            b.append("Hallazgos registrados:\\n");
            for (String item : selected) b.append("• ").append(item).append("\\n");
        }

        String notes = edtPanoNotes.getText().toString().trim();
        if (!notes.isEmpty()) b.append("\\nObservaciones: ").append(notes);
'''
new_pano_result = '''        String notes = edtPanoNotes.getText().toString().trim();
        boolean noFindingsConfirmed = cbPanoNoFindings != null && cbPanoNoFindings.isChecked();

        if (!selected.isEmpty() && noFindingsConfirmed) {
            Toast.makeText(this, "Hay hallazgos marcados y también una confirmación de ausencia. Corrija esa contradicción.", Toast.LENGTH_LONG).show();
            return;
        }

        if (selected.isEmpty() && notes.isEmpty() && !noFindingsConfirmed) {
            Toast.makeText(this, "Marque los hallazgos observados o confirme explícitamente una revisión sin hallazgos.", Toast.LENGTH_LONG).show();
            return;
        }

        StringBuilder b = new StringBuilder("Evaluación panorámica integral\\n\\n");
        if (selected.isEmpty() && noFindingsConfirmed) {
            b.append("El usuario confirmó haber completado la revisión sistemática sin hallazgos para registrar.");
        } else if (selected.isEmpty()) {
            b.append("No se seleccionaron categorías de hallazgo; revise las observaciones escritas.");
        } else {
            b.append("Hallazgos registrados:\\n");
            for (String item : selected) b.append("• ").append(item).append("\\n");
        }

        if (!notes.isEmpty()) b.append("\\nObservaciones: ").append(notes);
'''
r = replace_once(r, old_pano_result, new_pano_result, 'prevent empty panoramic review from implying normality')

# Full EXIF orientation support, including mirrored images.
old_exif = '''    private Bitmap applyExifRotation(Uri uri, Bitmap bitmap) {
        try (InputStream in = getContentResolver().openInputStream(uri)) {
            if (in == null) return bitmap;
            ExifInterface exif = new ExifInterface(in);
            int orientation = exif.getAttributeInt(
                    ExifInterface.TAG_ORIENTATION,
                    ExifInterface.ORIENTATION_NORMAL
            );
            float degrees;
            if (orientation == ExifInterface.ORIENTATION_ROTATE_90) degrees = 90f;
            else if (orientation == ExifInterface.ORIENTATION_ROTATE_180) degrees = 180f;
            else if (orientation == ExifInterface.ORIENTATION_ROTATE_270) degrees = 270f;
            else return bitmap;

            Matrix rotation = new Matrix();
            rotation.postRotate(degrees);
            Bitmap rotated = Bitmap.createBitmap(
                    bitmap, 0, 0, bitmap.getWidth(), bitmap.getHeight(), rotation, true
            );
            if (rotated != bitmap) bitmap.recycle();
            return rotated;
        } catch (Exception ignored) {
            return bitmap;
        }
    }
'''
new_exif = '''    private Bitmap applyExifRotation(Uri uri, Bitmap bitmap) {
        try (InputStream in = getContentResolver().openInputStream(uri)) {
            if (in == null) return bitmap;
            ExifInterface exif = new ExifInterface(in);
            int rotationDegrees = exif.getRotationDegrees();
            boolean flipped = exif.isFlipped();
            if (rotationDegrees == 0 && !flipped) return bitmap;

            Matrix transform = new Matrix();
            if (flipped) transform.postScale(-1f, 1f);
            if (rotationDegrees != 0) transform.postRotate(rotationDegrees);

            Bitmap corrected = Bitmap.createBitmap(
                    bitmap,
                    0,
                    0,
                    bitmap.getWidth(),
                    bitmap.getHeight(),
                    transform,
                    true
            );
            if (corrected != bitmap && !bitmap.isRecycled()) bitmap.recycle();
            return corrected;
        } catch (Exception ignored) {
            return bitmap;
        }
    }
'''
r = replace_once(r, old_exif, new_exif, 'support mirrored EXIF orientations')

assessment_path.write_text(r, encoding='utf-8')


# -----------------------------------------------------------------------------
# 3) Version: this audited build follows v1.33 and must be uniquely identifiable.
# -----------------------------------------------------------------------------
gradle_path = ROOT / 'app/build.gradle'
gradle = gradle_path.read_text(encoding='utf-8')
gradle = re.sub(r'versionCode\s+\d+', 'versionCode 35', gradle, count=1)
gradle = re.sub(r"versionName\s+'[^']+'", "versionName '1.34'", gradle, count=1)
gradle_path.write_text(gradle, encoding='utf-8')


# -----------------------------------------------------------------------------
# 4) Guardrails: fail the build if a safety-critical patch was not materialized.
# -----------------------------------------------------------------------------
final_analysis = analysis_path.read_text(encoding='utf-8')
final_assessment = assessment_path.read_text(encoding='utf-8')
final_gradle = gradle_path.read_text(encoding='utf-8')

checks = {
    'save failure propagation': 'boolean saved = SavedStudyStore.save' in final_analysis,
    'autosave failure state': 'R.string.autosave_failed' in final_analysis,
    'CVM placeholder': 'String[] concavityOptions' in final_assessment,
    'Nolla explicit selection': 'AssessmentInputValidator.nollaSelectionsComplete' in final_assessment,
    'resorption explicit selection': 'AssessmentInputValidator.resorptionSelectionsComplete' in final_assessment,
    'panoramic no-findings confirmation': 'PANO_NO_FINDINGS' in final_assessment,
    'assessment rotation state': 'restoreAssessmentState' in final_assessment,
    'radiograph requirement': 'private boolean requireRadiograph()' in final_assessment,
    'mirrored EXIF support': 'exif.isFlipped()' in final_assessment,
    'v1.34': "versionName '1.34'" in final_gradle,
    'versionCode 35': 'versionCode 35' in final_gradle,
}
missing = [name for name, ok in checks.items() if not ok]
if missing:
    raise RuntimeError('Audit-integrity fixes incomplete: ' + ', '.join(missing))

print('Audit-integrity fixes applied: persistence, explicit clinical inputs, state restoration, EXIF handling, v1.34.')
