package com.cefalo.angulos;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.graphics.Typeface;
import android.media.ExifInterface;
import android.net.Uri;
import android.os.Bundle;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

public class AnalysisActivity extends Activity {

    private static final int REQ_IMAGE = 1001;

    private MeasurementView measurementView;
    private TextView txtProgress;
    private TextView txtInstruction;
    private TextView btnCalculate;

    private List<MeasurementDefinition> definitions;
    private List<String> landmarks;
    private boolean vertebral;

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
                "Puede cerrar esta ventana, corregir un punto y volver a calcular."
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

        new AlertDialog.Builder(this)
                .setTitle(vertebral
                        ? "Resultados · Vertebral"
                        : "Resultados · Steiner")
                .setView(scroll)
                .setPositiveButton("Cerrar", null)
                .show();
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
