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
import android.graphics.Typeface;
import android.media.ExifInterface;
import android.net.Uri;
import android.os.Bundle;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
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

    private List<MeasurementDefinition> definitions;
    private List<String> landmarks;
    private boolean vertebral;

    private Bitmap pendingSaveBitmap;
    private int pendingSaveRequest = -1;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_analysis);

        String mode = getIntent().getStringExtra("MODE");
        vertebral = "VERTEBRAL".equals(mode);

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

        measurementView.setLandmarks(landmarks);
        measurementView.setProgressListener(this::updateProgress);

        findViewById(R.id.btnBack).setOnClickListener(v -> finish());
        findViewById(R.id.btnOpen).setOnClickListener(v -> openImage());
        findViewById(R.id.btnUndo).setOnClickListener(v -> measurementView.undo());
        findViewById(R.id.btnReset).setOnClickListener(v -> measurementView.resetMeasurement());
        findViewById(R.id.btnFit).setOnClickListener(v -> measurementView.fitImage());

        btnCalculate.setOnClickListener(v -> calculateFullAnalysis());

        txtInstruction.setText(
                "1. Abra la radiografía.\n" +
                "2. Marque cada punto una sola vez, en el orden indicado.\n" +
                "3. Puede arrastrar cualquier punto para corregirlo.\n" +
                "4. Use dos dedos para mover y ampliar.\n" +
                "5. Al terminar pulse CALCULAR ANÁLISIS."
        );

        updateProgress(0, landmarks.size(), landmarks.isEmpty() ? null : landmarks.get(0));
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

    private void updateProgress(int placed, int total, String nextLabel) {
        if (total == 0) {
            txtProgress.setText("No hay puntos definidos.");
            btnCalculate.setAlpha(0.45f);
            return;
        }

        if (placed >= total) {
            txtProgress.setText(
                    "✓ Puntos completos: " + placed + " / " + total +
                    "\nRevise los puntos y pulse CALCULAR ANÁLISIS."
            );
            btnCalculate.setAlpha(1f);
        } else {
            txtProgress.setText(
                    "Punto " + (placed + 1) + " de " + total +
                    ":  " + nextLabel
            );
            btnCalculate.setAlpha(0.55f);
        }
    }

    private void calculateFullAnalysis() {
        if (!measurementView.hasBitmap()) {
            Toast.makeText(this, "Primero abra una radiografía.", Toast.LENGTH_SHORT).show();
            return;
        }

        if (!measurementView.isComplete()) {
            String next = measurementView.getNextLabel();
            Toast.makeText(
                    this,
                    "Faltan puntos. Siguiente: " + (next == null ? "—" : next),
                    Toast.LENGTH_LONG
            ).show();
            return;
        }

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
                "Puede corregir un punto y volver a calcular."
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
                    "YomCephalometrics_radiografia_puntos.png",
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
                    vertebral
                            ? "YomCephalometrics_informe_vertebral.png"
                            : "YomCephalometrics_informe_steiner.png",
                    REQ_SAVE_REPORT
            );
        });
        container.addView(saveReport);

        new AlertDialog.Builder(this)
                .setTitle(vertebral
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
        button.setTextStyle(Typeface.BOLD);
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
                vertebral ? "Informe de análisis vertebral / craneocervical" : "Informe de análisis de Steiner",
                margin,
                120,
                subtitlePaint
        );

        int y = titleHeight;

        for (MeasurementDefinition def : definitions) {
            Double value = measurementView.calculate(def);
            if (value == null) continue;

            float left = margin;
            float top = y;
            float right = width - margin;
            float bottom = y + rowHeight - 18;

            android.graphics.RectF rect = new android.graphics.RectF(left, top, right, bottom);
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

            if (x + paint.measureText(test) > maxRight && line.length() > 0) {
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

    private void startSaveImage(Bitmap bitmap, String suggestedName, int requestCode) {
        pendingSaveBitmap = bitmap;
        pendingSaveRequest = requestCode;

        Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("image/png");
        intent.putExtra(Intent.EXTRA_TITLE, suggestedName);

        startActivityForResult(intent, requestCode);
    }

    private void writePendingBitmap(Uri uri) {
        if (pendingSaveBitmap == null || uri == null) return;

        try (OutputStream out = getContentResolver().openOutputStream(uri)) {
            if (out == null) throw new IOException("No se pudo abrir el archivo de salida.");

            boolean ok = pendingSaveBitmap.compress(Bitmap.CompressFormat.PNG, 100, out);
            out.flush();

            if (!ok) throw new IOException("No se pudo codificar PNG.");

            Toast.makeText(this, "Imagen guardada correctamente.", Toast.LENGTH_LONG).show();

        } catch (Exception e) {
            Toast.makeText(
                    this,
                    "No se pudo guardar la imagen.",
                    Toast.LENGTH_LONG
            ).show();

        } finally {
            if (pendingSaveBitmap != null && !pendingSaveBitmap.isRecycled()) {
                pendingSaveBitmap.recycle();
            }
            pendingSaveBitmap = null;
            pendingSaveRequest = -1;
        }
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
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == REQ_SAVE_ANNOTATED || requestCode == REQ_SAVE_REPORT) {
            if (resultCode == RESULT_OK && data != null && data.getData() != null) {
                writePendingBitmap(data.getData());
            } else {
                if (pendingSaveBitmap != null && !pendingSaveBitmap.isRecycled()) {
                    pendingSaveBitmap.recycle();
                }
                pendingSaveBitmap = null;
                pendingSaveRequest = -1;
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
            measurementView.setBitmap(bitmap);

        } catch (Exception e) {
            Toast.makeText(
                    this,
                    "No se pudo abrir la imagen.",
                    Toast.LENGTH_LONG
            ).show();
        }
    }

    private Bitmap decodeSampledBitmap(Uri uri, int maxDimension) throws IOException {
        BitmapFactory.Options bounds = new BitmapFactory.Options();
        bounds.inJustDecodeBounds = true;

        try (InputStream in = getContentResolver().openInputStream(uri)) {
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

        try (InputStream in = getContentResolver().openInputStream(uri)) {
            return BitmapFactory.decodeStream(in, null, opts);
        }
    }

    private Bitmap applyExifRotation(Uri uri, Bitmap bitmap) {
        try (InputStream in = getContentResolver().openInputStream(uri)) {
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
