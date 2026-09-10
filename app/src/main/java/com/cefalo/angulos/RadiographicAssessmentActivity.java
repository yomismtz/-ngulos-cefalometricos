package com.cefalo.angulos;

import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.net.Uri;
import android.os.Bundle;
import android.provider.OpenableColumns;
import android.text.InputType;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.exifinterface.media.ExifInterface;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * Mobile-first qualitative/ordinal assessments for radiographs that do not
 * belong in the free-landmark angle engine.
 */
public class RadiographicAssessmentActivity extends AppCompatActivity {
    public static final String EXTRA_MODE = "ASSESSMENT_MODE";
    public static final String MODE_CVM = "CVM";
    public static final String MODE_NOLLA = "NOLLA";
    public static final String MODE_RESORPTION = "RESORPTION";
    public static final String MODE_PANO_REVIEW = "PANO_REVIEW";

    private static final int REQ_IMAGE = 4101;

    private String mode;
    private String imageUriString;
    private RadiographImageView imageView;
    private LinearLayout content;
    private TextView txtResult;
    private TextView txtImageName;

    // CVM
    private Spinner spC2Concavity;
    private Spinner spC3Concavity;
    private Spinner spC4Concavity;
    private Spinner spC3Shape;
    private Spinner spC4Shape;

    // Nolla
    private Spinner spNollaSex;
    private Spinner spNollaArch;
    private Spinner spNollaSide;
    private final List<TextView> nollaToothLabels = new ArrayList<>();
    private final List<EditText> nollaScores = new ArrayList<>();
    private EditText edtChronYears;
    private EditText edtChronMonths;

    // Root resorption
    private Spinner spPrimaryTooth;
    private Spinner spResorption;
    private final LinkedHashMap<String, String> resorptionRecords = new LinkedHashMap<>();

    // Pano review
    private final LinkedHashMap<String, CheckBox> panoChecks = new LinkedHashMap<>();
    private EditText edtPanoNotes;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        mode = getIntent().getStringExtra(EXTRA_MODE);
        if (mode == null) mode = MODE_CVM;
        if (savedInstanceState != null) {
            imageUriString = savedInstanceState.getString("IMAGE_URI");
        }
        buildUi();
        if (imageUriString != null) restoreImage(Uri.parse(imageUriString));
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        outState.putString("IMAGE_URI", imageUriString);
    }

    private void buildUi() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundResource(R.drawable.bg_home);
        root.setPadding(dp(12), dp(10), dp(12), dp(16));

        LinearLayout header = new LinearLayout(this);
        header.setOrientation(LinearLayout.HORIZONTAL);
        header.setGravity(Gravity.CENTER_VERTICAL);

        TextView back = makeButton("←", true);
        LinearLayout.LayoutParams backLp = new LinearLayout.LayoutParams(dp(52), dp(48));
        backLp.setMargins(0, 0, dp(8), 0);
        header.addView(back, backLp);
        back.setContentDescription("Volver");
        back.setOnClickListener(v -> finish());

        TextView title = new TextView(this);
        title.setText(modeTitle());
        title.setTextSize(20f);
        title.setTextColor(getColor(R.color.text_primary));
        title.setTypeface(null, android.graphics.Typeface.BOLD);
        title.setGravity(Gravity.CENTER_VERTICAL);
        header.addView(title, new LinearLayout.LayoutParams(0, dp(48), 1f));
        root.addView(header);

        txtImageName = new TextView(this);
        txtImageName.setText("Sin radiografía seleccionada");
        txtImageName.setTextSize(12f);
        txtImageName.setTextColor(getColor(R.color.text_secondary));
        txtImageName.setGravity(Gravity.CENTER);
        txtImageName.setPadding(dp(6), dp(4), dp(6), dp(6));
        root.addView(txtImageName, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        ));

        imageView = new RadiographImageView(this);
        imageView.setBackgroundColor(getColor(R.color.analysis_panel));
        root.addView(imageView, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                dp(260)
        ));

        LinearLayout imageActions = new LinearLayout(this);
        imageActions.setOrientation(LinearLayout.HORIZONTAL);
        imageActions.setGravity(Gravity.CENTER);
        imageActions.setPadding(0, dp(8), 0, dp(8));

        TextView open = makeButton("ABRIR RADIOGRAFÍA", false);
        open.setOnClickListener(v -> openImage());
        imageActions.addView(open, weightedButtonParams());

        TextView fit = makeButton("CENTRAR", true);
        fit.setOnClickListener(v -> imageView.fitImage());
        imageActions.addView(fit, weightedButtonParams());
        root.addView(imageActions);

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(false);
        content = new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        content.setPadding(dp(2), dp(4), dp(2), dp(26));
        scroll.addView(content, new ScrollView.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        ));
        root.addView(scroll, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                0,
                1f
        ));

        setContentView(root);
        renderMode();
    }

    private void renderMode() {
        content.removeAllViews();
        addInfoCard(modeIntro());
        if (MODE_CVM.equals(mode)) {
            renderCvm();
        } else if (MODE_NOLLA.equals(mode)) {
            renderNolla();
        } else if (MODE_RESORPTION.equals(mode)) {
            renderResorption();
        } else {
            renderPanoramicReview();
        }
    }

    private void renderCvm() {
        addSection("1 · Concavidad del borde inferior");
        addSmallText("Observe solamente C2, C3 y C4. Marque «presente» solo cuando la concavidad inferior sea clara.");
        spC2Concavity = addSpinnerRow("C2", new String[]{"Plano / sin concavidad", "Concavidad presente"});
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
        spC3Shape = addSpinnerRow("C3", shapes);
        spC4Shape = addSpinnerRow("C4", shapes);

        TextView calculate = makeButton("DETERMINAR CS1–CS6", false);
        calculate.setOnClickListener(v -> calculateCvm());
        content.addView(calculate, fullButtonParams());

        txtResult = addResultCard();
        txtResult.setText("Seleccione los criterios de C2-C4. Si la imagen es ambigua, la app no forzará una etapa.");

        addInfoCard(
                "Guía rápida verificada:\n" +
                "CS1: C2-C4 planos; C3-C4 trapezoidales.\n" +
                "CS2: concavidad solo en C2; C3-C4 trapezoidales.\n" +
                "CS3: concavidad en C2-C3; C4 plana; C3-C4 trapezoidales o rectangulares horizontales.\n" +
                "CS4: concavidad C2-C4; C3-C4 rectangulares horizontales.\n" +
                "CS5: concavidad C2-C4; al menos una de C3/C4 cuadrada.\n" +
                "CS6: concavidad C2-C4; al menos una de C3/C4 rectangular vertical."
        );
    }

    private void calculateCvm() {
        RadiographicAssessmentLogic.CvmResult result =
                RadiographicAssessmentLogic.classifyCvm(
                        spC2Concavity.getSelectedItemPosition() == 1,
                        spC3Concavity.getSelectedItemPosition() == 1,
                        spC4Concavity.getSelectedItemPosition() == 1,
                        shapeFromPosition(spC3Shape.getSelectedItemPosition()),
                        shapeFromPosition(spC4Shape.getSelectedItemPosition())
                );
        txtResult.setText(
                result.stage + "\n\n" + result.summary +
                "\n\nInterpretación: estimación de maduración esquelética; no equivale a edad cronológica y debe correlacionarse con el contexto clínico."
        );
    }

    private RadiographicAssessmentLogic.VertebralShape shapeFromPosition(int position) {
        switch (position) {
            case 0: return RadiographicAssessmentLogic.VertebralShape.TRAPEZOID;
            case 1: return RadiographicAssessmentLogic.VertebralShape.RECTANGULAR_HORIZONTAL;
            case 2: return RadiographicAssessmentLogic.VertebralShape.SQUARE;
            case 3: return RadiographicAssessmentLogic.VertebralShape.RECTANGULAR_VERTICAL;
            default: return RadiographicAssessmentLogic.VertebralShape.UNKNOWN;
        }
    }

    private void renderNolla() {
        addSection("Datos de referencia");
        spNollaSex = addSpinnerRow("Sexo", new String[]{"Masculino", "Femenino"});
        spNollaArch = addSpinnerRow("Arcada", new String[]{"Mandibular", "Maxilar"});
        spNollaSide = addSpinnerRow("Lado", new String[]{"Izquierdo", "Derecho"});

        View.OnClickListener labelsUpdater = v -> updateNollaLabels();
        spNollaArch.setOnItemSelectedListener(new SimpleItemSelectedListener(this::updateNollaLabels));
        spNollaSide.setOnItemSelectedListener(new SimpleItemSelectedListener(this::updateNollaLabels));

        addSmallText(
                "Se evalúan 7 dientes permanentes de un cuadrante, excluyendo el tercer molar. La referencia original usa tablas separadas por sexo y arcada. Si un diente del lado elegido no puede valorarse, el homólogo contralateral puede servir como sustituto cuando sea clínicamente apropiado."
        );

        addSection("Etapas de Nolla");
        addSmallText("Ingrese 0–10. Si está entre dos etapas puede usar los incrementos recomendados .2, .5 o .7 (ej.: 7.5). Toque CALCULAR al terminar.");

        nollaToothLabels.clear();
        nollaScores.clear();
        for (int i = 0; i < 7; i++) {
            LinearLayout row = new LinearLayout(this);
            row.setOrientation(LinearLayout.HORIZONTAL);
            row.setGravity(Gravity.CENTER_VERTICAL);
            row.setPadding(0, dp(3), 0, dp(3));

            TextView tooth = new TextView(this);
            tooth.setTextSize(14f);
            tooth.setTypeface(null, android.graphics.Typeface.BOLD);
            tooth.setTextColor(getColor(R.color.text_primary));
            nollaToothLabels.add(tooth);
            row.addView(tooth, new LinearLayout.LayoutParams(0, dp(48), 1f));

            EditText score = new EditText(this);
            score.setHint("0–10");
            score.setSingleLine(true);
            score.setGravity(Gravity.CENTER);
            score.setInputType(InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_DECIMAL);
            score.setTextSize(15f);
            nollaScores.add(score);
            row.addView(score, new LinearLayout.LayoutParams(dp(96), dp(48)));
            content.addView(row);
        }
        updateNollaLabels();

        addSection("Edad cronológica (opcional)");
        LinearLayout ageRow = new LinearLayout(this);
        ageRow.setOrientation(LinearLayout.HORIZONTAL);
        ageRow.setGravity(Gravity.CENTER_VERTICAL);
        edtChronYears = numericField("años");
        edtChronMonths = numericField("meses");
        ageRow.addView(edtChronYears, new LinearLayout.LayoutParams(0, dp(48), 1f));
        LinearLayout.LayoutParams monthLp = new LinearLayout.LayoutParams(0, dp(48), 1f);
        monthLp.setMargins(dp(8), 0, 0, 0);
        ageRow.addView(edtChronMonths, monthLp);
        content.addView(ageRow);

        TextView stageGuide = makeButton("VER GUÍA DE ETAPAS 0–10", true);
        stageGuide.setOnClickListener(v -> showNollaGuide());
        content.addView(stageGuide, fullButtonParams());

        TextView calculate = makeButton("CALCULAR EDAD DENTAL ESTIMADA", false);
        calculate.setOnClickListener(v -> calculateNolla());
        content.addView(calculate, fullButtonParams());

        txtResult = addResultCard();
        txtResult.setText("El resultado aparecerá aquí. La edad dental será una estimación interpolada a partir de la tabla de Nolla, no una edad cronológica exacta.");
    }

    private void updateNollaLabels() {
        if (spNollaArch == null || spNollaSide == null || nollaToothLabels.size() != 7) return;
        boolean maxillary = spNollaArch.getSelectedItemPosition() == 1;
        boolean right = spNollaSide.getSelectedItemPosition() == 1;
        int[] teeth;
        if (maxillary && !right) teeth = new int[]{21,22,23,24,25,26,27};
        else if (maxillary) teeth = new int[]{11,12,13,14,15,16,17};
        else if (!right) teeth = new int[]{31,32,33,34,35,36,37};
        else teeth = new int[]{41,42,43,44,45,46,47};
        for (int i = 0; i < teeth.length; i++) {
            nollaToothLabels.get(i).setText("OD " + teeth[i]);
        }
    }

    private void calculateNolla() {
        double sum = 0.0;
        for (int i = 0; i < nollaScores.size(); i++) {
            String raw = nollaScores.get(i).getText().toString().trim().replace(',', '.');
            if (raw.isEmpty()) {
                Toast.makeText(this, "Falta la etapa de " + nollaToothLabels.get(i).getText(), Toast.LENGTH_LONG).show();
                return;
            }
            double value;
            try {
                value = Double.parseDouble(raw);
            } catch (NumberFormatException e) {
                Toast.makeText(this, "Valor no válido en " + nollaToothLabels.get(i).getText(), Toast.LENGTH_LONG).show();
                return;
            }
            if (!RadiographicAssessmentLogic.isValidNollaScore(value)) {
                Toast.makeText(this, "Use etapas enteras o fracciones .2, .5 o .7 en " + nollaToothLabels.get(i).getText(), Toast.LENGTH_LONG).show();
                return;
            }
            sum += value;
        }

        boolean female = spNollaSex.getSelectedItemPosition() == 1;
        boolean maxillary = spNollaArch.getSelectedItemPosition() == 1;
        double age = RadiographicAssessmentLogic.estimateNollaAge(female, maxillary, sum);

        StringBuilder result = new StringBuilder();
        result.append(String.format(Locale.US, "Puntaje de 7 dientes: %.1f\n", sum));
        result.append("Edad dental estimada: ")
                .append(RadiographicAssessmentLogic.formatDentalAge(age));

        String yearsRaw = edtChronYears.getText().toString().trim();
        if (!yearsRaw.isEmpty() && !Double.isNaN(age)) {
            try {
                int years = Integer.parseInt(yearsRaw);
                int months = 0;
                String monthsRaw = edtChronMonths.getText().toString().trim();
                if (!monthsRaw.isEmpty()) months = Integer.parseInt(monthsRaw);
                if (months < 0 || months > 11) throw new NumberFormatException();
                double chronological = years + months / 12.0;
                double differenceMonths = (age - chronological) * 12.0;
                result.append(String.format(
                        Locale.US,
                        "\nDiferencia respecto a edad cronológica: %+.1f meses",
                        differenceMonths
                ));
                result.append("\nEsta diferencia describe maduración dental relativa; no diagnostica por sí sola adelanto o retraso patológico.");
            } catch (NumberFormatException ignored) {
                result.append("\nEdad cronológica no válida; se omitió la comparación.");
            }
        }

        result.append("\n\nReferencia: tablas de Nolla por sexo y arcada. La exactitud puede variar entre poblaciones y observadores.");
        txtResult.setText(result.toString());
    }

    private void showNollaGuide() {
        StringBuilder b = new StringBuilder();
        for (int i = 0; i <= 10; i++) {
            if (i > 0) b.append("\n");
            b.append(RadiographicAssessmentLogic.nollaStageDescription(i));
        }
        new androidx.appcompat.app.AlertDialog.Builder(this)
                .setTitle("Etapas de Nolla")
                .setMessage(b.toString())
                .setPositiveButton("Cerrar", null)
                .show();
    }

    private void renderResorption() {
        addSection("Registro por diente temporal");
        String[] teeth = {
                "55","54","53","52","51","61","62","63","64","65",
                "85","84","83","82","81","71","72","73","74","75"
        };
        spPrimaryTooth = addSpinnerRow("OD temporal", teeth);
        String[] stages = {
                "Sin reabsorción evidente",
                "Reabsorción inicial",
                "≈ 1/4 de raíz reabsorbida",
                "≈ 1/2 de raíz reabsorbida",
                "≈ 3/4 de raíz reabsorbida",
                "Reabsorción prácticamente completa / exfoliación"
        };
        spResorption = addSpinnerRow("Estadio", stages);

        addSmallText(
                "Se utiliza una descripción morfológica por fracciones para no presentar como «Moorrees» la simplificación porcentual 67–99 / 34–66 / 0–33 % del documento. Moorrees, Fanning y Hunt publicaron estudios de formación y reabsorción, y las adaptaciones radiográficas posteriores suelen expresar la reabsorción por cuartos."
        );

        TextView add = makeButton("AÑADIR / ACTUALIZAR DIENTE", false);
        add.setOnClickListener(v -> addResorptionRecord());
        content.addView(add, fullButtonParams());

        TextView clear = makeButton("LIMPIAR REGISTRO", true);
        clear.setOnClickListener(v -> {
            resorptionRecords.clear();
            updateResorptionResult();
        });
        content.addView(clear, fullButtonParams());

        txtResult = addResultCard();
        updateResorptionResult();
    }

    private void addResorptionRecord() {
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

    private void updateResorptionResult() {
        if (txtResult == null) return;
        if (resorptionRecords.isEmpty()) {
            txtResult.setText("Aún no hay dientes registrados.");
            return;
        }
        StringBuilder b = new StringBuilder("Registro de reabsorción radicular temporal\n");
        for (Map.Entry<String, String> entry : resorptionRecords.entrySet()) {
            b.append("\nOD ").append(entry.getKey()).append(" · ")
                    .append(shortResorption(entry.getValue()))
                    .append("\n")
                    .append(RadiographicAssessmentLogic.resorptionInterpretation(entry.getValue()))
                    .append("\n");
        }
        b.append("\nUso educativo: correlacionar con movilidad, sucesor permanente y espacio disponible.");
        txtResult.setText(b.toString());
    }

    private String shortResorption(String key) {
        switch (key) {
            case "SIN_REABSORCION": return "sin reabsorción evidente";
            case "INICIAL": return "reabsorción inicial";
            case "R1_4": return "≈1/4";
            case "R1_2": return "≈1/2";
            case "R3_4": return "≈3/4";
            default: return "prácticamente completa/exfoliación";
        }
    }

    private void renderPanoramicReview() {
        addSmallText("Esta pantalla guía una lectura sistemática de la panorámica. No identifica lesiones automáticamente: registra lo observado por el usuario y evita que la revisión se limite solo a los dientes.");

        addSection("Calidad y posicionamiento");
        addPanoCheck("ROTACION", "Rotación/asimetría de posicionamiento aparente");
        addPanoCheck("INCLINACION", "Cabeza inclinada / plano oclusal distorsionado");
        addPanoCheck("MOVIMIENTO", "Movimiento o pérdida de nitidez");
        addPanoCheck("LENGUA", "Espacio palatogloso por lengua baja");
        addPanoCheck("ARTEFACTO", "Artefactos o superposiciones relevantes");

        addSection("Dentición y desarrollo");
        addPanoCheck("AUSENCIAS", "Dientes ausentes que requieren correlación clínica");
        addPanoCheck("SUPERNUM", "Posible diente supernumerario");
        addPanoCheck("ECTOPICA", "Trayectoria eruptiva ectópica / alterada");
        addPanoCheck("RETENCION", "Retención, inclusión o impactación");
        addPanoCheck("TRANSPOS", "Transposición / inclinación / rotación llamativa");
        addPanoCheck("APIÑAMIENTO", "Apiñamiento o falta de espacio aparente");

        addSection("Hueso y estructuras vecinas");
        addPanoCheck("RADIOLUCIDA", "Imagen radiolúcida que requiere descripción");
        addPanoCheck("RADIOPACA", "Imagen radiopaca que requiere descripción");
        addPanoCheck("SENOS", "Asimetría/opacificación de senos maxilares a correlacionar");
        addPanoCheck("CONDILOS", "Diferencia morfológica condilar llamativa");
        addPanoCheck("OTRO", "Otro hallazgo fuera de la región dentoalveolar");

        addSection("Notas / localización");
        edtPanoNotes = new EditText(this);
        edtPanoNotes.setHint("Ej.: radiolucidez unilocular bien delimitada en región... / OD relacionado...");
        edtPanoNotes.setMinLines(3);
        edtPanoNotes.setGravity(Gravity.TOP | Gravity.START);
        edtPanoNotes.setTextSize(14f);
        content.addView(edtPanoNotes, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        ));

        TextView generate = makeButton("GENERAR RESUMEN SISTEMÁTICO", false);
        generate.setOnClickListener(v -> generatePanoSummary());
        content.addView(generate, fullButtonParams());

        txtResult = addResultCard();
        txtResult.setText("Marque únicamente hallazgos observados y genere el resumen.");
    }

    private void addPanoCheck(String key, String label) {
        CheckBox cb = new CheckBox(this);
        cb.setText(label);
        cb.setTextSize(14f);
        cb.setTextColor(getColor(R.color.text_primary));
        cb.setPadding(dp(4), dp(4), dp(4), dp(4));
        panoChecks.put(key, cb);
        content.addView(cb, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        ));
    }

    private void generatePanoSummary() {
        List<String> selected = new ArrayList<>();
        for (Map.Entry<String, CheckBox> e : panoChecks.entrySet()) {
            if (e.getValue().isChecked()) selected.add(e.getValue().getText().toString());
        }

        StringBuilder b = new StringBuilder("Evaluación panorámica integral\n\n");
        if (selected.isEmpty()) {
            b.append("No se marcaron alteraciones radiográficas evidentes en esta revisión guiada.");
        } else {
            b.append("Hallazgos registrados:\n");
            for (String item : selected) b.append("• ").append(item).append("\n");
        }

        String notes = edtPanoNotes.getText().toString().trim();
        if (!notes.isEmpty()) b.append("\nObservaciones: ").append(notes);

        b.append("\n\nLimitaciones: la panorámica presenta magnificación, distorsión, superposición e imágenes fantasma. Los hallazgos deben correlacionarse con historia clínica/exploración y, cuando sea necesario, con estudios complementarios.");
        txtResult.setText(b.toString());
    }

    private void addInfoCard(String text) {
        TextView card = new TextView(this);
        card.setText(text);
        card.setTextSize(13f);
        card.setTextColor(getColor(R.color.text_primary));
        card.setBackgroundResource(R.drawable.button_soft_mint_centered);
        card.setPadding(dp(14), dp(12), dp(14), dp(12));
        card.setGravity(Gravity.START | Gravity.CENTER_VERTICAL);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        );
        lp.setMargins(0, dp(6), 0, dp(10));
        content.addView(card, lp);
    }

    private void addSection(String title) {
        TextView tv = new TextView(this);
        tv.setText(title);
        tv.setTextSize(16f);
        tv.setTypeface(null, android.graphics.Typeface.BOLD);
        tv.setTextColor(getColor(R.color.brand_purple));
        tv.setPadding(dp(2), dp(10), dp(2), dp(5));
        content.addView(tv);
    }

    private void addSmallText(String text) {
        TextView tv = new TextView(this);
        tv.setText(text);
        tv.setTextSize(12.5f);
        tv.setTextColor(getColor(R.color.text_secondary));
        tv.setPadding(dp(2), dp(2), dp(2), dp(7));
        content.addView(tv);
    }

    private Spinner addSpinnerRow(String label, String[] options) {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(Gravity.CENTER_VERTICAL);
        row.setPadding(0, dp(3), 0, dp(3));

        TextView tv = new TextView(this);
        tv.setText(label);
        tv.setTextSize(14f);
        tv.setTypeface(null, android.graphics.Typeface.BOLD);
        tv.setTextColor(getColor(R.color.text_primary));
        row.addView(tv, new LinearLayout.LayoutParams(0, dp(52), 0.38f));

        Spinner spinner = new Spinner(this);
        ArrayAdapter<String> adapter = new ArrayAdapter<>(
                this,
                android.R.layout.simple_spinner_item,
                options
        );
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinner.setAdapter(adapter);
        row.addView(spinner, new LinearLayout.LayoutParams(0, dp(52), 0.62f));
        content.addView(row);
        return spinner;
    }

    private TextView addResultCard() {
        TextView tv = new TextView(this);
        tv.setTextSize(14f);
        tv.setTextColor(getColor(R.color.text_primary));
        tv.setBackgroundResource(R.drawable.button_soft_purple_centered);
        tv.setPadding(dp(14), dp(14), dp(14), dp(14));
        tv.setTextIsSelectable(true);
        tv.setOnLongClickListener(v -> {
            copyResult(tv.getText().toString());
            return true;
        });
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        );
        lp.setMargins(0, dp(10), 0, dp(10));
        content.addView(tv, lp);

        TextView copy = makeButton("COPIAR RESULTADO", true);
        copy.setOnClickListener(v -> copyResult(tv.getText().toString()));
        content.addView(copy, fullButtonParams());
        return tv;
    }

    private void copyResult(String text) {
        ClipboardManager clipboard = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
        if (clipboard != null) {
            clipboard.setPrimaryClip(ClipData.newPlainText("YomCeph", text));
            Toast.makeText(this, "Resultado copiado", Toast.LENGTH_SHORT).show();
        }
    }

    private EditText numericField(String hint) {
        EditText field = new EditText(this);
        field.setHint(hint);
        field.setSingleLine(true);
        field.setGravity(Gravity.CENTER);
        field.setInputType(InputType.TYPE_CLASS_NUMBER);
        return field;
    }

    private TextView makeButton(String text, boolean secondary) {
        TextView tv = new TextView(this);
        tv.setText(text);
        tv.setTextSize(13f);
        tv.setTypeface(null, android.graphics.Typeface.BOLD);
        tv.setGravity(Gravity.CENTER);
        tv.setTextAlignment(View.TEXT_ALIGNMENT_CENTER);
        tv.setIncludeFontPadding(false);
        tv.setClickable(true);
        tv.setFocusable(true);
        if (secondary) {
            tv.setBackgroundResource(R.drawable.button_secondary_centered);
            tv.setTextColor(getColor(R.color.mint_text));
        } else {
            tv.setBackgroundResource(R.drawable.button_primary_centered);
            tv.setTextColor(getColor(R.color.white));
        }
        return tv;
    }

    private LinearLayout.LayoutParams weightedButtonParams() {
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, dp(48), 1f);
        lp.setMargins(dp(3), 0, dp(3), 0);
        return lp;
    }

    private LinearLayout.LayoutParams fullButtonParams() {
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                dp(50)
        );
        lp.setMargins(0, dp(5), 0, dp(5));
        return lp;
    }

    private String modeTitle() {
        if (MODE_NOLLA.equals(mode)) return "Desarrollo dental · Nolla";
        if (MODE_RESORPTION.equals(mode)) return "Reabsorción radicular temporal";
        if (MODE_PANO_REVIEW.equals(mode)) return "Evaluación panorámica integral";
        return "Maduración cervical C2–C4";
    }

    private String modeIntro() {
        if (MODE_NOLLA.equals(mode)) {
            return "Radiografía panorámica · Etapas 0–10 de desarrollo permanente y estimación de edad dental con tablas separadas por sexo y arcada. No equivale a edad cronológica exacta.";
        }
        if (MODE_RESORPTION.equals(mode)) {
            return "Radiografía panorámica · Registro de reabsorción de raíces temporales y relación con el sucesor permanente. Se evita convertir una simplificación docente en un diagnóstico automático.";
        }
        if (MODE_PANO_REVIEW.equals(mode)) {
            return "Radiografía panorámica · Revisión sistemática de calidad, dentición, erupción, hueso y estructuras vecinas. Cualquier hallazgo requiere correlación clínica.";
        }
        return "Radiografía lateral de cráneo · Método CVM modificado: utiliza únicamente C2, C3 y C4 y clasifica CS1–CS6 según concavidades inferiores y forma de C3/C4.";
    }

    private void openImage() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("image/*");
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
        startActivityForResult(intent, REQ_IMAGE);
    }

    @Override
    @SuppressWarnings("deprecation")
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != REQ_IMAGE || resultCode != RESULT_OK || data == null || data.getData() == null) return;
        Uri uri = data.getData();
        try {
            int flags = data.getFlags() & (Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
            getContentResolver().takePersistableUriPermission(uri, flags & Intent.FLAG_GRANT_READ_URI_PERMISSION);
        } catch (Exception ignored) {
            // Some providers do not expose persistable permissions. The current session still works.
        }
        imageUriString = uri.toString();
        restoreImage(uri);
    }

    private void restoreImage(Uri uri) {
        try {
            Bitmap bitmap = decodeSampledBitmap(uri, 4096);
            if (bitmap == null) throw new IOException("No se pudo decodificar la imagen");
            bitmap = applyExifRotation(uri, bitmap);
            imageView.setBitmap(bitmap);
            txtImageName.setText(queryDisplayName(uri));
        } catch (Exception e) {
            Toast.makeText(this, "No se pudo abrir la radiografía.", Toast.LENGTH_LONG).show();
        }
    }

    private Bitmap decodeSampledBitmap(Uri uri, int maxDimension) throws IOException {
        BitmapFactory.Options bounds = new BitmapFactory.Options();
        bounds.inJustDecodeBounds = true;
        try (InputStream in = getContentResolver().openInputStream(uri)) {
            BitmapFactory.decodeStream(in, null, bounds);
        }

        int sample = 1;
        int largest = Math.max(bounds.outWidth, bounds.outHeight);
        while (largest / sample > maxDimension) sample *= 2;

        BitmapFactory.Options opts = new BitmapFactory.Options();
        opts.inSampleSize = Math.max(1, sample);
        opts.inPreferredConfig = Bitmap.Config.ARGB_8888;
        try (InputStream in = getContentResolver().openInputStream(uri)) {
            return BitmapFactory.decodeStream(in, null, opts);
        }
    }

    private Bitmap applyExifRotation(Uri uri, Bitmap bitmap) {
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

    private String queryDisplayName(Uri uri) {
        try (android.database.Cursor cursor = getContentResolver().query(
                uri,
                new String[]{OpenableColumns.DISPLAY_NAME},
                null,
                null,
                null
        )) {
            if (cursor != null && cursor.moveToFirst()) {
                int index = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME);
                if (index >= 0) return cursor.getString(index);
            }
        } catch (Exception ignored) {}
        return "Radiografía seleccionada";
    }

    private int dp(float value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    /** Minimal listener adapter to keep the activity readable. */
    private static final class SimpleItemSelectedListener implements android.widget.AdapterView.OnItemSelectedListener {
        private final Runnable callback;
        SimpleItemSelectedListener(Runnable callback) {
            this.callback = callback;
        }
        @Override public void onItemSelected(android.widget.AdapterView<?> parent, View view, int position, long id) {
            callback.run();
        }
        @Override public void onNothingSelected(android.widget.AdapterView<?> parent) {}
    }
}
