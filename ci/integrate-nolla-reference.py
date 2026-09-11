from pathlib import Path
import base64
import re

# Embed the exact radiographic Nolla reference image supplied by the project
# owner. The repository connector stores it as small Base64 text parts; the
# Android build reconstructs the WebP resource locally before aapt packages it.
parts = [Path(f'ci/nolla-reference.part{i}.b64') for i in range(4)]
for part in parts:
    if not part.exists():
        raise RuntimeError(f'Missing Nolla reference part: {part}')
encoded = ''.join(part.read_text(encoding='utf-8').strip() for part in parts)
image_bytes = base64.b64decode(encoded, validate=True)
if len(image_bytes) < 10000 or not image_bytes.startswith(b'RIFF') or b'WEBP' not in image_bytes[:16]:
    raise RuntimeError('Reconstructed Nolla reference is not a valid expected WebP resource')

drawable_dir = Path('app/src/main/res/drawable-nodpi')
drawable_dir.mkdir(parents=True, exist_ok=True)
nolla_image = drawable_dir / 'nolla_reference.webp'
nolla_image.write_bytes(image_bytes)

java_dir = Path('app/src/main/java/com/cefalo/angulos')
reference_activity = java_dir / 'NollaReferenceActivity.java'
reference_activity.write_text(r'''package com.cefalo.angulos;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Bundle;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

/** Full-screen educational reference using the radiographic examples supplied by the owner. */
public class NollaReferenceActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundResource(R.drawable.bg_home);
        root.setPadding(dp(10), dp(8), dp(10), dp(10));

        LinearLayout header = new LinearLayout(this);
        header.setOrientation(LinearLayout.HORIZONTAL);
        header.setGravity(Gravity.CENTER_VERTICAL);

        TextView close = button("← CERRAR");
        close.setOnClickListener(v -> finish());
        LinearLayout.LayoutParams closeLp = new LinearLayout.LayoutParams(dp(84), dp(46));
        closeLp.setMargins(0, 0, dp(8), 0);
        header.addView(close, closeLp);

        TextView title = new TextView(this);
        title.setText("Estados de Nolla · referencia radiográfica");
        title.setTextSize(18f);
        title.setTextColor(getColor(R.color.text_primary));
        title.setTypeface(null, android.graphics.Typeface.BOLD);
        title.setGravity(Gravity.CENTER_VERTICAL);
        title.setTextAlignment(TextView.TEXT_ALIGNMENT_CENTER);
        header.addView(title, new LinearLayout.LayoutParams(0, dp(50), 1f));
        root.addView(header);

        TextView hint = new TextView(this);
        hint.setText("Compare la panorámica del paciente con los ejemplos 0–10. Pellizque para ampliar y arrastre la referencia; después regrese al análisis e introduzca la etapa observada para cada diente.");
        hint.setTextSize(12.5f);
        hint.setTextColor(getColor(R.color.text_secondary));
        hint.setGravity(Gravity.CENTER);
        hint.setTextAlignment(TextView.TEXT_ALIGNMENT_CENTER);
        hint.setPadding(dp(8), dp(5), dp(8), dp(8));
        root.addView(hint);

        RadiographImageView reference = new RadiographImageView(this);
        reference.setBackgroundColor(getColor(R.color.analysis_panel));
        reference.setContentDescription("Ejemplos radiográficos de los estados de Nolla del 0 al 10");
        Bitmap bitmap = BitmapFactory.decodeResource(getResources(), R.drawable.nolla_reference);
        if (bitmap != null) {
            reference.setBitmap(bitmap);
        }
        root.addView(reference, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                0,
                1f
        ));

        TextView note = new TextView(this);
        note.setText("Referencia visual de apoyo para el estudiante. La etapa se registra según la morfología observada en cada diente; la app no asigna el estadio automáticamente a partir de esta lámina.");
        note.setTextSize(11.5f);
        note.setTextColor(getColor(R.color.text_secondary));
        note.setGravity(Gravity.CENTER);
        note.setTextAlignment(TextView.TEXT_ALIGNMENT_CENTER);
        note.setPadding(dp(8), dp(8), dp(8), dp(2));
        root.addView(note);

        setContentView(root);
        reference.post(reference::fitImage);
    }

    private TextView button(String text) {
        TextView v = new TextView(this);
        v.setText(text);
        v.setTextSize(10f);
        v.setTextColor(getColor(R.color.brand_purple));
        v.setTypeface(null, android.graphics.Typeface.BOLD);
        v.setGravity(Gravity.CENTER);
        v.setTextAlignment(TextView.TEXT_ALIGNMENT_CENTER);
        v.setBackgroundResource(R.drawable.button_soft_purple_centered);
        v.setClickable(true);
        v.setFocusable(true);
        return v;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
''', encoding='utf-8')

# Replace the former text-only Nolla guide with the supplied radiographic plate.
assessment = java_dir / 'RadiographicAssessmentActivity.java'
a = assessment.read_text(encoding='utf-8')
a = a.replace(
    'TextView stageGuide = makeButton("VER GUÍA DE ETAPAS 0–10", true);',
    'TextView stageGuide = makeButton("VER IMAGEN DE REFERENCIA · ETAPAS 0–10", true);',
    1
)
pattern = re.compile(
    r'    private void showNollaGuide\(\) \{[\s\S]*?\n    \}\n\n    private void renderResorption\(\)'
)
replacement = '''    private void showNollaGuide() {\n        startActivity(new Intent(this, NollaReferenceActivity.class));\n    }\n\n    private void renderResorption()'''
a, count = pattern.subn(replacement, a, count=1)
if count != 1:
    raise RuntimeError('Could not replace the text-only Nolla guide')
assessment.write_text(a, encoding='utf-8')

# Register the internal reference viewer.
manifest = Path('app/src/main/AndroidManifest.xml')
m = manifest.read_text(encoding='utf-8')
if '.NollaReferenceActivity' not in m:
    anchor = '        <activity android:name=".RadiographicAssessmentActivity" android:exported="false" />'
    if anchor not in m:
        raise RuntimeError('RadiographicAssessmentActivity manifest entry not found')
    m = m.replace(
        anchor,
        anchor + '\n        <activity android:name=".NollaReferenceActivity" android:exported="false" />',
        1
    )
manifest.write_text(m, encoding='utf-8')

# Build identity for the embedded-reference revision.
gradle = Path('app/build.gradle')
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+30\b', 'versionCode 31', g, count=1)
g = re.sub(r"versionName\s+'1\.29'", "versionName '1.30'", g, count=1)
gradle.write_text(g, encoding='utf-8')

# CI guardrails.
checks = {
    'embedded image': nolla_image.exists() and nolla_image.stat().st_size > 10000,
    'reference activity': reference_activity.exists(),
    'reference button': 'VER IMAGEN DE REFERENCIA · ETAPAS 0–10' in assessment.read_text(encoding='utf-8'),
    'manifest activity': '.NollaReferenceActivity' in manifest.read_text(encoding='utf-8'),
    'version 1.30': "versionName '1.30'" in gradle.read_text(encoding='utf-8'),
}
missing = [name for name, ok in checks.items() if not ok]
if missing:
    raise RuntimeError('Nolla reference integration incomplete: ' + ', '.join(missing))

print(f'Embedded owner-supplied Nolla radiographic reference ({len(image_bytes)} bytes) and connected it to the Nolla analysis.')
