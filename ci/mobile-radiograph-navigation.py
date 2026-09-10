from pathlib import Path
import re

# -----------------------------------------------------------------------------
# 1) MeasurementView: halve visible point markers and expose viewport panning.
# -----------------------------------------------------------------------------
view = Path('app/src/main/java/com/cefalo/angulos/MeasurementView.java')
v = view.read_text(encoding='utf-8')

# The previous mobile patch intentionally made markers small. The user requested
# another 50% visual reduction. The invisible hit radius remains unchanged so
# points stay easy to select even though they cover much less anatomy.
replacements = {
    'dp(5.2f), haloPaint': 'dp(2.6f), haloPaint',
    'dp(i == selectedIndex ? 3.8f : 3.2f)': 'dp(i == selectedIndex ? 1.9f : 1.6f)',
    'dp(7.2f), lockedRingPaint': 'dp(3.6f), lockedRingPaint',
    'dp(7.5f), selectedRingPaint': 'dp(3.8f), selectedRingPaint',
    's.x - dp(11), s.y, s.x - dp(6)': 's.x - dp(6), s.y, s.x - dp(3)',
    's.x + dp(6), s.y, s.x + dp(11)': 's.x + dp(3), s.y, s.x + dp(6)',
    's.x, s.y - dp(11), s.x, s.y - dp(6)': 's.x, s.y - dp(6), s.x, s.y - dp(3)',
    's.x, s.y + dp(6), s.x, s.y + dp(11)': 's.x, s.y + dp(3), s.x, s.y + dp(6)',
}
for old, new in replacements.items():
    v = v.replace(old, new)

# Reduce ring stroke widths as well, otherwise the rings would still dominate.
v = v.replace('selectedRingPaint.setStrokeWidth(dp(3));',
              'selectedRingPaint.setStrokeWidth(dp(1.5f));')
v = v.replace('lockedRingPaint.setStrokeWidth(dp(3));',
              'lockedRingPaint.setStrokeWidth(dp(1.5f));')

# Viewport listener interface.
calibration_interface = '''    public interface CalibrationListener {
        void onCalibrationReady(PointF first, PointF second, double pixelDistance);
    }
'''
viewport_interface = calibration_interface + '''
    public interface ViewportListener {
        void onViewportChanged(
                float horizontalFraction,
                float verticalFraction,
                boolean horizontalEnabled,
                boolean verticalEnabled
        );
    }
'''
if 'interface ViewportListener' not in v:
    if calibration_interface not in v:
        raise RuntimeError('Could not locate CalibrationListener in MeasurementView')
    v = v.replace(calibration_interface, viewport_interface, 1)

listener_field = '    private CalibrationListener calibrationListener;\n'
if 'private ViewportListener viewportListener;' not in v:
    if listener_field not in v:
        raise RuntimeError('Could not locate calibration listener field')
    v = v.replace(listener_field,
                  listener_field + '    private ViewportListener viewportListener;\n', 1)

viewport_anchor = '    private int firstMissingIndex() {\n'
if 'public void setHorizontalPanFraction(' not in v:
    viewport_methods = '''    public void setViewportListener(ViewportListener listener) {
        viewportListener = listener;
        post(this::notifyViewportChanged);
    }

    public void setHorizontalPanFraction(float fraction) {
        if (bitmap == null || getWidth() <= 0 || getHeight() <= 0) return;

        RectF rect = mappedImageRect();
        if (rect.width() <= getWidth() + 0.5f) {
            notifyViewportChanged();
            return;
        }

        float f = clamp(fraction, 0f, 1f);
        float targetLeft = -(rect.width() - getWidth()) * f;
        matrix.postTranslate(targetLeft - rect.left, 0f);
        constrainImageToViewport();
        updateInverse();
        invalidate();
    }

    public void setVerticalPanFraction(float fraction) {
        if (bitmap == null || getWidth() <= 0 || getHeight() <= 0) return;

        RectF rect = mappedImageRect();
        if (rect.height() <= getHeight() + 0.5f) {
            notifyViewportChanged();
            return;
        }

        float f = clamp(fraction, 0f, 1f);
        float targetTop = -(rect.height() - getHeight()) * f;
        matrix.postTranslate(0f, targetTop - rect.top);
        constrainImageToViewport();
        updateInverse();
        invalidate();
    }

    private RectF mappedImageRect() {
        RectF rect = new RectF();
        if (bitmap == null) return rect;

        rect.set(0f, 0f, bitmap.getWidth(), bitmap.getHeight());
        matrix.mapRect(rect);
        return rect;
    }

    private void notifyViewportChanged() {
        if (viewportListener == null) return;

        if (bitmap == null || getWidth() <= 0 || getHeight() <= 0) {
            viewportListener.onViewportChanged(0.5f, 0.5f, false, false);
            return;
        }

        RectF rect = mappedImageRect();
        boolean horizontalEnabled = rect.width() > getWidth() + 0.5f;
        boolean verticalEnabled = rect.height() > getHeight() + 0.5f;

        float horizontalFraction = 0.5f;
        float verticalFraction = 0.5f;

        if (horizontalEnabled) {
            horizontalFraction = clamp(
                    -rect.left / Math.max(1f, rect.width() - getWidth()),
                    0f,
                    1f
            );
        }

        if (verticalEnabled) {
            verticalFraction = clamp(
                    -rect.top / Math.max(1f, rect.height() - getHeight()),
                    0f,
                    1f
            );
        }

        viewportListener.onViewportChanged(
                horizontalFraction,
                verticalFraction,
                horizontalEnabled,
                verticalEnabled
        );
    }

'''
    if viewport_anchor not in v:
        raise RuntimeError('Could not locate viewport method anchor')
    v = v.replace(viewport_anchor, viewport_methods + viewport_anchor, 1)

# Keep both bars synchronized after zoom, fit, centering, two-finger pan, and
# automatic edge pan. Fresh CI checkouts mean this replacement is idempotent
# for each build.
if 'notifyViewportChanged();\n        invalidate();' not in v:
    v = v.replace('updateInverse();\n', 'updateInverse();\n        notifyViewportChanged();\n')
else:
    # New methods added above may still need notifications after updateInverse.
    v = re.sub(r'updateInverse\(\);\n(?!\s*notifyViewportChanged\(\);)',
               'updateInverse();\n        notifyViewportChanged();\n', v)

view.write_text(v, encoding='utf-8')

# -----------------------------------------------------------------------------
# 2) Layouts: reserve a bottom horizontal bar and a right vertical bar around
#    the radiograph. This works in portrait, landscape, and generated tablet UI.
# -----------------------------------------------------------------------------
def wrap_measurement_view(path: Path):
    if not path.exists():
        return
    s = path.read_text(encoding='utf-8')
    if '@+id/horizontalPanBar' in s:
        return

    pattern = re.compile(
        r'(?P<indent>[ \t]*)<com\.cefalo\.angulos\.MeasurementView\n'
        r'(?P<body>.*?android:id="@\+id/measurementView".*?)/>',
        re.S
    )
    match = pattern.search(s)
    if not match:
        raise RuntimeError(f'Could not locate measurementView in {path}')

    indent = match.group('indent')
    body = match.group('body')

    # Keep all outer LinearLayout sizing/margin attributes from the existing
    # MeasurementView, but move the dark panel background to the inner view.
    body_outer = re.sub(r'\n\s*android:background="@drawable/panel_dark"', '', body)
    body_outer = body_outer.replace('android:id="@+id/measurementView"',
                                    'android:id="@+id/radiographViewport"')

    inner = f'''{indent}<FrameLayout\n{body_outer}>\n\n'''
    inner += f'''{indent}    <com.cefalo.angulos.MeasurementView
{indent}        android:id="@+id/measurementView"
{indent}        android:layout_width="match_parent"
{indent}        android:layout_height="match_parent"
{indent}        android:layout_marginRight="30dp"
{indent}        android:layout_marginBottom="30dp"
{indent}        android:background="@drawable/panel_dark" />

'''
    inner += f'''{indent}    <SeekBar
{indent}        android:id="@+id/horizontalPanBar"
{indent}        android:layout_width="match_parent"
{indent}        android:layout_height="30dp"
{indent}        android:layout_gravity="bottom|start"
{indent}        android:layout_marginRight="30dp"
{indent}        android:max="1000"
{indent}        android:progress="500"
{indent}        android:splitTrack="false"
{indent}        android:paddingLeft="8dp"
{indent}        android:paddingRight="8dp"
{indent}        android:progressTint="@color/brand_purple"
{indent}        android:progressBackgroundTint="@color/text_secondary"
{indent}        android:thumbTint="@color/brand_teal"
{indent}        android:contentDescription="@string/radiograph_pan_horizontal" />

'''
    inner += f'''{indent}    <com.cefalo.angulos.VerticalPanSeekBar
{indent}        android:id="@+id/verticalPanBar"
{indent}        android:layout_width="30dp"
{indent}        android:layout_height="match_parent"
{indent}        android:layout_gravity="end|top"
{indent}        android:layout_marginBottom="30dp"
{indent}        android:max="1000"
{indent}        android:progress="500"
{indent}        android:splitTrack="false"
{indent}        android:paddingLeft="8dp"
{indent}        android:paddingRight="8dp"
{indent}        android:progressTint="@color/brand_purple"
{indent}        android:progressBackgroundTint="@color/text_secondary"
{indent}        android:thumbTint="@color/brand_teal"
{indent}        android:contentDescription="@string/radiograph_pan_vertical" />
{indent}</FrameLayout>'''

    s = s[:match.start()] + inner + s[match.end():]
    path.write_text(s, encoding='utf-8')

for rel in [
    'app/src/main/res/layout/activity_analysis.xml',
    'app/src/main/res/layout-land/activity_analysis.xml',
    'app/src/main/res/layout-sw600dp/activity_analysis.xml',
]:
    wrap_measurement_view(Path(rel))

# -----------------------------------------------------------------------------
# 3) AnalysisActivity: wire both bars and compact the angular/linear result
#    cards so they no longer dominate the bottom of smaller phone screens.
# -----------------------------------------------------------------------------
activity = Path('app/src/main/java/com/cefalo/angulos/AnalysisActivity.java')
a = activity.read_text(encoding='utf-8')

if 'import android.widget.SeekBar;' not in a:
    a = a.replace('import android.widget.ScrollView;\n',
                  'import android.widget.ScrollView;\nimport android.widget.SeekBar;\n', 1)

bind_anchor = '        measurementView = findViewById(R.id.measurementView);\n'
if 'horizontalPanBar = findViewById(R.id.horizontalPanBar)' not in a:
    if bind_anchor not in a:
        raise RuntimeError('Could not locate MeasurementView binding in AnalysisActivity')
    a = a.replace(
        bind_anchor,
        bind_anchor +
        '        SeekBar horizontalPanBar = findViewById(R.id.horizontalPanBar);\n' +
        '        VerticalPanSeekBar verticalPanBar = findViewById(R.id.verticalPanBar);\n',
        1
    )

progress_anchor = '        measurementView.setProgressListener(this::updateProgress);\n'
if 'setViewportListener((horizontalFraction' not in a:
    wiring = '''        final boolean[] syncingViewportBars = {false};

        if (horizontalPanBar != null && verticalPanBar != null) {
            horizontalPanBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
                @Override
                public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                    if (!fromUser || syncingViewportBars[0]) return;
                    measurementView.setHorizontalPanFraction(
                            progress / (float) Math.max(1, seekBar.getMax())
                    );
                }

                @Override public void onStartTrackingTouch(SeekBar seekBar) { }
                @Override public void onStopTrackingTouch(SeekBar seekBar) { }
            });

            verticalPanBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
                @Override
                public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                    if (!fromUser || syncingViewportBars[0]) return;
                    float visualFraction = progress / (float) Math.max(1, seekBar.getMax());
                    measurementView.setVerticalPanFraction(1f - visualFraction);
                }

                @Override public void onStartTrackingTouch(SeekBar seekBar) { }
                @Override public void onStopTrackingTouch(SeekBar seekBar) { }
            });

            measurementView.setViewportListener((horizontalFraction, verticalFraction,
                                                  horizontalEnabled, verticalEnabled) -> {
                syncingViewportBars[0] = true;

                horizontalPanBar.setEnabled(horizontalEnabled);
                horizontalPanBar.setAlpha(horizontalEnabled ? 1f : 0.35f);
                horizontalPanBar.setProgress(Math.round(horizontalFraction * horizontalPanBar.getMax()));

                verticalPanBar.setEnabled(verticalEnabled);
                verticalPanBar.setAlpha(verticalEnabled ? 1f : 0.35f);
                verticalPanBar.setProgress(Math.round((1f - verticalFraction) * verticalPanBar.getMax()));

                syncingViewportBars[0] = false;
            });
        }

'''
    if progress_anchor not in a:
        raise RuntimeError('Could not locate progress listener anchor')
    a = a.replace(progress_anchor, progress_anchor + '\n' + wiring, 1)

# Smaller result cards for angles and linear measurements.
a = a.replace('        int pad = dp(18);', '        int pad = dp(10);', 1)
a = a.replace('row.setTextSize(13.5f);', 'row.setTextSize(11.5f);')
a = a.replace('row.setPadding(\n                    dp(14),\n                    dp(12),\n                    dp(14),\n                    dp(12)\n            );',
              'row.setPadding(\n                    dp(9),\n                    dp(6),\n                    dp(9),\n                    dp(6)\n            );')
a = a.replace('row.setPadding(dp(14), dp(12), dp(14), dp(12));',
              'row.setPadding(dp(9), dp(6), dp(9), dp(6));')

results_anchor = '''    private void showResultsDialog() {
        ScrollView scroll = new ScrollView(this);
'''
if results_anchor in a and 'scroll.setClipToPadding(false);' not in a[a.find(results_anchor):a.find(results_anchor)+400]:
    a = a.replace(
        results_anchor,
        results_anchor +
        '        scroll.setClipToPadding(false);\n' +
        '        scroll.setPadding(0, 0, 0, dp(24));\n',
        1
    )

activity.write_text(a, encoding='utf-8')

# -----------------------------------------------------------------------------
# 4) Accessibility strings for the new navigation bars.
# -----------------------------------------------------------------------------
def add_strings(path: Path, horizontal: str, vertical: str):
    if not path.exists():
        return
    s = path.read_text(encoding='utf-8')
    additions = []
    if 'name="radiograph_pan_horizontal"' not in s:
        additions.append(f'    <string name="radiograph_pan_horizontal">{horizontal}</string>')
    if 'name="radiograph_pan_vertical"' not in s:
        additions.append(f'    <string name="radiograph_pan_vertical">{vertical}</string>')
    if additions:
        s = s.replace('</resources>', '\n'.join(additions) + '\n</resources>')
        path.write_text(s, encoding='utf-8')

add_strings(
    Path('app/src/main/res/values/strings.xml'),
    'Desplazar radiografía izquierda/derecha',
    'Desplazar radiografía arriba/abajo'
)
add_strings(
    Path('app/src/main/res/values-en/strings.xml'),
    'Move radiograph left/right',
    'Move radiograph up/down'
)

print('Compact result cards, half-size point markers, and radiograph pan bars applied.')