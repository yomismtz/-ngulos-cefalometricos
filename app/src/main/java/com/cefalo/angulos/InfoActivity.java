package com.cefalo.angulos;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Typeface;
import android.net.Uri;
import android.os.Bundle;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

public class InfoActivity extends Activity {

    private static final String PRIVACY_URL =
            "https://github.com/yomismtz/-ngulos-cefalometricos/blob/main/PRIVACY_POLICY.md";

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
        title.setText("Información y privacidad");
        title.setTextColor(0xFFFFFFFF);
        title.setTextSize(18f);
        title.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        title.setGravity(Gravity.CENTER);
        title.setTextAlignment(TextView.TEXT_ALIGNMENT_CENTER);
        header.addView(title, new LinearLayout.LayoutParams(0, dp(48), 1f));

        root.addView(header);

        ScrollView scroll = new ScrollView(this);
        LinearLayout content = new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        content.setPadding(dp(18), dp(18), dp(18), dp(28));

        TextView brand = new TextView(this);
        brand.setText("YomCeph\nTraza. Mide. Aprende.");
        brand.setTextColor(0xFF5B3FA4);
        brand.setTextSize(22f);
        brand.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        brand.setGravity(Gravity.CENTER);
        brand.setTextAlignment(TextView.TEXT_ALIGNMENT_CENTER);
        brand.setPadding(0, 0, 0, dp(18));
        content.addView(brand);

        content.addView(section(
                "Uso educativo",
                "YomCeph es una herramienta educativa para apoyar el aprendizaje y la práctica de trazados cefalométricos. " +
                "No es un dispositivo médico y no diagnostica, trata, cura ni previene ninguna afección médica. " +
                "Los resultados son referencias cefalométricas orientativas y deben revisarse con criterio profesional."
        ));

        content.addView(section(
                "Consulte a un profesional",
                "Para asesoramiento, diagnóstico o tratamiento médico u odontológico, consulte a un profesional sanitario cualificado. " +
                "Una medición aislada no debe utilizarse como diagnóstico independiente."
        ));

        content.addView(section(
                "Privacidad",
                "La app puede guardar en el dispositivo radiografías seleccionadas por el usuario, nombre del estudio, nombre del paciente, edad, sexo, puntos y calibración. " +
                "YomCeph no crea cuentas, no contiene anuncios ni analítica y no envía estos datos a servidores del desarrollador. " +
                "Los estudios permanecen localmente en el dispositivo salvo que el usuario exporte o comparta archivos por su cuenta."
        ));

        content.addView(section(
                "Uso responsable de radiografías",
                "Para actividades docentes, use radiografías anonimizadas o datos autorizados. Evite introducir información identificable de pacientes si no cuenta con autorización para utilizarla."
        ));

        TextView privacy = button(
                "VER POLÍTICA DE PRIVACIDAD",
                R.drawable.button_primary_centered,
                0xFFFFFFFF
        );
        privacy.setTextSize(13f);
        privacy.setOnClickListener(v -> {
            Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(PRIVACY_URL));
            startActivity(intent);
        });

        LinearLayout.LayoutParams privacyLp =
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        dp(54)
                );
        privacyLp.setMargins(0, dp(6), 0, 0);
        content.addView(privacy, privacyLp);

        scroll.addView(content);
        root.addView(scroll, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                0,
                1f
        ));

        setContentView(root);
    }

    private TextView section(String heading, String body) {
        TextView view = new TextView(this);
        view.setText(heading + "\n" + body);
        view.setTextColor(0xFF3D3946);
        view.setTextSize(14f);
        view.setLineSpacing(0f, 1.08f);
        view.setBackgroundResource(R.drawable.card_white);
        view.setPadding(dp(14), dp(12), dp(14), dp(12));

        LinearLayout.LayoutParams lp =
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                );
        lp.setMargins(0, 0, 0, dp(10));
        view.setLayoutParams(lp);
        return view;
    }

    private TextView button(String text, int bg, int color) {
        TextView view = new TextView(this);
        view.setText(text);
        view.setGravity(Gravity.CENTER);
        view.setTextAlignment(TextView.TEXT_ALIGNMENT_CENTER);
        view.setIncludeFontPadding(false);
        view.setTextColor(color);
        view.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        view.setBackgroundResource(bg);
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
