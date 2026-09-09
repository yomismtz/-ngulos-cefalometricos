package com.cefalo.angulos;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.media.ExifInterface;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import java.io.IOException;
import java.io.InputStream;
import java.util.List;
import java.util.Locale;

public class AnalysisActivity extends Activity {
    private static final int REQ_IMAGE = 1001;
    private MeasurementView measurementView;
    private TextView txtNorm, txtInstruction, txtResult, txtDiagnosis;
    private Spinner spinner;
    private List<MeasurementDefinition> definitions;
    private MeasurementDefinition current;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_analysis);

        String mode = getIntent().getStringExtra("MODE");
        boolean vertebral = "VERTEBRAL".equals(mode);
        definitions = vertebral ? MeasurementCatalog.vertebral() : MeasurementCatalog.steiner();

        TextView txtTitle = findViewById(R.id.txtTitle);
        txtTitle.setText(vertebral ? "Análisis vertebral" : "Análisis de Steiner");

        measurementView = findViewById(R.id.measurementView);
        txtNorm = findViewById(R.id.txtNorm);
        txtInstruction = findViewById(R.id.txtInstruction);
        txtResult = findViewById(R.id.txtResult);
        txtDiagnosis = findViewById(R.id.txtDiagnosis);
        spinner = findViewById(R.id.spinnerMeasurement);

        ArrayAdapter<MeasurementDefinition> adapter = new ArrayAdapter<>(this,
                android.R.layout.simple_spinner_item, definitions);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinner.setAdapter(adapter);

        spinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                current = definitions.get(position);
                txtNorm.setText("Norma: " + current.normText);
                txtInstruction.setText(current.instruction + "\nToque para marcar. Arrastre un punto para corregirlo. Use dos dedos para mover/zoom.");
                measurementView.setDefinition(current);
                updateResult(null);
            }
            @Override public void onNothingSelected(AdapterView<?> parent) {}
        });

        measurementView.setResultListener(this::updateResult);

        findViewById(R.id.btnBack).setOnClickListener(v -> finish());
        findViewById(R.id.btnOpen).setOnClickListener(v -> openImage());
        findViewById(R.id.btnUndo).setOnClickListener(v -> measurementView.undo());
        findViewById(R.id.btnReset).setOnClickListener(v -> measurementView.resetMeasurement());
        findViewById(R.id.btnFit).setOnClickListener(v -> measurementView.fitImage());
    }

    private void updateResult(Double angle) {
        if (angle == null || current == null) {
            txtResult.setText("Resultado: —");
            txtDiagnosis.setText("Diagnóstico: —");
            return;
        }
        txtResult.setText(String.format(Locale.US, "Resultado: %.1f°", angle));
        txtDiagnosis.setText("Diagnóstico: " + current.diagnosis(angle));
    }

    private void openImage() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("image/*");
        startActivityForResult(intent, REQ_IMAGE);
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != REQ_IMAGE || resultCode != RESULT_OK || data == null || data.getData() == null) return;
        Uri uri = data.getData();
        try {
            getContentResolver().takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION);
        } catch (Exception ignored) {}
        try {
            Bitmap bitmap = decodeSampledBitmap(uri, 4096);
            if (bitmap == null) throw new IOException("Bitmap nulo");
            bitmap = applyExifRotation(uri, bitmap);
            measurementView.setBitmap(bitmap);
        } catch (Exception e) {
            Toast.makeText(this, "No se pudo abrir la imagen", Toast.LENGTH_LONG).show();
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
        while (max / sample > maxDimension) sample *= 2;
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
            int o = exif.getAttributeInt(ExifInterface.TAG_ORIENTATION, ExifInterface.ORIENTATION_NORMAL);
            float degrees = 0f;
            if (o == ExifInterface.ORIENTATION_ROTATE_90) degrees = 90f;
            else if (o == ExifInterface.ORIENTATION_ROTATE_180) degrees = 180f;
            else if (o == ExifInterface.ORIENTATION_ROTATE_270) degrees = 270f;
            if (degrees == 0f) return bitmap;
            Matrix m = new Matrix();
            m.postRotate(degrees);
            return Bitmap.createBitmap(bitmap, 0, 0, bitmap.getWidth(), bitmap.getHeight(), m, true);
        } catch (Exception e) {
            return bitmap;
        }
    }
}
