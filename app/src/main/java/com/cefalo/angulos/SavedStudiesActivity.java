package com.cefalo.angulos;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.graphics.Typeface;
import android.os.Bundle;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import java.text.DateFormat;
import java.util.Date;
import java.util.List;

public class SavedStudiesActivity extends Activity {

    private LinearLayout listContainer;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundResource(R.drawable.bg_home);
        root.setFitsSystemWindows(true);

        LinearLayout header = new LinearLayout(this);
        header.setOrientation(LinearLayout.HORIZONTAL);
        header.setGravity(Gravity.CENTER_VERTICAL);
        header.setPadding(dp(10), dp(10), dp(10), dp(10));
        header.setBackgroundResource(R.drawable.header_gradient);

        TextView back = button("←", R.drawable.button_soft_purple_centered, 0xFF5B3FA4);
        back.setTextSize(24f);
        back.setOnClickListener(v -> finish());
        header.addView(back, new LinearLayout.LayoutParams(dp(48), dp(48)));

        TextView title = new TextView(this);
        title.setText("Mis análisis");
        title.setTextColor(0xFFFFFFFF);
        title.setTextSize(22f);
        title.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        title.setGravity(Gravity.CENTER);
        header.addView(title, new LinearLayout.LayoutParams(0, dp(48), 1f));

        root.addView(header);

        ScrollView scroll = new ScrollView(this);
        listContainer = new LinearLayout(this);
        listContainer.setOrientation(LinearLayout.VERTICAL);
        listContainer.setPadding(dp(14), dp(14), dp(14), dp(24));
        scroll.addView(listContainer);

        root.addView(scroll, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                0,
                1f
        ));

        setContentView(root);
    }

    @Override
    protected void onResume() {
        super.onResume();
        refresh();
    }

    private void refresh() {
        listContainer.removeAllViews();

        List<SavedStudyStore.StudyData> studies =
                SavedStudyStore.list(this);

        if (studies.isEmpty()) {
            TextView empty = new TextView(this);
            empty.setText(
                    "Todavía no hay análisis guardados.\n" +
                    "Abra una radiografía y el estudio se guardará automáticamente."
            );
            empty.setTextColor(0xFF645B73);
            empty.setTextSize(16f);
            empty.setGravity(Gravity.CENTER);
            empty.setPadding(dp(18), dp(50), dp(18), dp(18));
            listContainer.addView(empty);
            return;
        }

        DateFormat format =
                DateFormat.getDateTimeInstance(
                        DateFormat.SHORT,
                        DateFormat.SHORT
                );

        for (SavedStudyStore.StudyData study : studies) {
            LinearLayout card = new LinearLayout(this);
            card.setOrientation(LinearLayout.VERTICAL);
            card.setBackgroundResource(R.drawable.card_white);
            card.setPadding(dp(16), dp(14), dp(16), dp(14));
            card.setElevation(dp(2));

            TextView name = new TextView(this);
            name.setText(
                    study.studyName == null || study.studyName.trim().isEmpty()
                            ? "Estudio"
                            : study.studyName
            );
            name.setTextColor(0xFF5B3FA4);
            name.setTextSize(18f);
            name.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
            card.addView(name);

            TextView patient = new TextView(this);
            String patientText =
                    study.patientName == null || study.patientName.trim().isEmpty()
                            ? "Paciente sin nombre"
                            : study.patientName;

            if (study.patientAge != null && !study.patientAge.trim().isEmpty()) {
                patientText += " · " + study.patientAge + " años";
            }

            if (study.patientSex != null && !study.patientSex.trim().isEmpty()) {
                patientText += " · " + study.patientSex;
            }

            patient.setText(patientText);
            patient.setTextColor(0xFF2C7E86);
            patient.setTextSize(14f);
            patient.setPadding(0, dp(3), 0, 0);
            card.addView(patient);

            TextView type = new TextView(this);
            String typeText;
            if ("VERTEBRAL".equals(study.mode)) {
                typeText = "Análisis vertebral / Rocabado";
            } else if ("POWELL".equals(study.mode)) {
                typeText = "Análisis de Powell";
            } else if ("TWEED".equals(study.mode)) {
                typeText = "Análisis de Tweed";
            } else if ("LEVANDOSKI".equals(study.mode)) {
                typeText = "Análisis panorámico de Levandoski";
            } else if ("AIRWAY".equals(study.mode)) {
                typeText = "Análisis de vía aérea";
            } else {
                typeText = "Análisis de Steiner";
            }
            type.setText(typeText);
            type.setTextColor(0xFF4A4652);
            type.setTextSize(14f);
            type.setPadding(0, dp(3), 0, 0);
            card.addView(type);

            TextView details = new TextView(this);
            details.setText(
                    format.format(new Date(study.updatedAt)) +
                    "   ·   " +
                    study.placedCount() +
                    "/" +
                    study.labels.size() +
                    " puntos" +
                    (study.locked ? "   ·   🔒" : "")
            );
            details.setTextColor(0xFF6A6471);
            details.setTextSize(13f);
            details.setPadding(0, dp(5), 0, dp(12));
            card.addView(details);

            LinearLayout row = new LinearLayout(this);
            row.setOrientation(LinearLayout.HORIZONTAL);

            TextView open = button(
                    "ABRIR",
                    R.drawable.button_primary_centered,
                    0xFFFFFFFF
            );

            open.setOnClickListener(v -> {
                Intent intent = new Intent(
                        this,
                        AnalysisActivity.class
                );
                intent.putExtra("STUDY_ID", study.id);
                startActivity(intent);
            });

            row.addView(
                    open,
                    new LinearLayout.LayoutParams(
                            0,
                            dp(50),
                            1f
                    )
            );

            TextView delete = button(
                    "ELIMINAR",
                    R.drawable.button_soft_mint_centered,
                    0xFF15383D
            );

            LinearLayout.LayoutParams deleteLp =
                    new LinearLayout.LayoutParams(
                            0,
                            dp(50),
                            1f
                    );
            deleteLp.setMargins(dp(8), 0, 0, 0);
            row.addView(delete, deleteLp);

            delete.setOnClickListener(v ->
                    new AlertDialog.Builder(this)
                            .setTitle("Eliminar análisis")
                            .setMessage(
                                    "¿Desea eliminar \"" +
                                    name.getText() +
                                    "\"?"
                            )
                            .setNegativeButton("Cancelar", null)
                            .setPositiveButton(
                                    "Eliminar",
                                    (dialog, which) -> {
                                        SavedStudyStore.delete(
                                                this,
                                                study.id
                                        );
                                        refresh();
                                    }
                            )
                            .show()
            );

            card.addView(row);

            int availableWidth =
                    getResources().getDisplayMetrics().widthPixels - dp(28);
            int cardWidth =
                    Math.min(availableWidth, dp(560));

            LinearLayout.LayoutParams cardLp =
                    new LinearLayout.LayoutParams(
                            cardWidth,
                            ViewGroup.LayoutParams.WRAP_CONTENT
                    );
            cardLp.gravity = Gravity.CENTER_HORIZONTAL;
            cardLp.setMargins(0, 0, 0, dp(12));

            listContainer.addView(card, cardLp);
        }
    }

    private TextView button(
            String text,
            int bg,
            int color
    ) {
        TextView view = new TextView(this);
        view.setText(text);
        view.setGravity(Gravity.CENTER);
        view.setTextColor(color);
        view.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        view.setTextSize(15f);
        view.setBackgroundResource(bg);
        view.setIncludeFontPadding(false);
        view.setTextAlignment(TextView.TEXT_ALIGNMENT_CENTER);
        view.setClickable(true);
        view.setFocusable(true);
        view.setPadding(0, 0, 0, 0);
        return view;
    }

    private int dp(int value) {
        return Math.round(
                value * getResources()
                        .getDisplayMetrics()
                        .density
        );
    }
}
