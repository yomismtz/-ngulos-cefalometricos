package com.cefalo.angulos;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.os.Bundle;
import android.widget.TextView;

public class MainActivity extends Activity {

    private static final String PREFS = "yomceph_prefs";
    private static final String KEY_DISCLAIMER_SHOWN = "educational_disclaimer_shown";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        TextView btnSteiner = findViewById(R.id.btnSteiner);
        TextView btnVertebral = findViewById(R.id.btnVertebral);
        TextView btnPowell = findViewById(R.id.btnPowell);
        TextView btnTweed = findViewById(R.id.btnTweed);
        TextView btnLevandoski = findViewById(R.id.btnLevandoski);
        TextView btnAirway = findViewById(R.id.btnAirway);
        TextView btnStudies = findViewById(R.id.btnStudies);
        TextView btnInfo = findViewById(R.id.btnInfo);

        btnSteiner.setOnClickListener(v -> openAnalysis("STEINER"));
        btnVertebral.setOnClickListener(v -> openAnalysis("VERTEBRAL"));
        btnPowell.setOnClickListener(v -> openAnalysis("POWELL"));
        btnTweed.setOnClickListener(v -> openAnalysis("TWEED"));
        btnLevandoski.setOnClickListener(v -> openAnalysis("LEVANDOSKI"));
        btnAirway.setOnClickListener(v -> openAnalysis("AIRWAY"));

        btnStudies.setOnClickListener(v ->
                startActivity(new Intent(this, SavedStudiesActivity.class))
        );

        btnInfo.setOnClickListener(v ->
                startActivity(new Intent(this, InfoActivity.class))
        );

        showEducationalDisclaimerOnce();
    }

    private void showEducationalDisclaimerOnce() {
        boolean shown =
                getSharedPreferences(PREFS, MODE_PRIVATE)
                        .getBoolean(KEY_DISCLAIMER_SHOWN, false);

        if (shown) return;

        AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle(R.string.educational_disclaimer_title)
                .setMessage(R.string.educational_disclaimer)
                .setNegativeButton(
                        R.string.more_info,
                        (unused, which) ->
                                startActivity(new Intent(this, InfoActivity.class))
                )
                .setPositiveButton(R.string.understood, null)
                .create();

        dialog.setOnDismissListener(unused ->
                getSharedPreferences(PREFS, MODE_PRIVATE)
                        .edit()
                        .putBoolean(KEY_DISCLAIMER_SHOWN, true)
                        .apply()
        );

        dialog.setCanceledOnTouchOutside(false);
        dialog.show();
    }

    private void openAnalysis(String mode) {
        Intent intent = new Intent(this, AnalysisActivity.class);
        intent.putExtra("MODE", mode);
        startActivity(intent);
    }
}
