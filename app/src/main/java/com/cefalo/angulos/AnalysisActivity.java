package com.cefalo.angulos;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Matrix;
import android.graphics.Paint;
import android.graphics.PointF;
import android.graphics.Typeface;
import androidx.exifinterface.media.ExifInterface;
import android.net.Uri;
import android.os.Bundle;
import android.text.InputType;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Spinner;
import android.widget.ArrayAdapter;
import android.widget.Toast;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

public class AnalysisActivity extends Activity {

    private static final int REQ_IMAGE = 1001;
    private static final int REQ_SAVE_ANNOTATED = 1002;
    private static final int REQ_SAVE_REPORT = 1003;

    private MeasurementView measurementView;
    private TextView txtProgress;
    private TextView txtInstruction;
    private TextView txtStudyInfo;
    private TextView btnCalculate;
    private TextView btnLock;
    private TextView btnCalibrate;
    private TextView txtCalibration;
    private LinearLayout pointChips;

    private List<MeasurementDefinition> definitions;
    private List<LinearMeasurementDefinition> linearDefinitions = new ArrayList<>();
    private List<String> landmarks;

    private String mode;
    private String studyId;
    private String imageUriString;
    private String studyName = "";
    private String patientName = "";
    private String patientAge = "";
    private String patientSex = "";
    private double mmPerPixel = Double.NaN;
    private String calibrationLabel = "";

    private SavedStudyStore.StudyData restoredStudy;
    private boolean restoring = false;
    private Bitmap pendingSaveBitmap;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        if (savedInstanceState != null) {
            studyId = savedInstanceState.getString("STUDY_ID");
        }

        if (studyId == null) {
            studyId = getIntent().getStringExtra("STUDY_ID");
        }

        if (studyId != null) {
            restoredStudy = SavedStudyStore.load(this, studyId);
        }

        if (restoredStudy != null) {
            mode = restoredStudy.mode;
            imageUriString = restoredStudy.imageUri;
            studyName = safe(restoredStudy.studyName);
            patientName = safe(restoredStudy.patientName);
            patientAge = safe(restoredStudy.patientAge);
            patientSex = safe(restoredStudy.patientSex);
            mmPerPixel = restoredStudy.mmPerPixel;
            calibrationLabel = safe(restoredStudy.calibrationLabel);
        } else {
            if (savedInstanceState != null) {
                mode = savedInstanceState.getString("MODE");
                imageUriString = savedInstanceState.getString("IMAGE_URI");
                studyName = safe(savedInstanceState.getString("STUDY_NAME"));
                patientName = safe(savedInstanceState.getString("PATIENT_NAME"));
                patientAge = safe(savedInstanceState.getString("PATIENT_AGE"));
                patientSex = safe(savedInstanceState.getString("PATIENT_SEX"));
                mmPerPixel = savedInstanceState.getDouble("MM_PER_PIXEL", Double.NaN);
                calibrationLabel = safe(savedInstanceState.getString("CALIBRATION_LABEL"));
            }

            if (mode == null) {
                mode = getIntent().getStringExtra("MODE");
            }

            if (mode == null) {
                mode = "STEINER";
            }
        }

        setContentView(R.layout.activity_analysis);

        definitions = new ArrayList<>();
        linearDefinitions = new ArrayList<>();

        if ("VERTEBRAL".equals(mode)) {
            definitions = MeasurementCatalog.vertebral();
            linearDefinitions = LinearMeasurementCatalog.rocabado();
        } else if ("POWELL".equals(mode)) {
            definitions = MeasurementCatalog.powell();
        } else if ("TWEED".equals(mode)) {
            definitions = MeasurementCatalog.tweed();
        } else if ("LEVANDOSKI".equals(mode)) {
            linearDefinitions = LinearMeasurementCatalog.levandoski();
        } else if ("AIRWAY".equals(mode)) {
            definitions = MeasurementCatalog.airwayAngles();
            linearDefinitions = LinearMeasurementCatalog.airway();
        } else {
            definitions = MeasurementCatalog.steiner();
        }

        landmarks = buildLandmarkList(definitions, linearDefinitions);

        TextView txtTitle = findViewById(R.id.txtTitle);
        txtTitle.setText(modeTitle());

        measurementView = findViewById(R.id.measurementView);
        txtProgress = findViewById(R.id.txtProgress);
        txtInstruction = findViewById(R.id.txtInstruction);
        txtStudyInfo = findViewById(R.id.txtStudyInfo);
        btnCalculate = findViewById(R.id.btnCalculate);
        btnLock = findViewById(R.id.btnLock);
        btnCalibrate = findViewById(R.id.btnCalibrate);
        txtCalibration = findViewById(R.id.txtCalibration);
        pointChips = findViewById(R.id.pointChips);

        measurementView.setLandmarks(landmarks);
        measurementView.setProgressListener(this::updateProgress);

        findViewById(R.id.btnBack).setOnClickListener(v -> finish());
        findViewById(R.id.btnOpen).setOnClickListener(v -> openImage());

        findViewById(R.id.btnUndo).setOnClickListener(v ->
                measurementView.undo()
        );

        findViewById(R.id.btnReset).setOnClickListener(v -> {
            new AlertDialog.Builder(this)
                    .setTitle("Borrar todos los puntos")
                    .setMessage(
                            "Esto eliminará todos los puntos colocados en esta radiografía. ¿Desea continuar?"
                    )
                    .setNegativeButton("Cancelar", null)
                    .setPositiveButton(
                            "Borrar todos",
                            (dialog, which) ->
                                    measurementView.resetMeasurement()
                    )
                    .show();
        });

        findViewById(R.id.btnFit)
                .setOnClickListener(v -> measurementView.fitImage());

        findViewById(R.id.btnPrevious)
                .setOnClickListener(v -> measurementView.selectPrevious());

        findViewById(R.id.btnNext)
                .setOnClickListener(v -> measurementView.selectNext());

        findViewById(R.id.btnPointHelp)
                .setOnClickListener(v -> showCurrentPointGuide());

        findViewById(R.id.btnSaveStudy)
                .setOnClickListener(v -> showStudyDetailsDialog(false));

        btnCalibrate.setOnClickListener(v -> startCalibrationFlow());

        btnLock.setOnClickListener(v -> toggleLock());
        btnCalculate.setOnClickListener(v -> calculateFullAnalysis());

        txtInstruction.setText(
                "Toque para colocar el punto seleccionado. Arrastre con un dedo para desplazarse por la radiografía y use dos dedos para hacer zoom. " +
                "Para corregir un punto ya colocado, selecciónelo primero en su recuadro superior y después toque su nueva posición."
        );

        if (linearDefinitions.isEmpty()) {
            btnCalibrate.setVisibility(android.view.View.GONE);
            txtCalibration.setVisibility(android.view.View.GONE);
        }

        refreshPointChips();
        updateStudyInfo();
        updateCalibrationStatus();

        if (restoredStudy != null) {
            restoreStudy(restoredStudy);
        } else {
            updateProgress(
                    measurementView.getPlacedCount(),
                    landmarks.size(),
                    measurementView.getCurrentLabel()
            );
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        saveStudy(true);
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);

        outState.putString("STUDY_ID", studyId);
        outState.putString("MODE", mode);
        outState.putString("IMAGE_URI", imageUriString);
        outState.putString("STUDY_NAME", studyName);
        outState.putString("PATIENT_NAME", patientName);
        outState.putString("PATIENT_AGE", patientAge);
        outState.putString("PATIENT_SEX", patientSex);
        outState.putDouble("MM_PER_PIXEL", mmPerPixel);
        outState.putString("CALIBRATION_LABEL", calibrationLabel);
    }

    private String modeTitle() {
        if ("VERTEBRAL".equals(mode)) return "Vertebral / Rocabado";
        if ("POWELL".equals(mode)) return "Análisis de Powell";
        if ("TWEED".equals(mode)) return "Análisis de Tweed";
        if ("LEVANDOSKI".equals(mode)) return "Panorámico de Levandoski";
        if ("AIRWAY".equals(mode)) return "Análisis de vía aérea";
        return "Análisis de Steiner";
    }

    private String safe(String value) {
        return value == null ? "" : value;
    }

    private List<String> buildLandmarkList(
            List<MeasurementDefinition> defs,
            List<LinearMeasurementDefinition> linearDefs
    ) {
        Set<String> ordered = new LinkedHashSet<>();

        for (MeasurementDefinition def : defs) {
            for (String label : def.pointLabels) {
                ordered.add(label);
            }
        }

        for (LinearMeasurementDefinition def : linearDefs) {
            for (String label : def.pointLabels) {
                ordered.add(label);
            }
        }

        return new ArrayList<>(ordered);
    }

    private void restoreStudy(
            SavedStudyStore.StudyData study
    ) {
        if (study.imageUri == null) return;

        restoring = true;
        imageUriString = study.imageUri;

        try {
            Uri uri = Uri.parse(imageUriString);

            Bitmap bitmap =
                    decodeSampledBitmap(uri, 4096);

            if (bitmap == null) {
                throw new IOException("Bitmap nulo");
            }

            bitmap = applyExifRotation(uri, bitmap);

            measurementView.setBitmap(bitmap);
            measurementView.setPoints(
                    mapSavedPoints(study)
            );
            measurementView.setLocked(false);
            measurementView.setPointLocks(
                    mapSavedPointLocks(study)
            );

            if (study.locked) {
                measurementView.lockAllPlacedPoints();
            }

            mmPerPixel = study.mmPerPixel;
            calibrationLabel = safe(study.calibrationLabel);

            updateLockButton();
            updateStudyInfo();
            updateCalibrationStatus();

            updateProgress(
                    measurementView.getPlacedCount(),
                    landmarks.size(),
                    measurementView.getCurrentLabel()
            );

        } catch (Exception e) {
            Toast.makeText(
                    this,
                    "No se pudo volver a abrir la radiografía guardada.",
                    Toast.LENGTH_LONG
            ).show();

        } finally {
            restoring = false;
        }
    }

    private List<PointF> mapSavedPoints(
            SavedStudyStore.StudyData study
    ) {
        List<PointF> mapped = new ArrayList<>();

        for (String currentLabel : landmarks) {
            int savedIndex =
                    study.labels.indexOf(currentLabel);

            if (savedIndex >= 0
                    && savedIndex < study.points.size()) {

                PointF p = study.points.get(savedIndex);

                mapped.add(
                        p == null
                                ? null
                                : new PointF(p.x, p.y)
                );

            } else {
                mapped.add(null);
            }
        }

        return mapped;
    }

    private List<Boolean> mapSavedPointLocks(
            SavedStudyStore.StudyData study
    ) {
        List<Boolean> mapped = new ArrayList<>();

        for (String currentLabel : landmarks) {
            int savedIndex =
                    study.labels.indexOf(currentLabel);

            boolean value =
                    savedIndex >= 0
                            && savedIndex < study.pointLocks.size()
                            && Boolean.TRUE.equals(
                                    study.pointLocks.get(savedIndex)
                            );

            mapped.add(value);
        }

        return mapped;
    }

    private void updateProgress(
            int placed,
            int total,
            String currentLabel
    ) {
        refreshPointChips();
        updatePointDescription(currentLabel);

        if (total == 0) {
            txtProgress.setText(
                    "No hay puntos definidos."
            );
            btnCalculate.setAlpha(0.45f);
            return;
        }

        int selected =
                measurementView.getSelectedIndex();

        boolean selectedPlaced =
                measurementView.hasPointAt(selected);

        boolean selectedLocked =
                measurementView.isPointLocked(selected);

        String selectedState =
                selectedLocked
                        ? "Bloqueado: "
                        : selectedPlaced
                                ? "Corregir: "
                                : "Marcar: ";

        if (placed >= total) {
            txtProgress.setText(
                    "✓ Puntos completos: " +
                    placed +
                    " / " +
                    total +
                    "\n" +
                    selectedState +
                    currentLabel
            );

            btnCalculate.setAlpha(1f);

        } else {
            txtProgress.setText(
                    "Puntos: " +
                    placed +
                    " / " +
                    total +
                    "\n" +
                    selectedState +
                    currentLabel
            );

            btnCalculate.setAlpha(0.55f);
        }

        updateLockButton();

        if (!restoring) {
            saveStudy(true);
        }
    }

    private void updatePointDescription(String currentLabel) {
        if (txtInstruction == null) return;

        if (currentLabel == null || currentLabel.trim().isEmpty()) {
            txtInstruction.setText(
                    "Seleccione un punto para ver exactamente dónde colocarlo."
            );
            return;
        }

        int index = landmarks.indexOf(currentLabel);
        boolean placed = index >= 0 && measurementView.hasPointAt(index);
        boolean pointLocked = index >= 0 && measurementView.isPointLocked(index);

        txtInstruction.setText(
                (pointLocked ? "BLOQUEADO · " : placed ? "✓ " : "⌖ ") +
                currentLabel +
                " · Dónde colocarlo:\n" +
                PointGuide.description(currentLabel) +
                "\nToque para marcar. Arrastre con un dedo para mover la imagen. Para corregir un punto existente, selecciónelo en su recuadro y toque la nueva posición; tocar directamente otro punto no lo selecciona."
        );
    }

    private void refreshPointChips() {
        if (pointChips == null
                || landmarks == null
                || measurementView == null) {
            return;
        }

        pointChips.removeAllViews();

        int selected =
                measurementView.getSelectedIndex();

        for (int i = 0; i < landmarks.size(); i++) {
            final int index = i;

            String label = landmarks.get(i);

            boolean placed =
                    measurementView.hasPointAt(i);

            boolean isSelected =
                    i == selected;

            boolean pointLocked =
                    measurementView.isPointLocked(i);

            TextView chip = new TextView(this);

            chip.setText(
                    label +
                    (pointLocked
                            ? "  🔒"
                            : placed
                                    ? "  ✓"
                                    : "")
            );

            chip.setTextSize(11.5f);
            chip.setTypeface(
                    Typeface.DEFAULT,
                    Typeface.BOLD
            );
            chip.setGravity(Gravity.CENTER);

            chip.setPadding(
                    dp(10),
                    dp(6),
                    dp(10),
                    dp(6)
            );

            chip.setClickable(true);
            chip.setFocusable(true);

            if (isSelected) {
                chip.setBackgroundResource(
                        R.drawable.chip_selected
                );
                chip.setTextColor(0xFF5B3FA4);

            } else if (placed) {
                chip.setBackgroundResource(
                        R.drawable.button_soft_mint
                );
                chip.setTextColor(0xFF15383D);

            } else {
                chip.setBackgroundResource(
                        R.drawable.button_soft_purple
                );
                chip.setTextColor(0xFF5B3FA4);
            }

            LinearLayout.LayoutParams lp =
                    new LinearLayout.LayoutParams(
                            ViewGroup.LayoutParams.WRAP_CONTENT,
                            dp(48)
                    );

            lp.setMargins(
                    0,
                    0,
                    dp(5),
                    0
            );

            chip.setLayoutParams(lp);

            chip.setOnClickListener(v -> {
                measurementView.setSelectedIndex(
                        index,
                        true
                );
            });

            chip.setOnLongClickListener(v -> {
                showPointGuide(
                        landmarks.get(index)
                );
                return true;
            });

            pointChips.addView(chip);
        }
    }

    private void showCurrentPointGuide() {
        String label =
                measurementView.getCurrentLabel();

        if (label == null) {
            Toast.makeText(
                    this,
                    "No hay un punto seleccionado.",
                    Toast.LENGTH_SHORT
            ).show();
            return;
        }

        showPointGuide(label);
    }

    private void showPointGuide(String label) {
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setGravity(Gravity.CENTER_HORIZONTAL);
        box.setPadding(
                dp(20),
                dp(10),
                dp(20),
                dp(6)
        );

        ImageView image = new ImageView(this);
        image.setImageResource(
                R.drawable.tooth_ruler_mascot
        );
        image.setScaleType(
                ImageView.ScaleType.CENTER_INSIDE
        );

        box.addView(
                image,
                new LinearLayout.LayoutParams(
                        dp(96),
                        dp(74)
                )
        );

        TextView description = new TextView(this);

        String status =
                measurementView.hasPointAt(
                        landmarks.indexOf(label)
                )
                        ? "\n\n✓ Ya está colocado. Para corregirlo, seleccione su recuadro y toque la nueva posición en la radiografía."
                        : "\n\n— Todavía no está colocado.";

        description.setText(
                PointGuide.description(label) +
                status
        );

        description.setTextSize(15f);
        description.setTextColor(0xFF3D3946);
        description.setPadding(
                0,
                dp(8),
                0,
                dp(6)
        );

        box.addView(description);

        ScrollView guideScroll = new ScrollView(this);
        guideScroll.setFillViewport(true);
        guideScroll.addView(box);

        AlertDialog guideDialog = new AlertDialog.Builder(this)
                .setTitle(
                        "¿Dónde está " +
                        label +
                        "?"
                )
                .setView(guideScroll)
                .setPositiveButton(
                        "Entendido",
                        null
                )
                .create();

        guideDialog.show();
    }

    private void toggleLock() {
        int selected =
                measurementView.getSelectedIndex();

        if (!measurementView.hasPointAt(selected)) {
            Toast.makeText(
                    this,
                    "Primero coloque el punto seleccionado.",
                    Toast.LENGTH_SHORT
            ).show();
            return;
        }

        if (measurementView.toggleSelectedPointLock()) {
            updateLockButton();
            refreshPointChips();
            updatePointDescription(
                    measurementView.getCurrentLabel()
            );
            saveStudy(true);
        }
    }

    private void updateLockButton() {
        int selected =
                measurementView.getSelectedIndex();

        if (!measurementView.hasPointAt(selected)) {
            btnLock.setText("BLOQ. PUNTO");
            btnLock.setAlpha(0.55f);
            btnLock.setBackgroundResource(
                    R.drawable.button_soft_purple_centered
            );
            btnLock.setTextColor(0xFF5B3FA4);
            return;
        }

        btnLock.setAlpha(1f);

        if (measurementView.isPointLocked(selected)) {
            btnLock.setText("DESBLOQ. PUNTO");
            btnLock.setBackgroundResource(
                    R.drawable.button_soft_mint_centered
            );
            btnLock.setTextColor(0xFF15383D);

        } else {
            btnLock.setText("BLOQ. PUNTO");
            btnLock.setBackgroundResource(
                    R.drawable.button_soft_purple_centered
            );
            btnLock.setTextColor(0xFF5B3FA4);
        }
    }

    private void updateStudyInfo() {
        if (txtStudyInfo == null) return;

        String title =
                studyName.trim().isEmpty()
                        ? "Estudio sin nombre"
                        : studyName.trim();

        String patient =
                patientName.trim().isEmpty()
                        ? "Paciente sin nombre"
                        : patientName.trim();

        String age =
                patientAge.trim().isEmpty()
                        ? ""
                        : " · " +
                        patientAge.trim() +
                        " años";

        String sex =
                patientSex.trim().isEmpty()
                        ? ""
                        : " · " +
                        patientSex.trim();

        txtStudyInfo.setText(
                title +
                "   ·   " +
                patient +
                age +
                sex
        );
    }

    private void showStudyDetailsDialog(
            boolean firstTime
    ) {
        if (!measurementView.hasBitmap()
                && !firstTime) {

            Toast.makeText(
                    this,
                    "Abra una radiografía antes de guardar el estudio.",
                    Toast.LENGTH_SHORT
            ).show();

            return;
        }

        if (studyName.trim().isEmpty()) {
            studyName =
                    SavedStudyStore.suggestedStudyName(
                            this
                    );
        }

        LinearLayout form = new LinearLayout(this);
        form.setOrientation(LinearLayout.VERTICAL);
        form.setPadding(
                dp(20),
                dp(6),
                dp(20),
                dp(4)
        );

        ImageView image = new ImageView(this);
        image.setImageResource(
                R.drawable.ic_yomceph_mark
        );
        image.setScaleType(
                ImageView.ScaleType.CENTER_INSIDE
        );

        form.addView(
                image,
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        dp(74)
                )
        );

        TextView labelStudy =
                formLabel("Nombre del estudio o radiografía");

        EditText editStudy = new EditText(this);
        editStudy.setSingleLine(true);
        editStudy.setText(studyName);
        editStudy.setHint("Ej. Radiografía 1, Estudio 1");

        TextView labelPatient =
                formLabel("Nombre del paciente");

        EditText editPatient = new EditText(this);
        editPatient.setSingleLine(true);
        editPatient.setText(patientName);
        editPatient.setHint("Nombre para identificar el estudio");

        TextView labelAge =
                formLabel("Edad");

        EditText editAge = new EditText(this);
        editAge.setSingleLine(true);
        editAge.setText(patientAge);
        editAge.setHint("Ej. 12");
        editAge.setInputType(
                InputType.TYPE_CLASS_NUMBER
        );

        TextView labelSex =
                formLabel("Sexo para normas que lo requieran");

        Spinner editSex = new Spinner(this);
        ArrayAdapter<String> sexAdapter = new ArrayAdapter<>(
                this,
                android.R.layout.simple_spinner_item,
                new String[]{"Sin especificar", "Femenino", "Masculino"}
        );
        sexAdapter.setDropDownViewResource(
                android.R.layout.simple_spinner_dropdown_item
        );
        editSex.setAdapter(sexAdapter);

        if ("Femenino".equals(patientSex)) {
            editSex.setSelection(1);
        } else if ("Masculino".equals(patientSex)) {
            editSex.setSelection(2);
        }

        form.addView(labelStudy);
        form.addView(editStudy);
        form.addView(labelPatient);
        form.addView(editPatient);
        form.addView(labelAge);
        form.addView(editAge);
        form.addView(labelSex);
        form.addView(editSex);

        ScrollView formScroll = new ScrollView(this);
        formScroll.setFillViewport(true);
        formScroll.addView(form);

        AlertDialog dialog =
                new AlertDialog.Builder(this)
                        .setTitle(
                                firstTime
                                        ? "Identificar radiografía"
                                        : "Datos del estudio"
                        )
                        .setView(formScroll)
                        .setPositiveButton(
                                "Guardar",
                                null
                        )
                        .setNegativeButton(
                                firstTime
                                        ? "Usar sugerencia"
                                        : "Cancelar",
                                null
                        )
                        .create();

        dialog.setOnShowListener(unused -> {
            if (dialog.getWindow() != null) {
                dialog.getWindow().setSoftInputMode(
                        android.view.WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE
                );
            }

            dialog.getButton(
                    AlertDialog.BUTTON_POSITIVE
            ).setOnClickListener(v -> {
                String enteredStudy =
                        editStudy.getText()
                                .toString()
                                .trim();

                studyName =
                        enteredStudy.isEmpty()
                                ? SavedStudyStore
                                        .suggestedStudyName(this)
                                : enteredStudy;

                patientName =
                        editPatient.getText()
                                .toString()
                                .trim();

                patientAge =
                        editAge.getText()
                                .toString()
                                .trim();

                String selectedSex =
                        String.valueOf(editSex.getSelectedItem());
                patientSex =
                        "Sin especificar".equals(selectedSex)
                                ? ""
                                : selectedSex;

                updateStudyInfo();
                saveStudy(false);
                dialog.dismiss();

                if (firstTime) {
                    promptCalibrationBeforePoints();
                }
            });

            if (firstTime) {
                dialog.getButton(
                        AlertDialog.BUTTON_NEGATIVE
                ).setOnClickListener(v -> {
                    updateStudyInfo();
                    saveStudy(true);
                    dialog.dismiss();
                    promptCalibrationBeforePoints();
                });
            }
        });

        if (firstTime) {
            dialog.setCanceledOnTouchOutside(false);
            dialog.setOnCancelListener(unused -> {
                updateStudyInfo();
                saveStudy(true);
                promptCalibrationBeforePoints();
            });
        }

        dialog.show();
    }

    private TextView formLabel(String text) {
        TextView label = new TextView(this);
        label.setText(text);
        label.setTextColor(0xFF5B3FA4);
        label.setTypeface(
                Typeface.DEFAULT,
                Typeface.BOLD
        );
        label.setTextSize(14f);
        label.setPadding(
                0,
                dp(10),
                0,
                0
        );
        return label;
    }

    private void saveStudy(boolean silent) {
        if (measurementView == null
                || !measurementView.hasBitmap()
                || imageUriString == null) {

            if (!silent) {
                Toast.makeText(
                        this,
                        "Abra una radiografía antes de guardar el estudio.",
                        Toast.LENGTH_SHORT
                ).show();
            }

            return;
        }

        if (studyId == null) {
            studyId =
                    SavedStudyStore.newId();
        }

        if (studyName.trim().isEmpty()) {
            studyName =
                    SavedStudyStore
                            .suggestedStudyName(this);
        }

        SavedStudyStore.StudyData study =
                new SavedStudyStore.StudyData();

        study.id = studyId;
        study.mode = mode;
        study.imageUri = imageUriString;
        study.studyName = studyName;
        study.patientName = patientName;
        study.patientAge = patientAge;
        study.patientSex = patientSex;
        study.locked =
                measurementView.areAllPlacedPointsLocked();
        study.pointLocks =
                measurementView.getPointLocksSnapshot();
        study.mmPerPixel = mmPerPixel;
        study.calibrationLabel = calibrationLabel;

        study.labels =
                new ArrayList<>(landmarks);

        study.points =
                measurementView
                        .getPointsSnapshot();

        SavedStudyStore.save(
                this,
                study
        );

        if (!silent) {
            Toast.makeText(
                    this,
                    "Estudio guardado en Mis análisis.",
                    Toast.LENGTH_LONG
            ).show();
        }
    }

    private void promptCalibrationBeforePoints() {
        if (linearDefinitions.isEmpty()
                || !measurementView.hasBitmap()
                || (!Double.isNaN(mmPerPixel) && mmPerPixel > 0)) {
            return;
        }

        AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle("Paso 1 · Calibración")
                .setMessage(
                        "Antes de colocar los puntos, calibre la radiografía si desea obtener medidas en mm o cm. " +
                        "Marque dos extremos de una referencia de longitud conocida y escriba cuánto mide.\n\n" +
                        "Si la imagen no tiene una referencia válida, puede continuar sin calibrar; los ángulos seguirán funcionando, pero las medidas lineales no se calcularán."
                )
                .setNegativeButton(
                        "Continuar sin calibrar",
                        null
                )
                .setPositiveButton(
                        "Calibrar ahora",
                        (d, which) -> startCalibrationFlow()
                )
                .create();

        dialog.setCanceledOnTouchOutside(false);
        dialog.show();
    }

    private void updateCalibrationStatus() {
        if (txtCalibration == null) return;

        if (Double.isNaN(mmPerPixel) || mmPerPixel <= 0) {
            txtCalibration.setText("PASO 1 · SIN CALIBRAR");
            btnCalibrate.setText("CALIBRAR");
            return;
        }

        txtCalibration.setText(
                "PASO 1 · CALIBRADO · " +
                calibrationLabel
        );
        btnCalibrate.setText("RECALIBRAR");
    }

    private String calibrationInstructions() {
        String base =
                "Use una regla, calibrador o marcador de longitud conocida visible en la imagen. " +
                "Puede estar horizontal, vertical o diagonal. Marque sus dos extremos y después indique cuánto mide.\n\n" +
                "La calibración se guarda con este estudio.";

        if ("LEVANDOSKI".equals(mode)) {
            return base +
                    "\n\nImportante: en radiografías panorámicas la magnificación puede variar entre zonas. " +
                    "Use las medidas de Levandoski principalmente para comparación derecha/izquierda y evite interpretar una sola calibración global como escala geométrica exacta de toda la panorámica.";
        }

        return base +
                " Para reducir error de magnificación, la referencia debe pertenecer a la misma imagen y, de ser posible, al mismo plano del objeto medido.";
    }

    private void startCalibrationFlow() {
        if (!measurementView.hasBitmap()) {
            Toast.makeText(
                    this,
                    "Primero abra una radiografía.",
                    Toast.LENGTH_SHORT
            ).show();
            return;
        }

        LinearLayout content = new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        content.setPadding(dp(20), dp(8), dp(20), dp(8));

        TextView step = new TextView(this);
        step.setText("1. Localice una referencia de longitud conocida en la radiografía.");
        step.setTextSize(14f);
        step.setTextColor(0xFF3D3946);
        step.setPadding(0, 0, 0, dp(8));
        content.addView(step);

        TextView step2 = new TextView(this);
        step2.setText("2. Toque un extremo y después el otro. Puede ser horizontal, vertical o diagonal.");
        step2.setTextSize(14f);
        step2.setTextColor(0xFF3D3946);
        step2.setPadding(0, 0, 0, dp(8));
        content.addView(step2);

        TextView step3 = new TextView(this);
        step3.setText("3. Después escribirá cuánto mide realmente en mm o cm.");
        step3.setTextSize(14f);
        step3.setTextColor(0xFF3D3946);
        step3.setPadding(0, 0, 0, dp(8));
        content.addView(step3);

        TextView note = new TextView(this);
        note.setText(calibrationInstructions());
        note.setTextSize(12.5f);
        note.setTextColor(0xFF2C7E86);
        note.setBackgroundResource(R.drawable.button_soft_mint);
        note.setPadding(dp(12), dp(10), dp(12), dp(10));
        content.addView(note);

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.addView(content);

        AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle("Paso 1 · Calibración")
                .setView(scroll)
                .setNegativeButton("Cancelar", null)
                .setPositiveButton(
                        "Marcar referencia",
                        (unused, which) -> {
                            Toast.makeText(
                                    this,
                                    "Toque el primer extremo y después el segundo.",
                                    Toast.LENGTH_LONG
                            ).show();

                            measurementView.startCalibration(
                                    (first, second, pixelDistance) ->
                                            showCalibrationLengthDialog(pixelDistance)
                            );
                        }
                )
                .create();

        dialog.show();

        if (dialog.getWindow() != null) {
            dialog.getWindow().setSoftInputMode(
                    android.view.WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE
            );
        }
    }

    private void showCalibrationLengthDialog(double pixelDistance) {
        if (pixelDistance < 10.0) {
            measurementView.clearCalibrationOverlay();
            Toast.makeText(
                    this,
                    "La referencia quedó demasiado corta. Marque dos extremos más separados.",
                    Toast.LENGTH_LONG
            ).show();
            return;
        }

        LinearLayout form = new LinearLayout(this);
        form.setOrientation(LinearLayout.VERTICAL);
        form.setPadding(dp(20), dp(6), dp(20), dp(8));

        TextView info = new TextView(this);
        info.setText(
                "Referencia marcada: " +
                String.format(Locale.US, "%.1f píxeles", pixelDistance)
        );
        info.setTextColor(0xFF5B3FA4);
        info.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        info.setTextSize(14f);
        info.setGravity(Gravity.CENTER);
        info.setPadding(0, 0, 0, dp(10));
        form.addView(info);

        TextView help = new TextView(this);
        help.setText(
                "Escriba la longitud REAL de la regla, calibrador o marcador que acaba de señalar."
        );
        help.setTextColor(0xFF4A4652);
        help.setTextSize(13f);
        help.setGravity(Gravity.CENTER);
        help.setPadding(0, 0, 0, dp(8));
        form.addView(help);

        TextView label = formLabel("Longitud conocida");
        label.setGravity(Gravity.CENTER);
        form.addView(label);

        LinearLayout valueRow = new LinearLayout(this);
        valueRow.setOrientation(LinearLayout.HORIZONTAL);
        valueRow.setGravity(Gravity.CENTER_VERTICAL);

        EditText length = new EditText(this);
        length.setSingleLine(true);
        length.setHint("Ej. 10");
        length.setTextSize(16f);
        length.setGravity(Gravity.CENTER);
        length.setInputType(
                InputType.TYPE_CLASS_NUMBER |
                InputType.TYPE_NUMBER_FLAG_DECIMAL
        );

        LinearLayout.LayoutParams lengthLp =
                new LinearLayout.LayoutParams(0, dp(54), 1f);
        valueRow.addView(length, lengthLp);

        Spinner unit = new Spinner(this);
        ArrayAdapter<String> adapter = new ArrayAdapter<>(
                this,
                android.R.layout.simple_spinner_item,
                new String[]{"mm", "cm"}
        );
        adapter.setDropDownViewResource(
                android.R.layout.simple_spinner_dropdown_item
        );
        unit.setAdapter(adapter);

        LinearLayout.LayoutParams unitLp =
                new LinearLayout.LayoutParams(dp(100), dp(54));
        unitLp.setMargins(dp(8), 0, 0, 0);
        valueRow.addView(unit, unitLp);

        form.addView(valueRow);

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.addView(form);

        AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle("Paso 1 · Longitud de referencia")
                .setView(scroll)
                .setNegativeButton(
                        "Cancelar",
                        (unused, which) ->
                                measurementView.clearCalibrationOverlay()
                )
                .setPositiveButton("Guardar", null)
                .create();

        dialog.setOnShowListener(unused -> {
            if (dialog.getWindow() != null) {
                dialog.getWindow().setSoftInputMode(
                        android.view.WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE
                );
            }

            dialog.getButton(AlertDialog.BUTTON_POSITIVE)
                    .setOnClickListener(v -> {
                        String raw = length.getText().toString().trim();

                        if (raw.isEmpty()) {
                            length.setError("Ingrese una longitud.");
                            return;
                        }

                        double value;

                        try {
                            value = Double.parseDouble(
                                    raw.replace(',', '.')
                            );
                        } catch (Exception e) {
                            length.setError("Longitud no válida.");
                            return;
                        }

                        if (value <= 0 || pixelDistance <= 0) {
                            length.setError("Debe ser mayor que cero.");
                            return;
                        }

                        String selectedUnit =
                                String.valueOf(unit.getSelectedItem());

                        double realMm =
                                "cm".equals(selectedUnit)
                                        ? value * 10.0
                                        : value;

                        mmPerPixel = realMm / pixelDistance;

                        calibrationLabel =
                                String.format(
                                        Locale.US,
                                        "%.2f %s",
                                        value,
                                        selectedUnit
                                );

                        updateCalibrationStatus();
                        saveStudy(true);
                        measurementView.clearCalibrationOverlay();

                        Toast.makeText(
                                this,
                                "Calibración guardada. Ya puede colocar los puntos.",
                                Toast.LENGTH_LONG
                        ).show();

                        dialog.dismiss();
                    });
        });

        dialog.show();
    }

    private Double calculateLinear(
            LinearMeasurementDefinition def
    ) {
        if (def == null
                || Double.isNaN(mmPerPixel)
                || mmPerPixel <= 0) {
            return null;
        }

        if (def.type == LinearMeasurementDefinition.Type.DISTANCE) {
            PointF a = measurementView.getPoint(def.pointLabels[0]);
            PointF b = measurementView.getPoint(def.pointLabels[1]);

            if (a == null || b == null) return null;

            return Math.hypot(
                    b.x - a.x,
                    b.y - a.y
            ) * mmPerPixel;
        }

        PointF a = measurementView.getPoint(def.pointLabels[0]);
        PointF b = measurementView.getPoint(def.pointLabels[1]);
        PointF p = measurementView.getPoint(def.pointLabels[2]);

        if (a == null || b == null || p == null) return null;

        double dx = b.x - a.x;
        double dy = b.y - a.y;
        double length = Math.hypot(dx, dy);

        if (length == 0) return null;

        double signedPixels =
                (
                        dx * (p.y - a.y) -
                        dy * (p.x - a.x)
                ) / length;

        if (def.interpretation
                == LinearMeasurementDefinition.Interpretation.HYOID_TRIANGLE) {
            double t =
                    (
                            (p.x - a.x) * dx +
                            (p.y - a.y) * dy
                    ) / (length * length);

            double projectionY = a.y + t * dy;
            double magnitudeMm = Math.abs(signedPixels) * mmPerPixel;

            if (Math.abs(p.y - projectionY) < 0.01) {
                return 0.0;
            }

            // En coordenadas de imagen Android, Y aumenta hacia inferior.
            // Así, H por debajo de C3-RGn siempre queda positivo aunque
            // la radiografía esté orientada hacia la izquierda o derecha.
            return p.y > projectionY
                    ? magnitudeMm
                    : -magnitudeMm;
        }

        if (def.interpretation
                == LinearMeasurementDefinition.Interpretation.CERVICAL_DEPTH) {
            PointF anteriorReference = measurementView.getPoint("N");

            if (anteriorReference != null) {
                double referenceSide =
                        (
                                dx * (anteriorReference.y - a.y) -
                                dy * (anteriorReference.x - a.x)
                        ) / length;

                if (Math.abs(referenceSide) > 0.0001) {
                    signedPixels *= Math.signum(referenceSide);
                }
            }
        }

        double valueMm = signedPixels * mmPerPixel;

        if (def.type == LinearMeasurementDefinition.Type.PERPENDICULAR_ABS) {
            return Math.abs(valueMm);
        }

        return valueMm;
    }

    private void calculateFullAnalysis() {
        if (!measurementView.hasBitmap()) {
            Toast.makeText(
                    this,
                    "Primero abra una radiografía.",
                    Toast.LENGTH_SHORT
            ).show();
            return;
        }

        if (definitions.isEmpty()
                && !linearDefinitions.isEmpty()
                && (Double.isNaN(mmPerPixel) || mmPerPixel <= 0)) {
            Toast.makeText(
                    this,
                    "Este análisis necesita calibración para obtener medidas en mm.",
                    Toast.LENGTH_LONG
            ).show();
            startCalibrationFlow();
            return;
        }

        if (!measurementView.isComplete()) {
            String next =
                    measurementView.getCurrentLabel();

            Toast.makeText(
                    this,
                    "Faltan puntos. Seleccionado: " +
                    (
                            next == null
                                    ? "—"
                                    : next
                    ),
                    Toast.LENGTH_LONG
            ).show();

            return;
        }

        saveStudy(true);
        showResultsDialog();
    }

    private void showResultsDialog() {
        ScrollView scroll = new ScrollView(this);

        LinearLayout container =
                new LinearLayout(this);

        container.setOrientation(
                LinearLayout.VERTICAL
        );

        int pad = dp(18);

        container.setPadding(
                pad,
                pad,
                pad,
                pad
        );

        scroll.addView(container);

        TextView heading = new TextView(this);
        heading.setText(
                studyName +
                "\n" +
                (
                        patientName.trim().isEmpty()
                                ? "Paciente sin nombre"
                                : patientName
                ) +
                (
                        patientAge.trim().isEmpty()
                                ? ""
                                : " · " +
                                patientAge +
                                " años"
                ) +
                (
                        patientSex.trim().isEmpty()
                                ? ""
                                : " · " + patientSex
                )
        );
        heading.setTextColor(0xFF5B3FA4);
        heading.setTextSize(15f);
        heading.setTypeface(
                Typeface.DEFAULT,
                Typeface.BOLD
        );
        heading.setPadding(
                0,
                0,
                0,
                dp(10)
        );
        container.addView(heading);

        TextView intro = new TextView(this);
        intro.setText(
                "Resultados calculados con los mismos puntos anatómicos. " +
                "Puede cerrar esta ventana, desbloquear el trazado, corregir un punto y volver a calcular."
        );
        intro.setTextSize(13f);
        intro.setTextColor(0xFF4A4652);
        intro.setPadding(
                0,
                0,
                0,
                dp(12)
        );
        container.addView(intro);

        TextView evidenceNotice = new TextView(this);
        evidenceNotice.setText(resultsSafetyNotice());
        evidenceNotice.setTextSize(12.5f);
        evidenceNotice.setTextColor(0xFF5A4615);
        evidenceNotice.setGravity(Gravity.CENTER);
        evidenceNotice.setTextAlignment(android.view.View.TEXT_ALIGNMENT_CENTER);
        evidenceNotice.setBackgroundResource(R.drawable.button_soft_mint_centered);
        evidenceNotice.setPadding(dp(12), dp(10), dp(12), dp(10));

        LinearLayout.LayoutParams evidenceLp =
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                );
        evidenceLp.setMargins(0, 0, 0, dp(12));
        evidenceNotice.setLayoutParams(evidenceLp);
        container.addView(evidenceNotice);

        for (MeasurementDefinition def : definitions) {
            Double value =
                    measurementView.calculate(def);

            if (value == null) continue;

            TextView row = new TextView(this);

            row.setText(
                    def.name +
                    "\n" +
                    String.format(
                            Locale.US,
                            "%.1f°",
                            value
                    ) +
                    "   ·   Referencia: " +
                    def.normText +
                    "\n" +
                    def.diagnosis(value)
            );

            row.setTextSize(13.5f);
            row.setTextColor(0xFF292631);
            row.setGravity(Gravity.CENTER);
            row.setTextAlignment(android.view.View.TEXT_ALIGNMENT_CENTER);

            row.setTypeface(
                    Typeface.DEFAULT,
                    Typeface.NORMAL
            );

            row.setBackgroundResource(
                    R.drawable.card_white
            );

            row.setPadding(
                    dp(14),
                    dp(12),
                    dp(14),
                    dp(12)
            );

            LinearLayout.LayoutParams lp =
                    new LinearLayout.LayoutParams(
                            ViewGroup.LayoutParams.MATCH_PARENT,
                            ViewGroup.LayoutParams.WRAP_CONTENT
                    );

            lp.setMargins(
                    0,
                    0,
                    0,
                    dp(10)
            );

            row.setLayoutParams(lp);

            container.addView(row);
        }

        if (!linearDefinitions.isEmpty()) {
            TextView linearTitle = new TextView(this);
            linearTitle.setText(linearSectionTitle());
            linearTitle.setTextColor(0xFF5B3FA4);
            linearTitle.setTextSize(15f);
            linearTitle.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
            linearTitle.setPadding(0, dp(8), 0, dp(8));
            container.addView(linearTitle);

            if (Double.isNaN(mmPerPixel) || mmPerPixel <= 0) {
                TextView warning = new TextView(this);
                warning.setText(
                        "Para obtener resultados en mm primero calibre la radiografía con una referencia de longitud conocida."
                );
                warning.setTextColor(0xFF7A4F00);
                warning.setTextSize(14f);
                warning.setBackgroundResource(R.drawable.button_soft_mint);
                warning.setPadding(dp(14), dp(12), dp(14), dp(12));
                container.addView(warning);

            } else {
                TextView calibration = new TextView(this);
                calibration.setText(
                        "Calibración: " +
                        calibrationLabel +
                        " · " +
                        String.format(Locale.US, "%.5f mm/píxel", mmPerPixel)
                );
                calibration.setTextColor(0xFF2C7E86);
                calibration.setTextSize(13f);
                calibration.setPadding(0, 0, 0, dp(8));
                container.addView(calibration);

                for (LinearMeasurementDefinition def : linearDefinitions) {
                    Double value = calculateLinear(def);
                    if (value == null) continue;

                    TextView row = new TextView(this);
                    row.setText(
                            def.name +
                            "\n" +
                            String.format(Locale.US, "%.2f mm", value) +
                            "   ·   Referencia: " +
                            linearNormText(def, value) +
                            "\n" +
                            linearDiagnosis(def, value)
                    );
                    row.setTextSize(13.5f);
                    row.setTextColor(0xFF292631);
                    row.setGravity(Gravity.CENTER);
                    row.setTextAlignment(android.view.View.TEXT_ALIGNMENT_CENTER);
                    row.setTypeface(Typeface.DEFAULT, Typeface.NORMAL);
                    row.setBackgroundResource(R.drawable.card_white);
                    row.setPadding(dp(14), dp(12), dp(14), dp(12));

                    LinearLayout.LayoutParams lp =
                            new LinearLayout.LayoutParams(
                                    ViewGroup.LayoutParams.MATCH_PARENT,
                                    ViewGroup.LayoutParams.WRAP_CONTENT
                            );
                    lp.setMargins(0, 0, 0, dp(10));
                    row.setLayoutParams(lp);

                    container.addView(row);
                }

                if ("LEVANDOSKI".equals(mode)) {
                    addLevandoskiSummary(container);
                }
            }
        }

        if ("TWEED".equals(mode)) {
            addTweedSummary(container);
        }

        TextView saveAnnotated =
                createDialogButton(
                        "GUARDAR RADIOGRAFÍA CON PUNTOS",
                        R.drawable.button_soft_mint,
                        0xFF15383D
                );

        saveAnnotated.setOnClickListener(v -> {
            Bitmap annotated =
                    measurementView
                            .renderAnnotatedBitmap();

            if (annotated == null) {
                Toast.makeText(
                        this,
                        "No se pudo preparar la imagen.",
                        Toast.LENGTH_SHORT
                ).show();

                return;
            }

            startSaveImage(
                    annotated,
                    safeFileName(
                            studyName +
                            "_puntos.png"
                    ),
                    REQ_SAVE_ANNOTATED
            );
        });

        container.addView(saveAnnotated);

        TextView saveReport =
                createDialogButton(
                        "GUARDAR INFORME COMO IMAGEN",
                        R.drawable.card_steiner,
                        Color.WHITE
                );

        saveReport.setOnClickListener(v -> {
            Bitmap report =
                    buildReportBitmap();

            if (report == null) {
                Toast.makeText(
                        this,
                        "No se pudo preparar el informe.",
                        Toast.LENGTH_SHORT
                ).show();

                return;
            }

            startSaveImage(
                    report,
                    safeFileName(
                            studyName +
                            "_informe.png"
                    ),
                    REQ_SAVE_REPORT
            );
        });

        container.addView(saveReport);

        new AlertDialog.Builder(this)
                .setTitle("Resultados · " + modeTitle())
                .setView(scroll)
                .setPositiveButton(
                        "Cerrar",
                        null
                )
                .show();
    }

    private String resultsSafetyNotice() {
        if ("AIRWAY".equals(mode)) {
            return "Interpretación cefalométrica orientativa. La telerradiografía lateral es una imagen 2D tomada despierto y no puede confirmar ni excluir obstrucción de vía aérea o apnea del sueño. Los valores se comparan con referencias publicadas o, cuando se indica, con la tabla docente aportada.";
        }

        if ("LEVANDOSKI".equals(mode)) {
            return "Interpretación orientativa para tamizaje de asimetría. La radiografía panorámica presenta magnificación y distorsión no uniformes; una discrepancia relevante debe correlacionarse clínicamente y confirmarse con un método apropiado cuando sea necesario.";
        }

        return "Interpretación cefalométrica orientativa. Los intervalos son referencias de análisis y poblaciones concretas; no sustituyen historia clínica, examen físico ni valoración profesional. Una sola medida no debe utilizarse como diagnóstico independiente.";
    }

    private boolean isProvidedAirwayTableReference(String name) {
        return name.startsWith("AD1")
                || name.startsWith("AD2")
                || name.startsWith("AD3");
    }

    private String linearSectionTitle() {
        if ("VERTEBRAL".equals(mode)) return "Medidas lineales · Rocabado";
        if ("LEVANDOSKI".equals(mode)) return "Medidas lineales · Levandoski";
        if ("AIRWAY".equals(mode)) return "Medidas lineales · Vía aérea";
        return "Medidas lineales";
    }

    private String linearNormText(
            LinearMeasurementDefinition def,
            double value
    ) {
        if (!"AIRWAY".equals(mode)) {
            return def.normText;
        }

        AirwayRef ref = airwayReference(def.name);

        if (ref == null) {
            if (isProvidedAirwayTableReference(def.name)) {
                return "Tabla docente aportada: referencia disponible solo para edades específicas";
            }

            if (def.name.startsWith("Faringe superior")) {
                int age = patientAgeYears();

                if (age > 0 && age < 18) {
                    return "McNamara: ≤5 mm = indicador de posible compromiso; la dimensión aumenta con la edad";
                }

                return "McNamara: adulto ≈17.4 mm; ≤5 mm = indicador de posible compromiso";
            }

            if (def.name.startsWith("Faringe posterior")) {
                return "McNamara: promedio ≈10–12 mm; >15 mm puede sugerir lengua anterior/tonsilas aumentadas";
            }

            return def.normText;
        }

        return String.format(
                Locale.US,
                "%.2f ± %.2f mm%s",
                ref.mean,
                ref.sd,
                isProvidedAirwayTableReference(def.name)
                        ? " · tabla docente aportada"
                        : " · referencia McNamara"
        );
    }

    private String linearDiagnosis(
            LinearMeasurementDefinition def,
            double value
    ) {
        if (!"AIRWAY".equals(mode)) {
            return def.diagnosis(value);
        }

        AirwayRef ref = airwayReference(def.name);

        if (isProvidedAirwayTableReference(def.name)) {
            if (ref == null) {
                return "Medida obtenida sin clasificación automática. Los valores AD1/AD2/AD3 conservan la tabla docente aportada, pero no se encontró evidencia suficiente para usarlos como umbrales diagnósticos individuales.";
            }

            double min = ref.mean - ref.sd;
            double max = ref.mean + ref.sd;

            String position =
                    value < min
                            ? "por debajo"
                            : value > max
                                    ? "por encima"
                                    : "dentro";

            return "La medida está " +
                    position +
                    " de ±1 DE de la referencia tabular aportada. " +
                    "No debe interpretarse como diagnóstico de hipertrofia adenoidea, obstrucción ni apnea del sueño.";
        }

        if (def.name.startsWith("Faringe superior")) {
            if (value <= 5.0) {
                return "≤5 mm: McNamara lo describió únicamente como indicador de posible compromiso de vía aérea superior. Requiere valoración clínica/otorrinolaringológica; no es un diagnóstico.";
            }

            return "Mayor de 5 mm. McNamara no considera esta medida aislada suficiente para diagnosticar normalidad respiratoria; una telerradiografía 2D tampoco confirma ni excluye apnea del sueño.";
        }

        if (def.name.startsWith("Faringe posterior")) {
            if (value > 15.0) {
                return ">15 mm: McNamara indicó que puede sugerir posición anterior de la lengua y/o aumento tonsilar. Es una asociación cefalométrica, no un diagnóstico.";
            }

            return "≤15 mm. McNamara señaló que una medida inferior al promedio en esta región no es, por sí sola, un hallazgo diagnóstico. Correlacionar clínicamente.";
        }

        if (ref == null) {
            return "Medida obtenida; no hay una referencia aplicable con los datos actuales. No se realiza clasificación diagnóstica.";
        }

        double min = ref.mean - ref.sd;
        double max = ref.mean + ref.sd;

        if (value >= min && value <= max) {
            return "Dentro de ±1 DE de la referencia disponible. Esto no descarta un trastorno respiratorio.";
        }

        return (
                value < min
                        ? "Por debajo"
                        : "Por encima"
        ) +
                " de ±1 DE de la referencia disponible. " +
                "Una telerradiografía lateral 2D no establece un diagnóstico respiratorio.";
    }

    private int patientAgeYears() {
        try {
            int age = Integer.parseInt(patientAge.trim());
            return age >= 1 && age <= 120 ? age : -1;
        } catch (Exception e) {
            return -1;
        }
    }

    private AirwayRef airwayReference(String name) {
        int age = patientAgeYears();

        boolean female = "Femenino".equals(patientSex);
        boolean male = "Masculino".equals(patientSex);

        // AD1/AD2/AD3: se conservan únicamente como referencias de la tabla
        // docente aportada por la usuaria; no se usan para diagnóstico.
        if (name.startsWith("AD1")) {
            if (!female && !male) return null;

            if (age == 6) {
                return female
                        ? new AirwayRef(20.66, 5.50)
                        : new AirwayRef(14.74, 5.69);
            }

            if (age == 16) {
                return female
                        ? new AirwayRef(26.48, 4.45)
                        : new AirwayRef(26.32, 4.28);
            }

            return null;
        }

        if (name.startsWith("AD2")) {
            if (!female && !male) return null;

            if (age == 6) {
                return female
                        ? new AirwayRef(15.89, 3.53)
                        : new AirwayRef(14.93, 3.52);
            }

            if (age == 16) {
                return female
                        ? new AirwayRef(22.44, 4.26)
                        : new AirwayRef(21.78, 4.67);
            }

            return null;
        }

        if (name.startsWith("AD3")) {
            if (age == 6) return new AirwayRef(7.02, 3.70);
            if (age == 16) return new AirwayRef(14.56, 4.70);
            return null;
        }

        // McNamara: mujeres primero en la tabla original (17.4±3.4;
        // 11.3±3.3) y hombres (17.4±4.3; 13.5±4.3).
        if (name.startsWith("Faringe superior")) {
            if (age < 18) return null;
            if (male) return new AirwayRef(17.4, 4.3);
            if (female) return new AirwayRef(17.4, 3.4);
            return null;
        }

        if (name.startsWith("Faringe posterior")) {
            if (age < 18) return null;
            if (male) return new AirwayRef(13.5, 4.3);
            if (female) return new AirwayRef(11.3, 3.3);
            return null;
        }

        return null;
    }

    private static class AirwayRef {
        final double mean;
        final double sd;

        AirwayRef(double mean, double sd) {
            this.mean = mean;
            this.sd = sd;
        }
    }

    private void addTweedSummary(LinearLayout container) {
        MeasurementDefinition fmaDef = null;

        for (MeasurementDefinition def : definitions) {
            if ("FMA".equals(def.name)) {
                fmaDef = def;
                break;
            }
        }

        if (fmaDef == null) return;

        Double fma = measurementView.calculate(fmaDef);
        if (fma == null) return;

        String description;

        if (fma < 20) {
            description = "FMA bajo respecto al intervalo clásico.";
        } else if (fma <= 30) {
            description = "FMA dentro del intervalo central clásico de Tweed.";
        } else {
            description = "FMA elevado respecto al intervalo central clásico.";
        }

        TextView summary = new TextView(this);

        summary.setText(
                "Triángulo de Tweed · referencia histórica\n" +
                String.format(Locale.US, "FMA %.1f° · %s", fma, description) +
                "\nFMA, FMIA e IMPA deben interpretarse en conjunto; no se muestra un «pronóstico» clínico automático."
        );

        summary.setTextSize(13.5f);
        summary.setTextColor(0xFF5B3FA4);
        summary.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        summary.setGravity(Gravity.CENTER);
        summary.setTextAlignment(android.view.View.TEXT_ALIGNMENT_CENTER);
        summary.setBackgroundResource(R.drawable.button_soft_mint_centered);
        summary.setPadding(dp(12), dp(10), dp(12), dp(10));

        LinearLayout.LayoutParams lp =
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                );

        lp.setMargins(0, dp(4), 0, dp(10));
        summary.setLayoutParams(lp);
        container.addView(summary);
    }

    private void addLevandoskiSummary(LinearLayout container) {
        TextView note = new TextView(this);
        note.setText(
                "Líneas medias: la tabla proporcionada indica observación de coincidencia, no una medida en mm. " +
                "YomCeph no asigna un umbral automático. Las panorámicas tienen magnificación y distorsión no uniformes; " +
                "las diferencias derecha/izquierda son orientativas y una asimetría relevante debe confirmarse clínicamente o con imagen apropiada."
        );
        note.setTextSize(12.5f);
        note.setTextColor(0xFF4A4652);
        note.setGravity(Gravity.CENTER);
        note.setTextAlignment(android.view.View.TEXT_ALIGNMENT_CENTER);
        note.setBackgroundResource(R.drawable.button_soft_mint_centered);
        note.setPadding(dp(10), dp(8), dp(10), dp(8));

        LinearLayout.LayoutParams noteLp =
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                );
        noteLp.setMargins(0, dp(4), 0, dp(10));
        note.setLayoutParams(noteLp);
        container.addView(note);

        TextView title = new TextView(this);
        title.setText("Comparación derecha / izquierda");
        title.setTextSize(16f);
        title.setTextColor(0xFF5B3FA4);
        title.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        title.setPadding(0, dp(8), 0, dp(6));
        container.addView(title);

        addLevPair(container, "Cóndilo-incisivo maxilar",
                "Cóndilo a incisivo central maxilar derecho",
                "Cóndilo a incisivo central maxilar izquierdo");

        addLevPair(container, "Cóndilo-incisivo mandibular",
                "Cóndilo a incisivo central mandibular derecho",
                "Cóndilo a incisivo central mandibular izquierdo");

        addLevPair(container, "Cóndilo-Gonion",
                "Cóndilo-Gonion derecho",
                "Cóndilo-Gonion izquierdo");

        addLevPair(container, "Gonion-Coronoides",
                "Gonion-Coronoides derecho",
                "Gonion-Coronoides izquierdo");

        addLevPair(container, "Línea media-Cóndilo",
                "Línea media a cóndilo derecho",
                "Línea media a cóndilo izquierdo");

        addLevPair(container, "Línea media-Cuerpo mandibular",
                "Línea media a cuerpo mandibular derecho",
                "Línea media a cuerpo mandibular izquierdo");

        addLevPair(container, "2º molar-Línea media",
                "Distal 2º molar derecho a línea media",
                "Distal 2º molar izquierdo a línea media");

        addLevPair(container, "Ancho de rama mandibular",
                "Ancho de rama mandibular derecha",
                "Ancho de rama mandibular izquierda");
    }

    private void addLevPair(
            LinearLayout container,
            String label,
            String rightName,
            String leftName
    ) {
        Double right = calculateLinearByName(rightName);
        Double left = calculateLinearByName(leftName);
        if (right == null || left == null) return;

        double diff = right - left;
        String conclusion;

        if (Math.abs(diff) < 0.005) {
            conclusion = "Las medidas coinciden";
        } else if (diff > 0) {
            conclusion = "Lado derecho mayor por " +
                    String.format(Locale.US, "%.2f mm", Math.abs(diff));
        } else {
            conclusion = "Lado izquierdo mayor por " +
                    String.format(Locale.US, "%.2f mm", Math.abs(diff));
        }

        TextView row = new TextView(this);
        row.setText(
                label + "\n" +
                String.format(Locale.US, "D %.2f mm · I %.2f mm\n%s", right, left, conclusion)
        );
        row.setTextSize(13f);
        row.setTextColor(0xFF3D3946);
        row.setGravity(Gravity.CENTER);
        row.setTextAlignment(android.view.View.TEXT_ALIGNMENT_CENTER);
        row.setBackgroundResource(R.drawable.button_soft_mint);
        row.setPadding(dp(10), dp(9), dp(10), dp(9));

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        );
        lp.setMargins(0, 0, 0, dp(7));
        row.setLayoutParams(lp);
        container.addView(row);
    }

    private Double calculateLinearByName(String name) {
        for (LinearMeasurementDefinition def : linearDefinitions) {
            if (name.equals(def.name)) {
                return calculateLinear(def);
            }
        }
        return null;
    }

    private String safeFileName(String name) {
        return name
                .replaceAll(
                        "[\\\\/:*?\"<>|]",
                        "_"
                );
    }

    private TextView createDialogButton(
            String text,
            int backgroundRes,
            int textColor
    ) {
        TextView button = new TextView(this);

        button.setText(text);
        button.setGravity(Gravity.CENTER);

        button.setTypeface(
                Typeface.DEFAULT,
                Typeface.BOLD
        );

        button.setTextSize(13f);
        button.setTextColor(textColor);

        button.setBackgroundResource(
                backgroundRes
        );

        button.setIncludeFontPadding(false);
        button.setPadding(0, 0, 0, 0);

        button.setClickable(true);
        button.setFocusable(true);

        LinearLayout.LayoutParams lp =
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        dp(54)
                );

        lp.setMargins(
                0,
                dp(6),
                0,
                dp(8)
        );

        button.setLayoutParams(lp);

        return button;
    }

    private Bitmap buildReportBitmap() {
        int width = 1400;
        int margin = 70;
        int titleHeight = 390;
        int rowHeight = 320;
        int footer = 125;

        int linearCount =
                (!linearDefinitions.isEmpty() &&
                 !Double.isNaN(mmPerPixel) &&
                 mmPerPixel > 0)
                        ? linearDefinitions.size()
                        : 0;

        int height =
                titleHeight +
                ((definitions.size() + linearCount) * rowHeight) +
                (linearCount > 0 ? 70 : 0) +
                footer;

        Bitmap bitmap =
                Bitmap.createBitmap(
                        width,
                        height,
                        Bitmap.Config.ARGB_8888
                );

        Canvas canvas =
                new Canvas(bitmap);

        canvas.drawColor(
                Color.rgb(
                        247,
                        245,
                        251
                )
        );

        Paint titlePaint =
                new Paint(
                        Paint.ANTI_ALIAS_FLAG
                );

        titlePaint.setColor(
                Color.rgb(
                        91,
                        63,
                        164
                )
        );

        titlePaint.setTypeface(
                Typeface.create(
                        Typeface.DEFAULT,
                        Typeface.BOLD
                )
        );

        titlePaint.setTextSize(58f);

        Paint subtitlePaint =
                new Paint(
                        Paint.ANTI_ALIAS_FLAG
                );

        subtitlePaint.setColor(
                Color.rgb(
                        44,
                        126,
                        134
                )
        );

        subtitlePaint.setTextSize(30f);

        Paint infoPaint =
                new Paint(
                        Paint.ANTI_ALIAS_FLAG
                );

        infoPaint.setColor(
                Color.rgb(
                        65,
                        61,
                        72
                )
        );

        infoPaint.setTextSize(27f);

        Paint namePaint =
                new Paint(
                        Paint.ANTI_ALIAS_FLAG
                );

        namePaint.setColor(
                Color.rgb(
                        91,
                        63,
                        164
                )
        );

        namePaint.setTypeface(
                Typeface.create(
                        Typeface.DEFAULT,
                        Typeface.BOLD
                )
        );

        namePaint.setTextSize(34f);

        Paint valuePaint =
                new Paint(
                        Paint.ANTI_ALIAS_FLAG
                );

        valuePaint.setColor(
                Color.rgb(
                        25,
                        25,
                        30
                )
        );

        valuePaint.setTypeface(
                Typeface.create(
                        Typeface.DEFAULT,
                        Typeface.BOLD
                )
        );

        valuePaint.setTextSize(34f);

        Paint detailPaint =
                new Paint(
                        Paint.ANTI_ALIAS_FLAG
                );

        detailPaint.setColor(
                Color.rgb(
                        65,
                        61,
                        72
                )
        );

        detailPaint.setTextSize(27f);

        Paint cardPaint =
                new Paint(
                        Paint.ANTI_ALIAS_FLAG
                );

        cardPaint.setColor(
                Color.WHITE
        );

        Paint strokePaint =
                new Paint(
                        Paint.ANTI_ALIAS_FLAG
                );

        strokePaint.setColor(
                Color.rgb(
                        205,
                        194,
                        231
                )
        );

        strokePaint.setStyle(
                Paint.Style.STROKE
        );

        strokePaint.setStrokeWidth(3f);

        canvas.drawText(
                "YomCeph",
                margin,
                72,
                titlePaint
        );

        canvas.drawText(
                "Informe · " + modeTitle(),
                margin,
                120,
                subtitlePaint
        );

        canvas.drawText(
                "Estudio: " +
                studyName,
                margin,
                165,
                infoPaint
        );

        canvas.drawText(
                "Paciente: " +
                (
                        patientName.trim().isEmpty()
                                ? "Sin nombre"
                                : patientName
                ) +
                (
                        patientAge.trim().isEmpty()
                                ? ""
                                : " · " +
                                patientAge +
                                " años"
                ) +
                (
                        patientSex.trim().isEmpty()
                                ? ""
                                : " · " + patientSex
                ),
                margin,
                205,
                infoPaint
        );

        if (!linearDefinitions.isEmpty() &&
                !Double.isNaN(mmPerPixel) &&
                mmPerPixel > 0) {
            canvas.drawText(
                    "Calibración: " +
                    calibrationLabel +
                    " · " +
                    String.format(Locale.US, "%.5f mm/píxel", mmPerPixel),
                    margin,
                    235,
                    infoPaint
            );
        }

        Paint safetyPaint =
                new Paint(Paint.ANTI_ALIAS_FLAG);
        safetyPaint.setColor(Color.rgb(95, 73, 25));
        safetyPaint.setTextSize(23f);

        drawWrappedText(
                canvas,
                resultsSafetyNotice(),
                margin,
                285,
                width - margin,
                safetyPaint,
                30f
        );

        int y = titleHeight;

        for (MeasurementDefinition def : definitions) {
            Double value =
                    measurementView.calculate(def);

            if (value == null) continue;

            float left = margin;
            float top = y;
            float right = width - margin;
            float bottom =
                    y + rowHeight - 18;

            android.graphics.RectF rect =
                    new android.graphics.RectF(
                            left,
                            top,
                            right,
                            bottom
                    );

            canvas.drawRoundRect(
                    rect,
                    30f,
                    30f,
                    cardPaint
            );

            canvas.drawRoundRect(
                    rect,
                    30f,
                    30f,
                    strokePaint
            );

            canvas.drawText(
                    def.name,
                    left + 30,
                    top + 46,
                    namePaint
            );

            String valueLine =
                    String.format(
                            Locale.US,
                            "%.1f°   ·   Referencia: %s",
                            value,
                            def.normText
                    );

            canvas.drawText(
                    valueLine,
                    left + 30,
                    top + 91,
                    valuePaint
            );

            drawWrappedText(
                    canvas,
                    def.diagnosis(value),
                    left + 30,
                    top + 132,
                    right - 30,
                    detailPaint,
                    34f
            );

            y += rowHeight;
        }

        if (!linearDefinitions.isEmpty() &&
                !Double.isNaN(mmPerPixel) &&
                mmPerPixel > 0) {

            y += 50;

            for (LinearMeasurementDefinition def : linearDefinitions) {
                Double value = calculateLinear(def);
                if (value == null) continue;

                float left = margin;
                float top = y;
                float right = width - margin;
                float bottom = y + rowHeight - 18;

                android.graphics.RectF rect =
                        new android.graphics.RectF(
                                left,
                                top,
                                right,
                                bottom
                        );

                canvas.drawRoundRect(
                        rect,
                        30f,
                        30f,
                        cardPaint
                );

                canvas.drawRoundRect(
                        rect,
                        30f,
                        30f,
                        strokePaint
                );

                canvas.drawText(
                        def.name,
                        left + 30,
                        top + 46,
                        namePaint
                );

                String valueLine =
                        String.format(
                                Locale.US,
                                "%.2f mm   ·   Referencia: %s",
                                value,
                                linearNormText(def, value)
                        );

                canvas.drawText(
                        valueLine,
                        left + 30,
                        top + 91,
                        valuePaint
                );

                drawWrappedText(
                        canvas,
                        linearDiagnosis(def, value),
                        left + 30,
                        top + 132,
                        right - 30,
                        detailPaint,
                        34f
                );

                y += rowHeight;
            }
        }

        Paint footerPaint =
                new Paint(
                        Paint.ANTI_ALIAS_FLAG
                );

        footerPaint.setColor(
                Color.rgb(
                        100,
                        91,
                        115
                )
        );

        footerPaint.setTextSize(24f);

        drawWrappedText(
                canvas,
                "Referencia educativa: interpretar junto con historia clínica y exploración. Una medida cefalométrica aislada no equivale a un diagnóstico.",
                margin,
                height - 78,
                width - margin,
                footerPaint,
                28f
        );

        return bitmap;
    }

    private void drawWrappedText(
            Canvas canvas,
            String text,
            float x,
            float y,
            float maxRight,
            Paint paint,
            float lineHeight
    ) {
        if (text == null
                || text.trim().isEmpty()) {
            return;
        }

        String[] words =
                text.split("\\s+");

        StringBuilder line =
                new StringBuilder();

        float currentY = y;

        for (String word : words) {
            String test =
                    line.length() == 0
                            ? word
                            : line + " " + word;

            if (x + paint.measureText(test) > maxRight
                    && line.length() > 0) {

                canvas.drawText(
                        line.toString(),
                        x,
                        currentY,
                        paint
                );

                line =
                        new StringBuilder(word);

                currentY += lineHeight;

            } else {
                line =
                        new StringBuilder(test);
            }
        }

        if (line.length() > 0) {
            canvas.drawText(
                    line.toString(),
                    x,
                    currentY,
                    paint
            );
        }
    }

    private void startSaveImage(
            Bitmap bitmap,
            String suggestedName,
            int requestCode
    ) {
        pendingSaveBitmap = bitmap;

        Intent intent =
                new Intent(
                        Intent.ACTION_CREATE_DOCUMENT
                );

        intent.addCategory(
                Intent.CATEGORY_OPENABLE
        );

        intent.setType("image/png");

        intent.putExtra(
                Intent.EXTRA_TITLE,
                suggestedName
        );

        startActivityForResult(
                intent,
                requestCode
        );
    }

    private void writePendingBitmap(
            Uri uri
    ) {
        if (pendingSaveBitmap == null
                || uri == null) {
            return;
        }

        try (
                OutputStream out =
                        getContentResolver()
                                .openOutputStream(uri)
        ) {
            if (out == null) {
                throw new IOException(
                        "No se pudo abrir el archivo de salida."
                );
            }

            boolean ok =
                    pendingSaveBitmap.compress(
                            Bitmap.CompressFormat.PNG,
                            100,
                            out
                    );

            out.flush();

            if (!ok) {
                throw new IOException(
                        "No se pudo codificar PNG."
                );
            }

            Toast.makeText(
                    this,
                    "Imagen guardada correctamente.",
                    Toast.LENGTH_LONG
            ).show();

        } catch (Exception e) {
            Toast.makeText(
                    this,
                    "No se pudo guardar la imagen.",
                    Toast.LENGTH_LONG
            ).show();

        } finally {
            if (pendingSaveBitmap != null
                    && !pendingSaveBitmap.isRecycled()) {
                pendingSaveBitmap.recycle();
            }

            pendingSaveBitmap = null;
        }
    }

    private int dp(int value) {
        return Math.round(
                value *
                getResources()
                        .getDisplayMetrics()
                        .density
        );
    }

    private void openImage() {
        Intent intent =
                new Intent(
                        Intent.ACTION_OPEN_DOCUMENT
                );

        intent.addCategory(
                Intent.CATEGORY_OPENABLE
        );

        intent.setType("image/*");
        intent.addFlags(
                Intent.FLAG_GRANT_READ_URI_PERMISSION |
                Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION
        );

        startActivityForResult(
                intent,
                REQ_IMAGE
        );
    }

    @Override
    protected void onActivityResult(
            int requestCode,
            int resultCode,
            Intent data
    ) {
        super.onActivityResult(
                requestCode,
                resultCode,
                data
        );

        if (requestCode == REQ_SAVE_ANNOTATED
                || requestCode == REQ_SAVE_REPORT) {

            if (resultCode == RESULT_OK
                    && data != null
                    && data.getData() != null) {

                writePendingBitmap(
                        data.getData()
                );

            } else {
                if (pendingSaveBitmap != null
                        && !pendingSaveBitmap.isRecycled()) {

                    pendingSaveBitmap.recycle();
                }

                pendingSaveBitmap = null;
            }

            return;
        }

        if (requestCode != REQ_IMAGE
                || resultCode != RESULT_OK
                || data == null
                || data.getData() == null) {
            return;
        }

        Uri uri = data.getData();

        try {
            if ((data.getFlags() & Intent.FLAG_GRANT_READ_URI_PERMISSION) != 0) {
                getContentResolver()
                        .takePersistableUriPermission(
                                uri,
                                Intent.FLAG_GRANT_READ_URI_PERMISSION
                        );
            }
        } catch (Exception ignored) {
        }

        try {
            Bitmap bitmap =
                    decodeSampledBitmap(
                            uri,
                            4096
                    );

            if (bitmap == null) {
                throw new IOException(
                        "Bitmap nulo"
                );
            }

            bitmap =
                    applyExifRotation(
                            uri,
                            bitmap
                    );

            measurementView.setLocked(false);
            updateLockButton();

            measurementView.setBitmap(bitmap);
            measurementView.resetMeasurement();

            imageUriString =
                    uri.toString();

            studyId =
                    SavedStudyStore.newId();

            studyName =
                    SavedStudyStore
                            .suggestedStudyName(this);

            patientName = "";
            patientAge = "";
            patientSex = "";
            mmPerPixel = Double.NaN;
            calibrationLabel = "";

            updateStudyInfo();
            updateCalibrationStatus();
            showStudyDetailsDialog(true);

        } catch (Exception e) {
            Toast.makeText(
                    this,
                    "No se pudo abrir la imagen.",
                    Toast.LENGTH_LONG
            ).show();
        }
    }

    private Bitmap decodeSampledBitmap(
            Uri uri,
            int maxDimension
    ) throws IOException {

        BitmapFactory.Options bounds =
                new BitmapFactory.Options();

        bounds.inJustDecodeBounds = true;

        try (
                InputStream in =
                        getContentResolver()
                                .openInputStream(uri)
        ) {
            BitmapFactory.decodeStream(
                    in,
                    null,
                    bounds
            );
        }

        int sample = 1;

        int max =
                Math.max(
                        bounds.outWidth,
                        bounds.outHeight
                );

        while (max / sample > maxDimension) {
            sample *= 2;
        }

        BitmapFactory.Options opts =
                new BitmapFactory.Options();

        opts.inSampleSize = sample;
        opts.inPreferredConfig =
                Bitmap.Config.ARGB_8888;

        try (
                InputStream in =
                        getContentResolver()
                                .openInputStream(uri)
        ) {
            return BitmapFactory.decodeStream(
                    in,
                    null,
                    opts
            );
        }
    }

    private Bitmap applyExifRotation(
            Uri uri,
            Bitmap bitmap
    ) {
        try (
                InputStream in =
                        getContentResolver()
                                .openInputStream(uri)
        ) {
            ExifInterface exif =
                    new ExifInterface(in);

            int rotationDegrees =
                    exif.getRotationDegrees();

            boolean flipped =
                    exif.isFlipped();

            if (rotationDegrees == 0 && !flipped) {
                return bitmap;
            }

            Matrix matrix =
                    new Matrix();

            // ExifInterface define la orientación como espejo horizontal
            // primero y rotación después.
            if (flipped) {
                matrix.postScale(-1f, 1f);
            }

            if (rotationDegrees != 0) {
                matrix.postRotate(rotationDegrees);
            }

            Bitmap corrected =
                    Bitmap.createBitmap(
                            bitmap,
                            0,
                            0,
                            bitmap.getWidth(),
                            bitmap.getHeight(),
                            matrix,
                            true
                    );

            if (corrected != bitmap
                    && !bitmap.isRecycled()) {
                bitmap.recycle();
            }

            return corrected;

        } catch (Exception e) {
            return bitmap;
        }
    }
}

