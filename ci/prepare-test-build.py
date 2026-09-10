from pathlib import Path

analysis = Path('app/src/main/java/com/cefalo/angulos/AnalysisActivity.java')
text = analysis.read_text(encoding='utf-8')

old = '''        } else {
            definitions = MeasurementCatalog.steiner();
        }
'''
new = '''        } else {
            definitions = MeasurementCatalog.steiner();
            linearDefinitions = LinearMeasurementCatalog.cephalometric();
        }
'''
if old in text:
    text = text.replace(old, new, 1)

needle = '''        if (def.type == LinearMeasurementDefinition.Type.DISTANCE) {
            PointF a = measurementView.getPoint(def.pointLabels[0]);
            PointF b = measurementView.getPoint(def.pointLabels[1]);

            if (a == null || b == null) return null;

            return Math.hypot(
                    b.x - a.x,
                    b.y - a.y
            ) * mmPerPixel;
        }

        PointF a = measurementView.getPoint(def.pointLabels[0]);
'''
replacement = '''        if (def.type == LinearMeasurementDefinition.Type.DISTANCE) {
            PointF a = measurementView.getPoint(def.pointLabels[0]);
            PointF b = measurementView.getPoint(def.pointLabels[1]);

            if (a == null || b == null) return null;

            return Math.hypot(
                    b.x - a.x,
                    b.y - a.y
            ) * mmPerPixel;
        }

        if (def.type == LinearMeasurementDefinition.Type.AXIAL_PROJECTION) {
            PointF a = measurementView.getPoint(def.pointLabels[0]);
            PointF b = measurementView.getPoint(def.pointLabels[1]);
            PointF p = measurementView.getPoint(def.pointLabels[2]);

            if (a == null || b == null || p == null) return null;

            double dx = b.x - a.x;
            double dy = b.y - a.y;
            double length = Math.hypot(dx, dy);
            if (length == 0.0) return null;

            double axialPixels =
                    ((p.x - a.x) * dx + (p.y - a.y) * dy) / length;

            // SL y SE son longitudes S-L / S-E sobre el eje SN, no distancias
            // perpendiculares. Se informa la magnitud de la proyección construida.
            return Math.abs(axialPixels) * mmPerPixel;
        }

        PointF a = measurementView.getPoint(def.pointLabels[0]);
'''
if needle in text:
    text = text.replace(needle, replacement, 1)

old_complete = '''        if (!measurementView.isComplete()) {
            String next =
                    measurementView.getCurrentLabel();

            Toast.makeText(
                    this,
                    "Faltan puntos. Seleccionado: " +
                    (
                            next == null
                                    ? "—"
                                    : next
                    ),
                    Toast.LENGTH_LONG
            ).show();

            return;
        }

'''
new_complete = '''        if (measurementView.getPlacedCount() < 2) {
            Toast.makeText(
                    this,
                    "Coloque los puntos necesarios para al menos una medición.",
                    Toast.LENGTH_LONG
            ).show();
            return;
        }

'''
if old_complete in text:
    text = text.replace(old_complete, new_complete, 1)

analysis.write_text(text, encoding='utf-8')

# Flujo de colocación: no avanzar automáticamente al siguiente punto faltante.
view = Path('app/src/main/java/com/cefalo/angulos/MeasurementView.java')
v = view.read_text(encoding='utf-8')
auto_advance = '''                    if (editingPointWasMissing) {
                        int nextMissing =
                                nextMissingIndex(selectedIndex);

                        if (nextMissing >= 0) {
                            selectedIndex = nextMissing;
                        }
                    }

'''
if auto_advance in v:
    v = v.replace(auto_advance, '', 1)
view.write_text(v, encoding='utf-8')

# Guías para las construcciones de SL y SE.
guide = Path('app/src/main/java/com/cefalo/angulos/PointGuide.java')
g = guide.read_text(encoding='utf-8')
anchor = '        GUIDE.put("Gn", "Gnathion (Gn):'
idx = g.find(anchor)
if idx != -1 and 'GUIDE.put("Pg"' not in g:
    line_end = g.find('\n', idx)
    extra = '''\n        GUIDE.put("Pg", "Pogonion (Pg): punto más anterior del contorno óseo de la sínfisis mandibular. Para SL, el software proyecta Pg perpendicularmente sobre SN para construir L.");\n        GUIDE.put("Cóndilo posterior", "Contorno posterior del cóndilo: marque el punto más posterior de la cabeza condilar mandibular visible. Para SE, el software lo proyecta perpendicularmente sobre SN para construir E.");'''
    g = g[:line_end] + extra + g[line_end:]
guide.write_text(g, encoding='utf-8')

print('Test-build clinical/flow patches applied.')
