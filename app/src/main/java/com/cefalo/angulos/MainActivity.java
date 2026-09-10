package com.cefalo.angulos;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.app.AppCompatDelegate;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.widget.TextView;

public class MainActivity extends AppCompatActivity {

    private static final String PREFS = "yomceph_prefs";
    private static final String KEY_DISCLAIMER_SHOWN = "educational_disclaimer_shown";
    private static final String KEY_DARK_MODE = "dark_mode_enabled";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        boolean darkMode = getSharedPreferences(PREFS, MODE_PRIVATE)
                .getBoolean(KEY_DARK_MODE, false);
        AppCompatDelegate.setDefaultNightMode(
                darkMode
                        ? AppCompatDelegate.MODE_NIGHT_YES
                        : AppCompatDelegate.MODE_NIGHT_NO
        );

        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        TextView btnSteiner = findViewById(R.id.btnSteiner);
        TextView btnVertebral = findViewById(R.id.btnVertebral);
        TextView btnPowell = findViewById(R.id.btnPowell);
        TextView btnTweed = findViewById(R.id.btnTweed);
        TextView btnLevandoski = findViewById(R.id.btnLevandoski);
        TextView btnAirway = findViewById(R.id.btnAirway);
        TextView btnCvm = findViewById(R.id.btnCvm);
        TextView btnNolla = findViewById(R.id.btnNolla);
        TextView btnResorption = findViewById(R.id.btnResorption);
        TextView btnPanoramicReview = findViewById(R.id.btnPanoramicReview);
        TextView btnStudies = findViewById(R.id.btnStudies);
        TextView btnInfo = findViewById(R.id.btnInfo);
        TextView btnTheme = findViewById(R.id.btnTheme);

        updateThemeButton(btnTheme);

        // Every launcher binding is null-safe. This prevents a layout/resource
        // variant from closing the app merely because one optional control is absent.
        setSafeClick(btnSteiner, v -> openAnalysis("STEINER"));
        setSafeClick(btnVertebral, v -> openAnalysis("VERTEBRAL"));
        setSafeClick(btnAirway, v -> openAnalysis("AIRWAY"));
        setSafeClick(btnTweed, v -> openAnalysis("TWEED"));
        setSafeClick(btnPowell, v -> openAnalysis("POWELL"));
        setSafeClick(btnCvm, v -> openAssessment(RadiographicAssessmentActivity.MODE_CVM));

        setSafeClick(btnLevandoski, v -> openAnalysis("LEVANDOSKI"));
        setSafeClick(btnNolla, v -> openAssessment(RadiographicAssessmentActivity.MODE_NOLLA));
        setSafeClick(btnResorption, v -> openAssessment(RadiographicAssessmentActivity.MODE_RESORPTION));
        setSafeClick(btnPanoramicReview, v -> openAssessment(RadiographicAssessmentActivity.MODE_PANO_REVIEW));

        setSafeClick(btnStudies, v -> startActivity(new Intent(this, SavedStudiesActivity.class)));
        setSafeClick(btnInfo, v -> startActivity(new Intent(this, InfoActivity.class)));
        setSafeClick(btnTheme, v -> toggleTheme());

        // Wait until the window is attached before opening the first-run dialog.
        // This avoids BadToken-style launcher crashes on devices that attach slowly.
        getWindow().getDecorView().post(this::showEducationalDisclaimerOnce);
    }

    private void setSafeClick(View view, View.OnClickListener listener) {
        if (view != null) view.setOnClickListener(listener);
    }

    private void showEducationalDisclaimerOnce() {
        if (isFinishing() || isDestroyed()) return;

        boolean shown = getSharedPreferences(PREFS, MODE_PRIVATE)
                .getBoolean(KEY_DISCLAIMER_SHOWN, false);
        if (shown) return;

        AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle(R.string.educational_disclaimer_title)
                .setMessage(R.string.educational_disclaimer)
                .setNegativeButton(
                        R.string.more_info,
                        (unused, which) -> startActivity(new Intent(this, InfoActivity.class))
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

        try {
            dialog.show();
        } catch (WindowManager.BadTokenException ignored) {
            // Do not terminate the launcher if the Activity window disappeared
            // between posting the dialog and showing it.
        }
    }

    private void updateThemeButton(TextView button) {
        if (button == null) return;
        boolean darkMode = getSharedPreferences(PREFS, MODE_PRIVATE)
                .getBoolean(KEY_DARK_MODE, false);
        button.setText(darkMode ? R.string.theme_light : R.string.theme_dark);
    }

    private void toggleTheme() {
        boolean darkMode = getSharedPreferences(PREFS, MODE_PRIVATE)
                .getBoolean(KEY_DARK_MODE, false);
        boolean nextDarkMode = !darkMode;

        getSharedPreferences(PREFS, MODE_PRIVATE)
                .edit()
                .putBoolean(KEY_DARK_MODE, nextDarkMode)
                .apply();

        AppCompatDelegate.setDefaultNightMode(
                nextDarkMode
                        ? AppCompatDelegate.MODE_NIGHT_YES
                        : AppCompatDelegate.MODE_NIGHT_NO
        );
    }

    private void openAnalysis(String mode) {
        Intent intent = new Intent(this, AnalysisActivity.class);
        intent.putExtra("MODE", mode);
        startActivity(intent);
    }

    private void openAssessment(String mode) {
        Intent intent = new Intent(this, RadiographicAssessmentActivity.class);
        intent.putExtra(RadiographicAssessmentActivity.EXTRA_MODE, mode);
        startActivity(intent);
    }
}
