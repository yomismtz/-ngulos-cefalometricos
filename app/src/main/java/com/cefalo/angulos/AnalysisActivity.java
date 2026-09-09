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
import android.media.ExifInterface;
import android.net.Uri;
import android.os.Bundle;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.text.InputType;
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
    private TextView btnCalculate;
    private TextView btnLock;
    private TextView txtStudyMeta;
    private LinearLayout pointChips;

    private List<MeasurementDefinition> definitions;
    private List<String> landmarks;

    private String mode;
    private String studyId;
    private String imageUriString;
    private String studyName = "";
    private String patientName = "";
    private String patientAge = "";
    private SavedStudyStore.StudyData restoredStudy;
    private boolean restoring = false;

    private Bitmap pendingSaveBitmap;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        studyId = getIntent().getStringExtra("STUDY_ID");
        if (studyId != null) {
            restoredStudy = SavedStudyStore.load(this, studyId);
        }

        if (restoredStudy != null) {
            mode = restoredStudy.mode;
        } else {
            mode = getIntent().getStringExtra("MODE");
            if (mode == null) mode = "STEINER";
        }

        setContentView(R.layout.activity_analysis);

        boolean vertebral = "VERTEBRAL".equals(mode);

        definitions = vertebral
                ? MeasurementCatalog.vertebral()
                : MeasurementCatalog.steiner();

        landmarks = buildLandmarkList(definitions);

        TextView txtTitle = findViewById(R.id.txtTitle);
        txtTitle.setText(vertebral
                ? "Análisis vertebral"
                : "Análisis de Steiner");

        measurementView = findViewById(R.id.measurementView);
        txtProgress = findViewById(R.id.txtProgress);
        txtInstruction = findViewById(R.id.txtInstruction);
        btnCalculate = findViewById(R.id.btnCalculate);
        btnLock = findViewById(R.id.btnLock);
        txtStudyMeta = findViewById(R.id.txtStudyMeta);
        pointChips = findViewById(R.id.pointChips);

        measurementView.setLandmarks(landmarks);
        measurementView.setProgressListener(this::updateProgress);

        findViewById(R.id.btnBack).setOnClickListener(v -> finish());
        findViewById(R.id.btnOpen).setOnClickListener(v -> openImage());
        findViewById(R.id.btnUndo).setOnClickListener(v -> measurementView.undo());
        findViewById(R.id.btnReset).setOnClickListener(v -> {
            if (measurementView.isLocked()) {
                Toast.makeText(this, "Desbloquee el trazado para borrar puntos.", Toast.LENGTH_SHORT).show();
                return;
            }
            new AlertDialog.Builder(this)
                    .setTitle("Borrar puntos")
                    .setMessage("¿Desea borrar todos los puntos de este análisis?")
                    .setNegativeButton("Cancelar", null)
                    .setPositiveButton("Borrar", (dialog, which) -> measurementView.resetMeasurement())
                    .show();
        });
        findViewById(R.id.btnFit).setOnClickListener(v -> measurementView.fitImage());

        findViewById(R.id.btnPrevious).setOnClickListener(v -> measurementView.selectPrevious());
        findViewById(R.id.btnNext).setOnClickListener(v -> measurementView.selectNext());
        findViewById(R.id.btnPointHelp).setOnClickListener(v -> showCurrentPointGuide());
        findViewById(R.id.btnSaveStudy).setOnClickListener(v -> saveStudy(false));
        findViewById(R.id.btnStudyData).setOnClickListener(v -> showStudyDataDialog(false));
        findViewById(R.id.btnAssisted).setOnClickListener(v -> showAssistedDetectionInfo());

        btnLock.setOnClickListener(v -> toggleLock());
        btnCalculate.setOnClickListener(v -> calculateFullAnalysis());

        txtInstruction.setText(
                "Mantenga el dedo sobre la radiografía para usar la lupa. " +
                "Puede elegir cualquier punto en la lista, usar Anterior/Siguiente y volver a marcarlo. " +
                "Los estudios se guardan dentro de la app."
        );

        refreshPointChips();
        updateStudyMeta();

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

    private List<String> buildLandmarkList(List<MeasurementDefinition> defs) {
        Set<String> ordered = new LinkedHashSet<>();

        for (MeasurementDefinition def : defs) {
            for (String label : def.pointLabels) {
                ordered.add(label);
            }
        }

        return new ArrayList<>(ordered);
    }

    private void restoreStudy(SavedStudyStore.StudyData study) {
        if (study.imageUri == null) return;

        restoring = true;
        imageUriString = study.imageUri;
        studyName = safe(study.studyName);
        patientName = safe(study.patientName);
        patientAge = safe(study.patientAge);
        updateStudyMeta();

        try {
            Uri uri = Uri.parse(imageUriString);
            Bitmap bitmap = decodeSampledBitmap(uri, 4096);

            if (bitmap == null) throw new IOException("Bitmap nulo");

            bitmap = applyExifRotation(uri, bitmap);
            measurementView.setBitmap(bitmap);
            measurementView.setPoints(mapSavedPoints(study));
            measurementView.setLocked(study.locked);
            updateLockButton();

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

    private List<PointF> mapSavedPoints(SavedStudyStore.StudyData study) {
        List<PointF> mapped = new ArrayList<>();

        for (String currentLabel : landmarks) {
            int savedIndex = study.labels.indexOf(currentLabel);

            if (savedIndex >= 0 && savedIndex < study.points.size()) {
                PointF p = study.points.get(savedIndex);
                mapped.add(p == null ? null : new PointF(p.x, p.y));
            } else {
                mapped.add(null);
            }
        }

        return mapped;
    }

    private void updateProgress(int placed, int total, String currentLabel) {
        refreshPointChips();

        if (total == 0) {
            txtProgress.setText("No hay puntos definidos.");
            btnCalculate.setAlpha(0.45f);
            return;
        }

        int selected = measurementView.getSelectedIndex();
        boolean selectedPlaced = measurementView.hasPointAt(selected);

        if (placed >= total) {
            txtProgress.setText(
                    "✓ Puntos completos: " + placed + " / " + total +
                    "\nPUNTO SELECCIONADO: " + currentLabel +
                    (measurementView.isLocked()
                            ? "   ·   trazado bloqueado"
                            : "   ·   toque la radiografía para corregirlo")
            );
            btnCalculate.setAlpha(1f);
        } else {
            txtProgress.setText(
                    "Puntos: " + placed + " / " + total +
                    "\nPUNTO SELECCIONADO: " + currentLabel +
                    (selectedPlaced ? " ✓  ·  toque la radiografía para recolocarlo" : " —  ·  márquelo en la radiografía")
            );
            btnCalculate.setAlpha(0.55f);
        }

        if (!restoring) {
            saveStudy(true);
        }
    }

    private void refreshPointChips() {
        if (pointChips == null || landmarks == null) return;

        pointChips.removeAllViews();
        int selected = measurementView == null ? -1 : measurementView.getSelectedIndex();

        for (int i = 0; i < landmarks.size(); i++) {
            final int index = i;
            String label = landmarks.get(i);
            boolean placed = measurementView != null && measurementView.hasPointAt(i);
            boolean isSelected = i == selected;

            TextView chip = new TextView(this);
            chip.setText(label + (placed ? "  ✓" : "  —"));
            chip.setTextSize(13f);
            chip.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
            chip.setGravity(Gravity.CENTER);
            chip.setPadding(dp(12), dp(8), dp(12), dp(8));
            chip.setClickable(true);
            chip.setFocusable(true);

            if (isSelected) {
                chip.setBackgroundResource(R.drawable.chip_selected_outline);
                chip.setTextColor(0xFF5B3FA4);
                chip.setCompoundDrawablesWithIntrinsicBounds(R.drawable.ic_pointer, 0, 0, 0);
                chip.setCompoundDrawablePadding(dp(4));
            } else if (placed) {
                chip.setBackgroundResource(R.drawable.button_soft_mint);
                chip.setTextColor(0xFF15383D);
            } else {
                chip.setBackgroundResource(R.drawable.button_soft_purple);
                chip.setTextColor(0xFF5B3FA4);
            }

            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.WRAP_CONTENT,
                    dp(42)
            );
            lp.setMargins(0, 0, dp(7), 0);
            chip.setLayoutParams(lp);

            chip.setOnClickListener(v -> {
                measurementView.setSelectedIndex(index, true);
            });

            pointChips.addView(chip);
        }
    }

    private void showCurrentPointGuide() {
        String label = measurementView.getCurrentLabel();

        if (label == null) {
            Toast.makeText(this, "No hay un punto seleccionado.", Toast.LENGTH_SHORT).show();
            return;
        }

        showPointGuide(label);
    }

    private void showPointGuide(String label) {
        String status = measurementView.hasPointAt(landmarks.indexOf(label))
                ? "\n\nEste punto ya está colocado. Puede arrastrarlo o tocar otra posición para reemplazarlo."
                : "\n\nEste punto todavía no está colocado.";

        new AlertDialog.Builder(this)
                .setTitle("¿Dónde está " + label + "?")
                .setMessage(PointGuide.description(label) + status)
                .setPositiveButton("Entendido", null)
                .show();
    }

    private void showAssistedDetectionInfo() {
        new AlertDialog.Builder(this)
                .setTitle("Detección asistida")
                .setMessage(
                        "La detección automática de puntos queda preparada como función futura. " +
                        "Cuando se incorpore, la app solo propondrá la posición: cada punto tendrá que ser confirmado o corregido antes de calcular el análisis.\n\n" +
                        "En esta versión, la ayuda disponible es la lupa de precisión y la guía anatómica de cada punto."
                )
                .setPositiveButton("Entendido", null)
                .show();
    }

    private void toggleLock() {
        if (!measurementView.isLocked() && !measurementView.isComplete()) {
            Toast.makeText(
                    this,
                    "Complete todos los puntos antes de bloquear el trazado.",
                    Toast.LENGTH_LONG
            ).show();
            return;
        }

        measurementView.setLocked(!measurementView.isLocked());
        updateLockButton();
        saveStudy(true);
    }

    private void updateLockButton() {
        if (measurementView.isLocked()) {
            btnLock.setText("🔒 DESBLOQUEAR");
            btnLock.setBackgroundResource(R.drawable.button_soft_mint);
            btnLock.setTextColor(0xFF15383D);
        } else {
            btnLock.setText("🔓 BLOQUEAR TRAZADO");
            btnLock.setBackgroundResource(R.drawable.button_soft_purple);
            btnLock.setTextColor(0xFF5B3FA4);
        }
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
            studyId = SavedStudyStore.newId();
        }

        SavedStudyStore.StudyData study = new SavedStudyStore.StudyData();
        study.id = studyId;
        study.mode = mode;
        study.imageUri = imageUriString;
        study.studyName = studyName;
        study.patientName = patientName;
        study.patientAge = patientAge;
        study.locked = measurementView.isLocked();
        study.labels = new ArrayList<>(landmarks);
        study.points = measurementView.getPointsSnapshot();

        SavedStudyStore.save(this, study);

        if (!silent) {
            Toast.makeText(
                    this,
                    "Estudio guardado en Mis análisis.",
                    Toast.LENGTH_LONG
            ).show();
        }
    }

    private void calculateFullAnalysis() {
        if (!measurementView.hasBitmap()) {
            Toast.makeText(this, "Primero abra una radiografía.", Toast.LENGTH_SHORT).show();
            return;
        }

        if (!measurementView.isComplete()) {
            String next = measurementView.getCurrentLabel();
            Toast.makeText(
                    this,
                    "Faltan puntos. Seleccionado: " + (next == null ? "—" : next),
                    Toast.LENGTH_LONG
            ).show();
            return;
        }

        saveStudy(true);
        showResultsDialog();
    }

    private void showResultsDialog() {
        ScrollView scroll = new ScrollView(this);

        LinearLayout container = new LinearLayout(this);
        container.setOrientation(LinearLayout.VERTICAL);
        int pad = dp(18);
        container.setPadding(pad, pad, pad, pad);
        scroll.addView(container);

        TextView intro = new TextView(this);
        intro.setText(
                "Resultados calculados con los mismos puntos anatómicos. " +
                "Puede cerrar esta ventana, desbloquear el trazado, corregir un punto y volver a calcular."
        );
        intro.setTextSize(14f);
        intro.setTextColor(0xFF4A4652);
        intro.setPadding(0, 0, 0, dp(12));
        container.addView(intro);

        for (MeasurementDefinition def : definitions) {
            Double value = measurementView.calculate(def);
            if (value == null) continue;

            TextView row = new TextView(this);
            row.setText(
                    def.name + "\n" +
                    String.format(Locale.US, "%.1f°", value) +
                    "   ·   Norma: " + def.normText + "\n" +
                    def.diagnosis(value)
            );
            row.setTextSize(15f);
            row.setTextColor(0xFF292631);
            row.setTypeface(Typeface.DEFAULT, Typeface.NORMAL);
            row.setBackgroundResource(R.drawable.card_white);
            row.setPadding(dp(14), dp(12), dp(14), dp(12));

            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT
            );
            lp.setMargins(0, 0, 0, dp(10));
            row.setLayoutParams(lp);

            container.addView(row);
        }

        TextView saveAnnotated = createDialogButton(
                "GUARDAR RADIOGRAFÍA CON PUNTOS",
                R.drawable.button_soft_mint,
                0xFF15383D
        );
        saveAnnotated.setOnClickListener(v -> {
            Bitmap annotated = measurementView.renderAnnotatedBitmap();
            if (annotated == null) {
                Toast.makeText(this, "No se pudo preparar la imagen.", Toast.LENGTH_SHORT).show();
                return;
            }

            startSaveImage(
                    annotated,
                    safeFileName(studyName.length() == 0 ? "YomCephalometrics_radiografia" : studyName) + "_puntos.png",
                    REQ_SAVE_ANNOTATED
            );
        });
        container.addView(saveAnnotated);

        TextView saveReport = createDialogButton(
                "GUARDAR INFORME COMO IMAGEN",
                R.drawable.card_steiner,
                Color.WHITE
        );
        saveReport.setOnClickListener(v -> {
            Bitmap report = buildReportBitmap();
            if (report == null) {
                Toast.makeText(this, "No se pudo preparar el informe.", Toast.LENGTH_SHORT).show();
                return;
            }

            startSaveImage(
                    report,
                    "VERTEBRAL".equals(mode)
                            ? safeFileName(studyName.length() == 0 ? "YomCephalometrics" : studyName) + "_informe_vertebral.png"
                            : safeFileName(studyName.length() == 0 ? "YomCephalometrics" : studyName) + "_informe_steiner.png",
                    REQ_SAVE_REPORT
            );
        });
        container.addView(saveReport);

        new AlertDialog.Builder(this)
                .setTitle("VERTEBRAL".equals(mode)
                        ? "Resultados · Vertebral"
                        : "Resultados · Steiner")
                .setView(scroll)
                .setPositiveButton("Cerrar", null)
                .show();
    }

    private TextView createDialogButton(String text, int backgroundRes, int textColor) {
        TextView button = new TextView(this);
        button.setText(text);
        button.setGravity(Gravity.CENTER);
        button.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        button.setTextSize(15f);
        button.setTextColor(textColor);
        button.setBackgroundResource(backgroundRes);
        button.setPadding(dp(14), dp(14), dp(14), dp(14));
        button.setClickable(true);
        button.setFocusable(true);

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                dp(54)
        );
        lp.setMargins(0, dp(6), 0, dp(8));
        button.setLayoutParams(lp);

        return button;
    }

    private Bitmap buildReportBitmap() {
        int width = 1400;
        int margin = 70;
        int titleHeight = 165;
        int rowHeight = 180;
        int footer = 70;

        int height = titleHeight + (definitions.size() * rowHeight) + footer;

        Bitmap bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas(bitmap);
        canvas.drawColor(Color.rgb(247, 245, 251));

        Paint titlePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        titlePaint.setColor(Color.rgb(91, 63, 164));
        titlePaint.setTypeface(Typeface.create(Typeface.DEFAULT, Typeface.BOLD));
        titlePaint.setTextSize(58f);

        Paint subtitlePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        subtitlePaint.setColor(Color.rgb(44, 126, 134));
        subtitlePaint.setTextSize(30f);

        Paint namePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        namePaint.setColor(Color.rgb(91, 63, 164));
        namePaint.setTypeface(Typeface.create(Typeface.DEFAULT, Typeface.BOLD));
        namePaint.setTextSize(34f);

        Paint valuePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        valuePaint.setColor(Color.rgb(25, 25, 30));
        valuePaint.setTypeface(Typeface.create(Typeface.DEFAULT, Typeface.BOLD));
        valuePaint.setTextSize(34f);

        Paint detailPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        detailPaint.setColor(Color.rgb(65, 61, 72));
        detailPaint.setTextSize(27f);

        Paint cardPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        cardPaint.setColor(Color.WHITE);

        Paint strokePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        strokePaint.setColor(Color.rgb(205, 194, 231));
        strokePaint.setStyle(Paint.Style.STROKE);
        strokePaint.setStrokeWidth(3f);

        canvas.drawText("YomCephalometrics", margin, 72, titlePaint);
        canvas.drawText(
                "VERTEBRAL".equals(mode)
                        ? "Informe de análisis vertebral / craneocervical"
                        : "Informe de análisis de Steiner",
                margin,
                120,
                subtitlePaint
        );

        String patientLine = (studyName.length() == 0 ? "Estudio" : studyName);
        if (patientName.length() > 0) patientLine += " · Paciente: " + patientName;
        if (patientAge.length() > 0) patientLine += " · Edad: " + patientAge;
        subtitlePaint.setTextSize(25f);
        canvas.drawText(patientLine, margin, 154, subtitlePaint);

        int y = titleHeight + 24;

        for (MeasurementDefinition def : definitions) {
            Double value = measurementView.calculate(def);
            if (value == null) continue;

            float left = margin;
            float top = y;
            float right = width - margin;
            float bottom = y + rowHeight - 18;

            android.graphics.RectF rect =
                    new android.graphics.RectF(left, top, right, bottom);

            canvas.drawRoundRect(rect, 30f, 30f, cardPaint);
            canvas.drawRoundRect(rect, 30f, 30f, strokePaint);

            canvas.drawText(def.name, left + 30, top + 46, namePaint);

            String valueLine = String.format(
                    Locale.US,
                    "%.1f°   ·   Norma: %s",
                    value,
                    def.normText
            );

            canvas.drawText(valueLine, left + 30, top + 91, valuePaint);

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

        Paint footerPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        footerPaint.setColor(Color.rgb(100, 91, 115));
        footerPaint.setTextSize(24f);

        canvas.drawText(
                "Resultados angulares calculados a partir de los puntos marcados en la radiografía.",
                margin,
                height - 28,
                footerPaint
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
        if (text == null || text.trim().isEmpty()) return;

        String[] words = text.split("\\s+");
        StringBuilder line = new StringBuilder();
        float currentY = y;

        for (String word : words) {
            String test = line.length() == 0
                    ? word
                    : line + " " + word;

            if (x + paint.measureText(test) > maxRight
                    && line.length() > 0) {
                canvas.drawText(line.toString(), x, currentY, paint);
                line = new StringBuilder(word);
                currentY += lineHeight;
            } else {
                line = new StringBuilder(test);
            }
        }

        if (line.length() > 0) {
            canvas.drawText(line.toString(), x, currentY, paint);
        }
    }

    private void startSaveImage(
            Bitmap bitmap,
            String suggestedName,
            int requestCode
    ) {
        pendingSaveBitmap = bitmap;

        Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("image/png");
        intent.putExtra(Intent.EXTRA_TITLE, suggestedName);

        startActivityForResult(intent, requestCode);
    }

    private void writePendingBitmap(Uri uri) {
        if (pendingSaveBitmap == null || uri == null) return;

        try (OutputStream out = getContentResolver().openOutputStream(uri)) {
            if (out == null) {
                throw new IOException("No se pudo abrir el archivo de salida.");
            }

            boolean ok = pendingSaveBitmap.compress(
                    Bitmap.CompressFormat.PNG,
                    100,
                    out
            );

            out.flush();

            if (!ok) {
                throw new IOException("No se pudo codificar PNG.");
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

    private void showStudyDataDialog(boolean firstTime) {
        LinearLayout form = new LinearLayout(this);
        form.setOrientation(LinearLayout.VERTICAL);
        form.setPadding(dp(20), dp(8), dp(20), 0);

        EditText studyInput = new EditText(this);
        studyInput.setHint("Nombre del estudio (ej. Radiografía 1)");
        studyInput.setSingleLine(true);
        studyInput.setText(studyName);
        form.addView(studyInput);

        EditText patientInput = new EditText(this);
        patientInput.setHint("Nombre del paciente");
        patientInput.setSingleLine(true);
        patientInput.setText(patientName);
        form.addView(patientInput);

        EditText ageInput = new EditText(this);
        ageInput.setHint("Edad");
        ageInput.setSingleLine(true);
        ageInput.setInputType(InputType.TYPE_CLASS_NUMBER);
        ageInput.setText(patientAge);
        form.addView(ageInput);

        AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle("Datos del estudio")
                .setMessage("Estos datos sirven para identificar la radiografía en Mis análisis.")
                .setView(form)
                .setNegativeButton(firstTime ? "Después" : "Cancelar", null)
                .setPositiveButton("Guardar", null)
                .create();

        dialog.setOnShowListener(d -> dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            String newStudyName = studyInput.getText().toString().trim();
            if (newStudyName.length() == 0) {
                studyInput.setError("Escriba un nombre para el estudio.");
                return;
            }

            studyName = newStudyName;
            patientName = patientInput.getText().toString().trim();
            patientAge = ageInput.getText().toString().trim();

            updateStudyMeta();
            saveStudy(true);
            dialog.dismiss();
        }));

        dialog.setOnDismissListener(d -> {
            if (firstTime && studyName.length() == 0) {
                studyName = "Estudio " + (SavedStudyStore.list(this).size() + 1);
                updateStudyMeta();
            }
            saveStudy(true);
        });

        dialog.show();
    }

    private void updateStudyMeta() {
        if (txtStudyMeta == null) return;

        String title = studyName.length() == 0 ? "Estudio sin nombre" : studyName;
        String details = "";

        if (patientName.length() > 0) {
            details += "Paciente: " + patientName;
        }

        if (patientAge.length() > 0) {
            if (details.length() > 0) details += "   ·   ";
            details += "Edad: " + patientAge;
        }

        txtStudyMeta.setText(details.length() == 0 ? title : title + "\n" + details);
    }

    private String safe(String value) {
        return value == null ? "" : value;
    }

    private String safeFileName(String value) {
        String cleaned = value.replaceAll("[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ_-]+", "_");
        return cleaned.length() == 0 ? "YomCephalometrics" : cleaned;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    private void openImage() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("image/*");
        startActivityForResult(intent, REQ_IMAGE);
    }

    @Override
    protected void onActivityResult(
            int requestCode,
            int resultCode,
            Intent data
    ) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == REQ_SAVE_ANNOTATED
                || requestCode == REQ_SAVE_REPORT) {
            if (resultCode == RESULT_OK
                    && data != null
                    && data.getData() != null) {
                writePendingBitmap(data.getData());
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
            getContentResolver().takePersistableUriPermission(
                    uri,
                    Intent.FLAG_GRANT_READ_URI_PERMISSION
            );
        } catch (Exception ignored) {
        }

        try {
            Bitmap bitmap = decodeSampledBitmap(uri, 4096);

            if (bitmap == null) {
                throw new IOException("Bitmap nulo");
            }

            bitmap = applyExifRotation(uri, bitmap);

            measurementView.setLocked(false);
            updateLockButton();
            measurementView.setBitmap(bitmap);
            measurementView.resetMeasurement();

            imageUriString = uri.toString();
            if (studyId == null) studyId = SavedStudyStore.newId();
            if (studyName.length() == 0) {
                studyName = "Estudio " + (SavedStudyStore.list(this).size() + 1);
            }
            updateStudyMeta();
            showStudyDataDialog(true);

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
        BitmapFactory.Options bounds = new BitmapFactory.Options();
        bounds.inJustDecodeBounds = true;

        try (InputStream in =
                     getContentResolver().openInputStream(uri)) {
            BitmapFactory.decodeStream(in, null, bounds);
        }

        int sample = 1;
        int max = Math.max(bounds.outWidth, bounds.outHeight);

        while (max / sample > maxDimension) {
            sample *= 2;
        }

        BitmapFactory.Options opts = new BitmapFactory.Options();
        opts.inSampleSize = sample;
        opts.inPreferredConfig = Bitmap.Config.ARGB_8888;

        try (InputStream in =
                     getContentResolver().openInputStream(uri)) {
            return BitmapFactory.decodeStream(in, null, opts);
        }
    }

    private Bitmap applyExifRotation(Uri uri, Bitmap bitmap) {
        try (InputStream in =
                     getContentResolver().openInputStream(uri)) {

            ExifInterface exif = new ExifInterface(in);

            int orientation = exif.getAttributeInt(
                    ExifInterface.TAG_ORIENTATION,
                    ExifInterface.ORIENTATION_NORMAL
            );

            float degrees = 0f;

            if (orientation == ExifInterface.ORIENTATION_ROTATE_90) {
                degrees = 90f;
            } else if (orientation == ExifInterface.ORIENTATION_ROTATE_180) {
                degrees = 180f;
            } else if (orientation == ExifInterface.ORIENTATION_ROTATE_270) {
                degrees = 270f;
            }

            if (degrees == 0f) {
                return bitmap;
            }

            Matrix matrix = new Matrix();
            matrix.postRotate(degrees);

            return Bitmap.createBitmap(
                    bitmap,
                    0,
                    0,
                    bitmap.getWidth(),
                    bitmap.getHeight(),
                    matrix,
                    true
            );

        } catch (Exception e) {
            return bitmap;
        }
    }
}
