package com.cefalo.angulos;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.widget.TextView;

public class MainActivity extends Activity {

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

        btnSteiner.setOnClickListener(v -> openAnalysis("STEINER"));
        btnVertebral.setOnClickListener(v -> openAnalysis("VERTEBRAL"));
        btnPowell.setOnClickListener(v -> openAnalysis("POWELL"));
        btnTweed.setOnClickListener(v -> openAnalysis("TWEED"));
        btnLevandoski.setOnClickListener(v -> openAnalysis("LEVANDOSKI"));
        btnAirway.setOnClickListener(v -> openAnalysis("AIRWAY"));

        btnStudies.setOnClickListener(v ->
                startActivity(new Intent(this, SavedStudiesActivity.class))
        );
    }

    private void openAnalysis(String mode) {
        Intent intent = new Intent(this, AnalysisActivity.class);
        intent.putExtra("MODE", mode);
        startActivity(intent);
    }
}
