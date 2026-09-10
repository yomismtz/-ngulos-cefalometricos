from pathlib import Path

# Final radiographic audit for the mobile build.
# Runs after the historical redesign patch scripts so that the APK is built from
# one clinically reviewed set of values and wording. The source document supplied
# by the project owner is used as a checklist, but ambiguous/inconsistent values
# are not copied blindly.

# -----------------------------------------------------------------------------
# Angular measurements: lateral cephalogram
# -----------------------------------------------------------------------------
catalog = Path('app/src/main/java/com/cefalo/angulos/MeasurementCatalog.java')
m = catalog.read_text(encoding='utf-8')

# Steiner mandibular plane: classic reference 32 +/- 5 deg.
m = m.replace(
    '''                28, 36,\n                "32° ± 4°",\n                "Marque S-N y Go-Gn.",''',
    '''                27, 37,\n                "32° ± 5° · referencia clásica de Steiner",\n                "Marque 4 puntos: S y N forman la base craneal anterior; Go y Gn forman el plano mandibular.",'''
)
m = m.replace(
    '"SN/Go-Gn dentro del intervalo 32° ± 4° de la referencia adoptada."',
    '"SN/Go-Gn dentro del intervalo 32° ± 5° de la referencia clásica adoptada."'
)

# U1-NA: the classical nominal value is 22 deg; commonly reproduced SD is ~2 deg.
m = m.replace(
    '''                16, 28,\n                "22° ± 6°",\n                "Marque el eje del incisivo superior y la línea N-A.",''',
    '''                20, 24,\n                "22° ± 2° · referencia clásica de Steiner",\n                "Marque 4 puntos: borde y ápice del incisivo superior para formar su eje; N y A para formar la línea NA.",'''
)
m = m.replace(
    '"Incisivo superior dentro del intervalo angular 22° ± 6° de la referencia adoptada."',
    '"Incisivo superior dentro del intervalo angular 22° ± 2° de la referencia clásica adoptada."'
)

# Make the already-correct L1-NB variability explicit; do not use the 16 deg
# entry present in the supplied teaching sheet because it conflicts with the
# classical Steiner definition/value (25 deg).
m = m.replace(
    '"25° ± 4°",\n                "Marque el eje del incisivo inferior y la línea N-B."',
    '"25° ± 4° · referencia clásica de Steiner",\n                "Marque 4 puntos: borde y ápice del incisivo inferior para formar su eje; N y B para formar la línea NB."'
)

# More explicit construction wording for recurrent planes.
m = m.replace(
    '"Marque S-N y S-Gn."',
    '"Marque N, S y Gn. La app forma NS y el eje S-Gn; S es el punto compartido."'
)
m = m.replace(
    '"Marque el eje del incisivo superior y S-N."',
    '"Marque 4 puntos: borde y ápice del incisivo superior para formar su eje; S y N para formar SN."'
)
m = m.replace(
    '"Construya el plano oclusal con sus dos puntos y compárelo con S-N."',
    '"Marque 4 puntos: Oclusal 1 y Oclusal 2 forman el plano oclusal; S y N forman SN."'
)
m = m.replace(
    '"Marque los ejes longitudinales de los incisivos superior e inferior."',
    '"Marque 4 puntos: borde y ápice del incisivo superior, y borde y ápice del incisivo inferior. Cada par forma un eje longitudinal."'
)

# Add SN-FH because it reuses four easy/common landmarks and is useful for
# judging whether SN itself is unusually inclined. It is deliberately
# descriptive: the literature reports a typical value near 7 deg but also
# meaningful individual/population variation.
steiner_return = '''        return list;\n    }\n\n    /** Módulo: Postura cráneo-cervical. */'''
if 'Inclinación SN / Frankfort' not in m and steiner_return in m:
    addition = '''        list.add(m(\n                "Inclinación SN / Frankfort",\n                TWO_LINES,\n                p("S", "N", "Po", "Or"),\n                Double.NaN,\n                Double.NaN,\n                "Referencia aproximada ≈7°; existe variación individual y poblacional",\n                "Marque 4 puntos: S-N forma la base craneal anterior y Po-Or forma el plano de Frankfort.",\n                "",\n                "Describe la inclinación de SN respecto a Frankfort. Un valor alejado de ~7° puede modificar la lectura de otras medidas basadas en SN; no se usa aquí como diagnóstico aislado de biotipo.",\n                "",\n                false\n        ));\n\n'''
    m = m.replace(steiner_return, addition + steiner_return, 1)

# Tangent constructions: counts and exact landmarks must be explicit.
m = m.replace(
    '"Marque S-N y OPT, formada por CV2tg-CV2ip."',
    '"Marque 4 puntos: S y N forman SN; CV2tg y CV2ip forman la tangente OPT. CV2tg es un punto, no una línea."'
)
m = m.replace(
    '"Marque S-N y CVT, formada por CV2tg-CV4ip."',
    '"Marque 4 puntos: S y N forman SN; CV2tg y CV4ip forman la tangente CVT. CV2tg es un punto, no una línea."'
)
m = m.replace(
    '"Marque CV2tg, CV4ip y CV6ip. El software forma CVT y EVT."',
    '"Marque 3 puntos: CV2tg, CV4ip y CV6ip. CVT = CV2tg-CV4ip y EVT = CV4ip-CV6ip; ambas líneas comparten CV4ip."'
)

# Tweed: use the values commonly reported in the classic comparison table.
m = m.replace(
    '''                20, 30,\n                "25° ± 5° · referencia clásica del triángulo",''',
    '''                21, 29,\n                "25° ± 4° · referencia clásica de Tweed",'''
)
m = m.replace('"FMA dentro de 25° ± 5°."', '"FMA dentro de 25° ± 4°."')
m = m.replace(
    '''                60, 70,\n                "65° ± 5° · ideal clásico 65°; interpretar junto con FMA e IMPA",''',
    '''                61, 69,\n                "65° ± 4° · referencia clásica; interpretar junto con FMA e IMPA",'''
)
m = m.replace('"FMIA dentro del intervalo central 65° ± 5°."', '"FMIA dentro del intervalo central 65° ± 4°."')
m = m.replace(
    '''                85, 95,\n                "90° ± 5° · referencia clásica",''',
    '''                86, 94,\n                "90° ± 4° · referencia clásica de Tweed",'''
)
m = m.replace('"IMPA dentro de 90° ± 5°."', '"IMPA dentro de 90° ± 4°."')

# Powell: preserve broad classical teaching interval but state variation.
m = m.replace(
    '"80°–95° · algunas publicaciones utilizan un intervalo más estrecho"',
    '"80°–95° · intervalo docente clásico amplio; algunas fuentes publican 80°–85°"'
)

catalog.write_text(m, encoding='utf-8')

# -----------------------------------------------------------------------------
# Linear measurements: Steiner + upper airway
# -----------------------------------------------------------------------------
linear = Path('app/src/main/java/com/cefalo/angulos/LinearMeasurementCatalog.java')
l = linear.read_text(encoding='utf-8')

# SL/SE: use classical values and realistic published variability.
l = l.replace(
    '''                47.0,\n                55.0,\n                "51 ± 4 mm · referencia cefalométrica clásica",''',
    '''                47.0,\n                55.0,\n                "51 ± 4 mm · referencia clásica de Steiner (aprox.)",'''
)
l = l.replace(
    '''                19.0,\n                25.0,\n                "22 ± 3 mm · referencia cefalométrica clásica",''',
    '''                20.0,\n                24.0,\n                "22 ± 2 mm · referencia clásica de Steiner (aprox.)",'''
)
l = l.replace('"SE dentro de 22 ± 3 mm de la referencia adoptada."', '"SE dentro de 22 ± 2 mm de la referencia clásica adoptada."')

# Linear incisor positions: do not leave the result without an interval.
l = l.replace(
    '''                Double.NaN,\n                Double.NaN,\n                "4 mm · valor clásico; sin tolerancia automática adoptada",\n                "",\n                "Distancia perpendicular del borde incisal superior a la línea NA. El valor clásico de referencia es 4 mm; interpretar con edad, población y el resto del análisis.",\n                ""\n        ));''',
    '''                2.0,\n                6.0,\n                "4 ± 2 mm · referencia clásica de Steiner",\n                "Borde incisal superior relativamente más posterior respecto a NA para la referencia adoptada; interpretar junto con la angulación 1-NA.",\n                "Distancia 1-NA dentro de 4 ± 2 mm de la referencia clásica adoptada.",\n                "Borde incisal superior relativamente más anterior respecto a NA para la referencia adoptada; interpretar junto con la angulación 1-NA."\n        ));''',
    1
)
l = l.replace(
    '''                Double.NaN,\n                Double.NaN,\n                "4 mm · valor clásico; sin tolerancia automática adoptada",\n                "",\n                "Distancia perpendicular del borde incisal inferior a la línea NB. El valor clásico de referencia es 4 mm; interpretar con edad, población y el resto del análisis.",\n                ""\n        ));''',
    '''                3.0,\n                5.0,\n                "4 ± 1 mm · referencia clásica de Steiner",\n                "Borde incisal inferior relativamente más posterior respecto a NB para la referencia adoptada; interpretar junto con la angulación 1-NB.",\n                "Distancia 1-NB dentro de 4 ± 1 mm de la referencia clásica adoptada.",\n                "Borde incisal inferior relativamente más anterior respecto a NB para la referencia adoptada; interpretar junto con la angulación 1-NB."\n        ));''',
    1
)

# Add the directly defined Linder-Aronson/Solow airway component distances.
# They remain descriptive because age/sex/population-specific reference data are
# required for a defensible automatic classification.
airway_anchor = '''        list.add(m("Adenoides · AD3 · tu-ad3", DISTANCE, RANGE,'''
if 'Adenoides · AD1-Ba' not in l and airway_anchor in l:
    additions = '''        list.add(m("Adenoides · AD1-Ba · espesor inferior", DISTANCE, RANGE,\n                p("AD1", "Ba"), Double.NaN, Double.NaN,\n                "AD1-Ba: espesor adenoideo inferior sobre la construcción PNS/ENP-Ba; sin umbral universal automático", "",\n                "Medida descriptiva del tejido adenoideo inferior. Debe interpretarse con edad, sexo y la referencia poblacional seleccionada.", ""));\n\n        list.add(m("Nasofaringe · ENP-Ba · dimensión inferior total", DISTANCE, RANGE,\n                p("ENP", "Ba"), Double.NaN, Double.NaN,\n                "PNS/ENP-Ba: dimensión total de la construcción inferior; sin umbral universal automático", "",\n                "Medida anatómica de referencia para contextualizar ENP-AD1 y AD1-Ba. No diagnostica obstrucción por sí sola.", ""));\n\n        list.add(m("Adenoides · AD2-Hormion · espesor superior", DISTANCE, RANGE,\n                p("AD2", "Hormion"), Double.NaN, Double.NaN,\n                "AD2-Hormion: espesor adenoideo superior sobre la perpendicular PNS/ENP a S-Ba", "",\n                "Medida descriptiva del tejido adenoideo superior. Interpretar con una referencia específica de edad/población.", ""));\n\n        list.add(m("Nasofaringe · ENP-Hormion · dimensión superior total", DISTANCE, RANGE,\n                p("ENP", "Hormion"), Double.NaN, Double.NaN,\n                "PNS/ENP-Hormion: dimensión superior total sobre la perpendicular a S-Ba", "",\n                "Medida anatómica de referencia para contextualizar ENP-AD2 y AD2-Hormion. No diagnostica función respiratoria por sí sola.", ""));\n\n'''
    l = l.replace(airway_anchor, additions + airway_anchor, 1)

# Ensure build-time renamed McNamara entries carry exact minimum-distance wording.
l = l.replace(
    '"Referencia cefalométrica de McNamara; interpretar con edad y protocolo", "",\n                "Comparar con la referencia apropiada. Una telerradiografía lateral 2D no diagnostica obstrucción ni apnea del sueño."',
    '"McNamara: distancia MÍNIMA entre el borde posterior del paladar blando y el punto más cercano de la pared faríngea posterior", "",\n                "Un valor menor describe un calibre cefalométrico superior más estrecho y uno mayor un calibre más amplio. No diagnostica obstrucción ni apnea del sueño en una imagen 2D."',
    1
)
l = l.replace(
    '"Referencia cefalométrica de McNamara; interpretar con edad y protocolo", "",\n                "Comparar con la referencia apropiada. Una telerradiografía lateral 2D no diagnostica apnea ni hipertrofia amigdalina."',
    '"McNamara: distancia MÍNIMA desde la base/posterior de la lengua al punto más cercano de la pared faríngea posterior", "",\n                "Un valor menor describe un calibre cefalométrico inferior más estrecho y uno mayor un calibre más amplio. No diagnostica apnea ni hipertrofia amigdalina en una imagen 2D."',
    1
)

linear.write_text(l, encoding='utf-8')

# -----------------------------------------------------------------------------
# Landmark help corrections/additions
# -----------------------------------------------------------------------------
guide = Path('app/src/main/java/com/cefalo/angulos/PointGuide.java')
g = guide.read_text(encoding='utf-8')

# Point D is the center of the symphysis image used by Steiner; avoid implying a
# mathematically exact geometric centroid when it is located radiographically.
g = g.replace(
    'GUIDE.put("D", "Punto D: centro geométrico de la sínfisis mandibular; es un punto construido, no un accidente anatómico superficial.");',
    'GUIDE.put("D", "Punto D de Steiner: punto localizado en el centro de la imagen radiográfica de la sínfisis mandibular. Es una referencia construida dentro de la sínfisis, no un accidente anatómico superficial.");'
)

# Correct wording for L/E: the app projects the anatomical point orthogonally to
# SN to construct L/E; SL and SE are then measured along SN from S.
g = g.replace(
    'GUIDE.put("Pg", "Pogonion óseo (Pg): punto más anterior del contorno óseo de la sínfisis mandibular. Para SL el software proyecta Pg perpendicularmente sobre SN; no debe marcarse un punto L adicional.");',
    'GUIDE.put("Pg", "Pogonion óseo (Pg): punto más anterior del contorno óseo de la sínfisis mandibular. Para SL, la app traza implícitamente una perpendicular desde Pg hasta SN para construir L y después mide S-L sobre SN; no marque L manualmente.");'
)
g = g.replace(
    'GUIDE.put("Cóndilo posterior", "Punto condilar posterior para SE: punto más posterior del contorno de la cabeza condilar visible. El software proyecta este punto perpendicularmente sobre SN para construir E; no debe marcarse E manualmente.");',
    'GUIDE.put("Cóndilo posterior", "Referencia condilar posterior para SE: marque el punto más posterior del contorno visible de la cabeza condilar. La app traza implícitamente una perpendicular hasta SN para construir E y después mide S-E sobre SN; no marque E manualmente.");'
)

if 'GUIDE.put("Hormion"' not in g:
    anchor = '        GUIDE.put("Ba", "Basion (Ba): punto medio del borde anterior del foramen magno.");\n'
    g = g.replace(
        anchor,
        anchor + '        GUIDE.put("Hormion", "Hormion (Ho): punto de la base craneal donde la perpendicular trazada desde ENP/PNS a la línea S-Ba intercepta el contorno esfenoidal. Se usa para contextualizar la construcción superior AD2; no confundir con H del hueso hioides.");\n',
        1
    )

# More conservative panoramic middle-line wording: a panoramic midline is a
# construction and should not claim metric accuracy if the patient is rotated.
g = g.replace(
    'GUIDE.put("LM sup.", "Línea media maxilar superior: punto superior sobre una línea media vertical del maxilar que siga el tabique nasal visible en la panorámica.");',
    'GUIDE.put("LM sup.", "Línea media maxilar, punto superior: seleccione una referencia estable sobre el eje del tabique/septo nasal visible. Junto con LM inf. construye una línea media de comparación; si la panorámica está rotada, la simetría métrica pierde confiabilidad.");'
)

guide.write_text(g, encoding='utf-8')

# -----------------------------------------------------------------------------
# Mobile text: explicitly identify reference scope in final report title/notes.
# -----------------------------------------------------------------------------
analysis = Path('app/src/main/java/com/cefalo/angulos/AnalysisActivity.java')
a = analysis.read_text(encoding='utf-8')

# The final report should not imply that any chosen population reference is a
# universal diagnosis. This is intentionally additive and harmless if wording
# changed in another patch.
a = a.replace(
    '"Uso educativo · No sustituye valoración profesional"',
    '"Uso educativo · Valores de referencia dependientes del método/población · No sustituye valoración profesional"'
)
analysis.write_text(a, encoding='utf-8')

print('Final radiographic audit applied: lateral ceph + panoramic modules only.')
