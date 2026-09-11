from pathlib import Path
import re

# -----------------------------------------------------------------------------
# 1) Local SQLite database: keep the existing SavedStudyStore public API but
#    persist the JSON payload in an indexed on-device database as well. Existing
#    SharedPreferences data remains readable and is migrated lazily.
# -----------------------------------------------------------------------------
java_dir = Path('app/src/main/java/com/cefalo/angulos')
java_dir.mkdir(parents=True, exist_ok=True)

db_java = java_dir / 'StudyDatabase.java'
db_java.write_text(r'''package com.cefalo.angulos;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

import java.util.ArrayList;
import java.util.List;

/**
 * Lightweight offline database bundled with the app code and created locally
 * on first use. No network service or external database is required.
 */
public final class StudyDatabase extends SQLiteOpenHelper {
    private static final String DB_NAME = "yom_radiographic_studies.db";
    private static final int DB_VERSION = 1;
    private static final String TABLE = "studies";

    private static StudyDatabase instance;

    private StudyDatabase(Context context) {
        super(context.getApplicationContext(), DB_NAME, null, DB_VERSION);
    }

    private static synchronized StudyDatabase get(Context context) {
        if (instance == null) instance = new StudyDatabase(context);
        return instance;
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL(
                "CREATE TABLE " + TABLE + " (" +
                "id TEXT PRIMARY KEY NOT NULL," +
                "payload TEXT NOT NULL," +
                "updated_at INTEGER NOT NULL DEFAULT 0" +
                ")"
        );
        db.execSQL(
                "CREATE INDEX idx_studies_updated ON " + TABLE + "(updated_at DESC)"
        );
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        // Version 1. Future migrations must preserve studies rather than drop them.
    }

    public static void save(Context context, String id, String payload, long updatedAt) {
        if (id == null || payload == null) return;
        ContentValues values = new ContentValues();
        values.put("id", id);
        values.put("payload", payload);
        values.put("updated_at", updatedAt);
        get(context).getWritableDatabase().insertWithOnConflict(
                TABLE, null, values, SQLiteDatabase.CONFLICT_REPLACE
        );
    }

    public static String load(Context context, String id) {
        if (id == null) return null;
        try (Cursor c = get(context).getReadableDatabase().query(
                TABLE,
                new String[]{"payload"},
                "id=?",
                new String[]{id},
                null, null, null,
                "1"
        )) {
            return c.moveToFirst() ? c.getString(0) : null;
        }
    }

    public static List<String> ids(Context context) {
        List<String> ids = new ArrayList<>();
        try (Cursor c = get(context).getReadableDatabase().query(
                TABLE,
                new String[]{"id"},
                null, null, null, null,
                "updated_at DESC"
        )) {
            while (c.moveToNext()) ids.add(c.getString(0));
        }
        return ids;
    }

    public static void delete(Context context, String id) {
        if (id == null) return;
        get(context).getWritableDatabase().delete(TABLE, "id=?", new String[]{id});
    }
}
''', encoding='utf-8')

store = java_dir / 'SavedStudyStore.java'
s = store.read_text(encoding='utf-8')

save_anchor = '''            SharedPreferences prefs =\n                    context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);\n'''
if 'StudyDatabase.save(context, study.id' not in s:
    if save_anchor not in s:
        raise RuntimeError('Could not locate SavedStudyStore save anchor')
    s = s.replace(
        save_anchor,
        '''            // Primary indexed local persistence. SharedPreferences below is kept\n            // as a compatibility mirror for older installs during migration.\n            StudyDatabase.save(context, study.id, root.toString(), study.updatedAt);\n\n''' + save_anchor,
        1
    )

old_load = '''        String raw = prefs.getString("study_" + id, null);\n        if (raw == null) return null;\n\n        try {\n            JSONObject root = new JSONObject(raw);\n'''
new_load = '''        String raw = StudyDatabase.load(context, id);\n        boolean migrateFromLegacy = false;\n        if (raw == null) {\n            raw = prefs.getString("study_" + id, null);\n            migrateFromLegacy = raw != null;\n        }\n        if (raw == null) return null;\n\n        try {\n            JSONObject root = new JSONObject(raw);\n            if (migrateFromLegacy) {\n                StudyDatabase.save(context, id, raw, root.optLong("updatedAt", 0L));\n            }\n'''
if old_load in s:
    s = s.replace(old_load, new_load, 1)

old_ids = '''        Set<String> ids =\n                prefs.getStringSet(IDS, Collections.emptySet());\n\n        List<StudyData> result = new ArrayList<>();\n'''
new_ids = '''        Set<String> ids = new HashSet<>(StudyDatabase.ids(context));\n        // On first run after this update, include legacy IDs; load() migrates them.\n        ids.addAll(prefs.getStringSet(IDS, Collections.emptySet()));\n\n        List<StudyData> result = new ArrayList<>();\n'''
if old_ids in s:
    s = s.replace(old_ids, new_ids, 1)

if 'StudyDatabase.delete(context, id);' not in s:
    delete_anchor = '''        ids.remove(id);\n\n        prefs.edit()\n'''
    if delete_anchor not in s:
        raise RuntimeError('Could not locate SavedStudyStore delete anchor')
    s = s.replace(delete_anchor,
                  '''        ids.remove(id);\n        StudyDatabase.delete(context, id);\n\n        prefs.edit()\n''', 1)

store.write_text(s, encoding='utf-8')

# -----------------------------------------------------------------------------
# 2) Built-in PDF viewer. Uses Android PdfRenderer and keeps one rendered page
#    in memory at a time so it is safe on modest devices.
# -----------------------------------------------------------------------------
pdf_java = java_dir / 'PdfViewerActivity.java'
pdf_java.write_text(r'''package com.cefalo.angulos;

import android.app.ActivityManager;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.graphics.pdf.PdfRenderer;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.ParcelFileDescriptor;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import java.io.IOException;

public class PdfViewerActivity extends AppCompatActivity {
    private ParcelFileDescriptor descriptor;
    private PdfRenderer renderer;
    private PdfRenderer.Page page;
    private Bitmap pageBitmap;
    private ImageView image;
    private TextView counter;
    private View previous;
    private View next;
    private Uri pdfUri;
    private int pageIndex = 0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_pdf_viewer);

        image = findViewById(R.id.pdfImage);
        counter = findViewById(R.id.pdfPageCounter);
        previous = findViewById(R.id.pdfPrevious);
        next = findViewById(R.id.pdfNext);

        findViewById(R.id.pdfClose).setOnClickListener(v -> finish());
        previous.setOnClickListener(v -> renderPage(pageIndex - 1));
        next.setOnClickListener(v -> renderPage(pageIndex + 1));
        findViewById(R.id.pdfExternal).setOnClickListener(v -> openExternally());

        pdfUri = getIntent().getData();
        if (pdfUri == null) {
            Toast.makeText(this, "No se encontró el informe PDF.", Toast.LENGTH_LONG).show();
            finish();
            return;
        }

        try {
            descriptor = getContentResolver().openFileDescriptor(pdfUri, "r");
            if (descriptor == null) throw new IOException("Descriptor nulo");
            renderer = new PdfRenderer(descriptor);
            if (renderer.getPageCount() == 0) throw new IOException("PDF sin páginas");
            renderPage(0);
        } catch (Exception e) {
            Toast.makeText(this, "No se pudo mostrar el PDF dentro de la app.", Toast.LENGTH_LONG).show();
            finish();
        }
    }

    private int maxRenderWidth() {
        ActivityManager am = (ActivityManager) getSystemService(ACTIVITY_SERVICE);
        boolean lowRam = Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT && am != null && am.isLowRamDevice();
        int memoryClass = am == null ? 256 : am.getMemoryClass();
        if (lowRam || memoryClass <= 128) return 900;
        if (memoryClass <= 256) return 1200;
        int screen = getResources().getDisplayMetrics().widthPixels;
        return Math.min(1800, Math.max(1200, screen * 2));
    }

    private void renderPage(int requested) {
        if (renderer == null) return;
        int target = Math.max(0, Math.min(renderer.getPageCount() - 1, requested));

        closePageOnly();
        pageIndex = target;
        page = renderer.openPage(pageIndex);

        int width = Math.min(maxRenderWidth(), Math.max(1, page.getWidth() * 2));
        int height = Math.max(1, Math.round(width * (page.getHeight() / (float) page.getWidth())));
        pageBitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888);
        pageBitmap.eraseColor(Color.WHITE);
        page.render(pageBitmap, null, null, PdfRenderer.Page.RENDER_MODE_FOR_DISPLAY);
        image.setImageBitmap(pageBitmap);

        counter.setText("Página " + (pageIndex + 1) + " de " + renderer.getPageCount());
        previous.setEnabled(pageIndex > 0);
        previous.setAlpha(pageIndex > 0 ? 1f : 0.35f);
        next.setEnabled(pageIndex < renderer.getPageCount() - 1);
        next.setAlpha(pageIndex < renderer.getPageCount() - 1 ? 1f : 0.35f);
    }

    private void openExternally() {
        if (pdfUri == null) return;
        try {
            Intent intent = new Intent(Intent.ACTION_VIEW);
            intent.setDataAndType(pdfUri, "application/pdf");
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            startActivity(intent);
        } catch (Exception e) {
            Toast.makeText(this, "No hay otro visor PDF disponible.", Toast.LENGTH_SHORT).show();
        }
    }

    private void closePageOnly() {
        if (page != null) {
            page.close();
            page = null;
        }
        if (pageBitmap != null && !pageBitmap.isRecycled()) {
            pageBitmap.recycle();
            pageBitmap = null;
        }
    }

    @Override
    protected void onDestroy() {
        closePageOnly();
        if (renderer != null) {
            renderer.close();
            renderer = null;
        }
        if (descriptor != null) {
            try { descriptor.close(); } catch (IOException ignored) { }
            descriptor = null;
        }
        super.onDestroy();
    }
}
''', encoding='utf-8')

layout = Path('app/src/main/res/layout/activity_pdf_viewer.xml')
layout.write_text(r'''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:fitsSystemWindows="true"
    android:background="#16151D">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="54dp"
        android:orientation="horizontal"
        android:gravity="center_vertical"
        android:paddingLeft="8dp"
        android:paddingRight="8dp"
        android:background="@drawable/header_gradient">

        <TextView
            android:id="@+id/pdfClose"
            android:layout_width="64dp"
            android:layout_height="44dp"
            android:gravity="center"
            android:text="CERRAR"
            android:textStyle="bold"
            android:textSize="10sp"
            android:textColor="@color/brand_purple"
            android:background="@drawable/button_soft_purple_centered" />

        <TextView
            android:id="@+id/pdfPageCounter"
            android:layout_width="0dp"
            android:layout_height="match_parent"
            android:layout_weight="1"
            android:gravity="center"
            android:text="PDF"
            android:textStyle="bold"
            android:textSize="13sp"
            android:textColor="@color/white" />

        <TextView
            android:id="@+id/pdfExternal"
            android:layout_width="82dp"
            android:layout_height="44dp"
            android:gravity="center"
            android:text="OTRO VISOR"
            android:textStyle="bold"
            android:textSize="9sp"
            android:textColor="@color/mint_text"
            android:background="@drawable/button_soft_mint_centered" />
    </LinearLayout>

    <ScrollView
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:fillViewport="true"
        android:padding="8dp">

        <ImageView
            android:id="@+id/pdfImage"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:adjustViewBounds="true"
            android:scaleType="fitCenter"
            android:background="#FFFFFF"
            android:contentDescription="Vista previa del informe PDF" />
    </ScrollView>

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="56dp"
        android:orientation="horizontal"
        android:gravity="center"
        android:paddingLeft="10dp"
        android:paddingRight="10dp">

        <TextView
            android:id="@+id/pdfPrevious"
            android:layout_width="0dp"
            android:layout_height="46dp"
            android:layout_weight="1"
            android:layout_marginRight="5dp"
            android:gravity="center"
            android:text="◀ ANTERIOR"
            android:textStyle="bold"
            android:textSize="11sp"
            android:textColor="@color/brand_purple"
            android:background="@drawable/button_soft_purple_centered" />

        <TextView
            android:id="@+id/pdfNext"
            android:layout_width="0dp"
            android:layout_height="46dp"
            android:layout_weight="1"
            android:layout_marginLeft="5dp"
            android:gravity="center"
            android:text="SIGUIENTE ▶"
            android:textStyle="bold"
            android:textSize="11sp"
            android:textColor="@color/mint_text"
            android:background="@drawable/button_soft_mint_centered" />
    </LinearLayout>
</LinearLayout>
''', encoding='utf-8')

# Tablet PDF viewer: same controls, more breathing room; ImageView remains fit.
pdf_tablet = Path('app/src/main/res/layout-sw600dp/activity_pdf_viewer.xml')
pdf_tablet.parent.mkdir(parents=True, exist_ok=True)
pdf_tablet.write_text(layout.read_text(encoding='utf-8').replace('android:padding="8dp"', 'android:padding="24dp"'), encoding='utf-8')

manifest = Path('app/src/main/AndroidManifest.xml')
m = manifest.read_text(encoding='utf-8')
if '.PdfViewerActivity' not in m:
    m = m.replace(
        '        <activity android:name=".AnalysisActivity" android:exported="false" />',
        '        <activity android:name=".AnalysisActivity" android:exported="false" />\n        <activity android:name=".PdfViewerActivity" android:exported="false" />',
        1
    )
manifest.write_text(m, encoding='utf-8')

# -----------------------------------------------------------------------------
# 3) AnalysisActivity: adaptive image decoding for low-RAM phones and automatic
#    in-app PDF preview immediately after the report is written.
# -----------------------------------------------------------------------------
activity = java_dir / 'AnalysisActivity.java'
a = activity.read_text(encoding='utf-8')
if 'import android.app.ActivityManager;' not in a:
    a = a.replace('import androidx.appcompat.app.AlertDialog;\n',
                  'import androidx.appcompat.app.AlertDialog;\nimport android.app.ActivityManager;\n', 1)

# Replace both 4096 decode calls, including split-line forms.
a = re.sub(r'decodeSampledBitmap\(uri,\s*4096\)',
           'decodeSampledBitmap(uri, radiographDecodeLimit())', a)
a = re.sub(r'decodeSampledBitmap\(\s*uri,\s*4096\s*\)',
           'decodeSampledBitmap(\n                            uri,\n                            radiographDecodeLimit()\n                    )', a)

if 'private int radiographDecodeLimit()' not in a:
    decode_anchor = '    private Bitmap decodeSampledBitmap(\n'
    if decode_anchor not in a:
        raise RuntimeError('Could not locate decodeSampledBitmap anchor')
    adaptive_method = r'''    private int radiographDecodeLimit() {
        ActivityManager manager =
                (ActivityManager) getSystemService(ACTIVITY_SERVICE);

        int memoryClass =
                manager == null ? 256 : manager.getMemoryClass();

        boolean lowRam =
                Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT
                        && manager != null
                        && manager.isLowRamDevice();

        // Preserve full diagnostic display resolution on capable devices while
        // avoiding multi-megapixel ARGB allocations on modest phones.
        if (lowRam || memoryClass <= 128) return 2048;
        if (memoryClass <= 256) return 3072;
        return 4096;
    }

'''
    a = a.replace(decode_anchor, adaptive_method + decode_anchor, 1)

if 'private void openPdfViewer(Uri uri)' not in a:
    bitmap_anchor = '    private void writePendingBitmap(\n'
    if bitmap_anchor not in a:
        raise RuntimeError('Could not locate writePendingBitmap anchor')
    viewer_method = r'''    private void openPdfViewer(Uri uri) {
        if (uri == null) return;
        try {
            Intent intent = new Intent(this, PdfViewerActivity.class);
            intent.setData(uri);
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            startActivity(intent);
        } catch (Exception e) {
            Toast.makeText(
                    this,
                    "El PDF se guardó, pero no se pudo abrir el visor interno.",
                    Toast.LENGTH_LONG
            ).show();
        }
    }

'''
    a = a.replace(bitmap_anchor, viewer_method + bitmap_anchor, 1)

# Open the internal viewer after successful PDF write. Scope replacement around
# the unique success message to avoid touching image export.
pdf_success = '''            Toast.makeText(\n                    this,\n                    "Informe PDF guardado correctamente.",\n                    Toast.LENGTH_LONG\n            ).show();\n'''
if 'openPdfViewer(uri);' not in a:
    if pdf_success not in a:
        raise RuntimeError('Could not locate PDF success toast')
    a = a.replace(pdf_success, pdf_success + '\n            openPdfViewer(uri);\n', 1)

activity.write_text(a, encoding='utf-8')

# -----------------------------------------------------------------------------
# 4) Screen classes. Default layout becomes the compact <360dp phone layout;
#    >=360dp portrait gets the normal phone layout; sw600dp and sw840dp get
#    dedicated tablet layouts. Landscape remains the dedicated land layout.
# -----------------------------------------------------------------------------
portrait = Path('app/src/main/res/layout/activity_analysis.xml')
normal_phone = Path('app/src/main/res/layout-w360dp-port/activity_analysis.xml')
normal_phone.parent.mkdir(parents=True, exist_ok=True)
normal_phone.write_text(portrait.read_text(encoding='utf-8'), encoding='utf-8')

small = portrait.read_text(encoding='utf-8')
small = small.replace('android:padding="6dp"', 'android:padding="4dp"', 1)
small = small.replace('android:textSize="15sp"', 'android:textSize="13sp"', 1)
small = small.replace('android:layout_height="52dp"', 'android:layout_height="46dp"', 1)
small = small.replace('android:layout_height="44dp"', 'android:layout_height="40dp"', 1)
small = small.replace('android:layout_height="58dp"', 'android:layout_height="52dp"', 2)
small = small.replace('android:layout_marginLeft="8dp"', 'android:layout_marginLeft="4dp"')
small = small.replace('android:layout_marginRight="8dp"', 'android:layout_marginRight="4dp"')
portrait.write_text(small, encoding='utf-8')

sw600 = Path('app/src/main/res/layout-sw600dp/activity_analysis.xml')
if sw600.exists():
    sw840 = Path('app/src/main/res/layout-sw840dp/activity_analysis.xml')
    sw840.parent.mkdir(parents=True, exist_ok=True)
    large = sw600.read_text(encoding='utf-8')
    large = large.replace('android:layout_width="360dp"', 'android:layout_width="430dp"', 1)
    large = large.replace('android:textSize="10.5sp"', 'android:textSize="11.5sp"', 1)
    sw840.write_text(large, encoding='utf-8')

# Home screen: keep buttons centered and bounded on tablets rather than stretching
# across the entire screen.
main = Path('app/src/main/res/layout/activity_main.xml')
if main.exists():
    base = main.read_text(encoding='utf-8')
    for qualifier, width in [('layout-sw600dp', '560dp'), ('layout-sw840dp', '680dp')]:
        target = Path('app/src/main/res') / qualifier / 'activity_main.xml'
        target.parent.mkdir(parents=True, exist_ok=True)
        tablet = base.replace(
            '    <LinearLayout\n        android:layout_width="match_parent"',
            f'    <LinearLayout\n        android:layout_width="{width}"\n        android:layout_gravity="center_horizontal"',
            1
        )
        tablet = tablet.replace('android:layout_height="168dp"', 'android:layout_height="184dp"', 1)
        target.write_text(tablet, encoding='utf-8')

# -----------------------------------------------------------------------------
# 5) Build identity for this adaptation pass.
# -----------------------------------------------------------------------------
gradle = Path('app/build.gradle')
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+29\b', 'versionCode 30', g, count=1)
g = re.sub(r"versionName\s+'1\.28'", "versionName '1.29'", g, count=1)
gradle.write_text(g, encoding='utf-8')

# Guardrails so CI fails if critical requested features disappear.
checks = {
    'SQLite database': 'StudyDatabase.save(context, study.id' in store.read_text(encoding='utf-8'),
    'PDF viewer activity': pdf_java.exists(),
    'PDF auto preview': 'openPdfViewer(uri);' in activity.read_text(encoding='utf-8'),
    'low RAM decode': 'radiographDecodeLimit()' in activity.read_text(encoding='utf-8'),
    'small phone layout': normal_phone.exists(),
    'tablet PDF layout': pdf_tablet.exists(),
}
missing = [name for name, ok in checks.items() if not ok]
if missing:
    raise RuntimeError('Adaptive/device/database/PDF checks failed: ' + ', '.join(missing))

print('Adaptive phone/tablet layouts, low-RAM image policy, SQLite study database, and in-app PDF viewer applied.')
