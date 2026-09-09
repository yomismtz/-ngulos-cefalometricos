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

        LinearLayout header = new LinearLayout(this);
        header.setOrientation(LinearLayout.HORIZONTAL);
        header.setGravity(Gravity.CENTER_VERTICAL);
        header.setPadding(dp(10), dp(10), dp(10), dp(10));
        header.setBackgroundResource(R.drawable.header_gradient);

        TextView back = button("←", 48, R.drawable.button_soft_purple, 0xFFFFFFFF);
        back.setTextSize(24f);
        back.setOnClickListener(v -> finish());
        header.addView(back);

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
        List<SavedStudyStore.StudyData> studies = SavedStudyStore.list(this);

        if (studies.isEmpty()) {
            TextView empty = new TextView(this);
            empty.setText("Todavía no hay análisis guardados.\nAbra una radiografía y el estudio se guardará automáticamente.");
            empty.setTextColor(0xFF645B73);
            empty.setTextSize(16f);
            empty.setGravity(Gravity.CENTER);
            empty.setPadding(dp(18), dp(50), dp(18), dp(18));
            listContainer.addView(empty);
            return;
        }

        DateFormat format = DateFormat.getDateTimeInstance(DateFormat.SHORT, DateFormat.SHORT);

        for (SavedStudyStore.StudyData study : studies) {
            LinearLayout card = new LinearLayout(this);
            card.setOrientation(LinearLayout.VERTICAL);
            card.setBackgroundResource(R.drawable.card_white);
            card.setPadding(dp(16), dp(14), dp(16), dp(14));
            card.setElevation(dp(2));

            TextView name = new TextView(this);
            name.setText("VERTEBRAL".equals(study.mode)
                    ? "Análisis vertebral / craneocervical"
                    : "Análisis de Steiner");
            name.setTextColor(0xFF5B3FA4);
            name.setTextSize(17f);
            name.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
            card.addView(name);

            TextView details = new TextView(this);
            details.setText(
                    format.format(new Date(study.updatedAt)) +
                    "   ·   " + study.placedCount() + "/" + study.labels.size() + " puntos" +
                    (study.locked ? "   ·   🔒" : "")
            );
            details.setTextColor(0xFF4A4652);
            details.setTextSize(14f);
            details.setPadding(0, dp(5), 0, dp(12));
            card.addView(details);

            LinearLayout row = new LinearLayout(this);
            row.setOrientation(LinearLayout.HORIZONTAL);

            TextView open = button("ABRIR", 50, R.drawable.card_steiner, 0xFFFFFFFF);
            open.setOnClickListener(v -> {
                Intent intent = new Intent(this, AnalysisActivity.class);
                intent.putExtra("STUDY_ID", study.id);
                startActivity(intent);
            });
            row.addView(open, new LinearLayout.LayoutParams(0, dp(50), 1f));

            TextView delete = button("ELIMINAR", 50, R.drawable.button_soft_mint, 0xFF15383D);
            LinearLayout.LayoutParams deleteLp = new LinearLayout.LayoutParams(0, dp(50), 1f);
            deleteLp.setMargins(dp(8), 0, 0, 0);
            row.addView(delete, deleteLp);

            delete.setOnClickListener(v -> new AlertDialog.Builder(this)
                    .setTitle("Eliminar análisis")
                    .setMessage("¿Desea eliminar este estudio guardado?")
                    .setNegativeButton("Cancelar", null)
                    .setPositiveButton("Eliminar", (dialog, which) -> {
                        SavedStudyStore.delete(this, study.id);
                        refresh();
                    })
                    .show());

            card.addView(row);

            LinearLayout.LayoutParams cardLp = new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT
            );
            cardLp.setMargins(0, 0, 0, dp(12));
            listContainer.addView(card, cardLp);
        }
    }

    private TextView button(String text, int heightDp, int bg, int color) {
        TextView view = new TextView(this);
        view.setText(text);
        view.setGravity(Gravity.CENTER);
        view.setTextColor(color);
        view.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        view.setTextSize(15f);
        view.setBackgroundResource(bg);
        view.setClickable(true);
        view.setFocusable(true);
        view.setPadding(dp(8), 0, dp(8), 0);
        return view;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
