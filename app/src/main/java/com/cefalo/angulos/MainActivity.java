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
        TextView btnStudies = findViewById(R.id.btnStudies);

        btnSteiner.setOnClickListener(v -> openAnalysis("STEINER"));
        btnVertebral.setOnClickListener(v -> openAnalysis("VERTEBRAL"));

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
