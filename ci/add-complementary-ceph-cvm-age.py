from pathlib import Path
import re

java_dir = Path('app/src/main/java/com/cefalo/angulos')

# -----------------------------------------------------------------------------
# 1) Complementary angular measurements that reuse landmarks already present in
#    the lateral-cephalogram / cervical / airway workflows.
#
# Important: two classical Downs measures are signed in the historical method.
# The app deliberately reports their MIRROR-INVARIANT MAGNITUDE because a user
# can import a horizontally flipped image. That avoids silently reversing a
# Class-II/Class-III sign when radiograph orientation is unknown.
# -----------------------------------------------------------------------------
catalog = java_dir / 'MeasurementCatalog.java'
m = catalog.read_text(encoding='utf-8')

steiner_anchor = '''        return list;\n    }\n\n    /** Módulo: Postura cráneo-cervical. */'''
if steiner_anchor not in m:
    raise RuntimeError('Could not locate cephalometric catalog insertion point')

if 'Downs · Convexidad N-A-Pg' not in m:
    ceph_additions = r'''        // Complementos cefalométricos publicados que reutilizan landmarks ya disponibles.
        // Las normas se identifican por análisis para no mezclarlas con Steiner.
        list.add(m(
                "Downs · Convexidad N-A-Pg · magnitud",
                TWO_LINES,
                p("N", "A", "A", "Pg"),
                Double.NaN,
                Double.NaN,
                "Downs: valor central ≈0°; rango clásico firmado publicado −8.5° a +10°. YOM informa magnitud para ser invariante al espejo.",
                "Marque N, A y Pg. La app compara la dirección N→A con A→Pg y muestra la desviación angular respecto a la continuidad de ambas líneas.",
                "",
                "Una magnitud pequeña indica poca convexidad/concavidad angular. Para asignar el signo histórico de Downs se requiere conocer la orientación anatómica de la imagen; YOM no lo infiere si la radiografía pudiera estar espejada.",
                "",
                false
        ));

        list.add(m(
                "Downs · Plano A-B / N-Pg · magnitud",
                TWO_LINES,
                p("A", "B", "N", "Pg"),
                Double.NaN,
                Double.NaN,
                "Downs: −4.6° ± 4.2° con signo en el método clásico. YOM informa magnitud por seguridad ante imágenes espejadas.",
                "Marque A, B, N y Pg. Se calcula el ángulo entre el plano A-B y el plano facial N-Pg.",
                "",
                "Medida complementaria de la relación sagital. La magnitud se informa sin signo automático para no invertir la interpretación en una imagen horizontalmente espejada.",
                "",
                false
        ));

        list.add(m(
                "Downs · Ángulo facial · FH / N-Pg",
                TWO_LINES,
                p("Po", "Or", "N", "Pg"),
                84.2,
                91.4,
                "87.8° ± 3.6° · referencia clásica de Downs",
                "Marque Po-Or para Frankfort y N-Pg para el plano facial.",
                "Ángulo facial menor que la referencia de Downs: el pogonion queda relativamente más posterior respecto a Frankfort; correlacione con SNB/ANB.",
                "Dentro de 87.8° ± 3.6° de la referencia clásica de Downs.",
                "Ángulo facial mayor que la referencia de Downs: el pogonion queda relativamente más anterior; correlacione con el resto del patrón sagital.",
                true
        ));

        list.add(m(
                "Downs · Eje Y · S-Gn / FH",
                TWO_LINES,
                p("S", "Gn", "Po", "Or"),
                55.6,
                63.2,
                "59.4° ± 3.8° · referencia clásica de Downs",
                "Marque S-Gn y Frankfort Po-Or.",
                "Eje Y menor que la referencia de Downs: dirección de crecimiento relativamente más horizontal en esta medida.",
                "Eje Y dentro de 59.4° ± 3.8° de la referencia clásica de Downs.",
                "Eje Y mayor que la referencia de Downs: dirección de crecimiento relativamente más vertical en esta medida.",
                true
        ));

        list.add(m(
                "Downs · Plano oclusal / FH",
                TWO_LINES,
                p("Oclusal 1", "Oclusal 2", "Po", "Or"),
                5.9,
                12.7,
                "9.3° ± 3.4° · referencia clásica de Downs",
                "Use los dos puntos del plano oclusal y Frankfort Po-Or.",
                "Inclinación oclusal menor respecto a Frankfort para la referencia de Downs.",
                "Plano oclusal dentro de 9.3° ± 3.4° de la referencia clásica de Downs.",
                "Inclinación oclusal mayor respecto a Frankfort para la referencia de Downs.",
                true
        ));

        list.add(m(
                "Downs · Incisivo inferior / plano oclusal",
                TWO_LINES,
                p("II borde", "II ápice", "Oclusal 1", "Oclusal 2"),
                51.3,
                60.3,
                "55.8° ± 4.5° · referencia clásica de Downs",
                "Marque el eje del incisivo inferior y los dos puntos del plano oclusal.",
                "Inclinación del incisivo inferior menor respecto al plano oclusal para esta referencia.",
                "Dentro de 55.8° ± 4.5° de la referencia clásica de Downs.",
                "Inclinación del incisivo inferior mayor respecto al plano oclusal para esta referencia.",
                true
        ));

        list.add(m(
                "Ricketts · Profundidad maxilar · FH / N-A",
                TWO_LINES,
                p("Po", "Or", "N", "A"),
                87.0,
                93.0,
                "90° ± 3° · referencia de Ricketts",
                "Marque Frankfort Po-Or y la línea N-A.",
                "Profundidad maxilar angular menor que la referencia adoptada; interprete junto con SNA y el patrón craneal.",
                "Dentro de 90° ± 3° de la referencia de Ricketts.",
                "Profundidad maxilar angular mayor que la referencia adoptada; interprete junto con SNA y el patrón craneal.",
                true
        ));

        list.add(m(
                "Ricketts · U1 / A-Pg · inclinación",
                TWO_LINES,
                p("IS borde", "IS ápice", "A", "Pg"),
                24.0,
                32.0,
                "28° ± 4° · referencia de Ricketts",
                "Marque el eje del incisivo superior y la línea A-Pg.",
                "Incisivo superior relativamente menos inclinado respecto a A-Pg para esta referencia.",
                "Dentro de 28° ± 4° de la referencia de Ricketts.",
                "Incisivo superior relativamente más inclinado respecto a A-Pg para esta referencia.",
                true
        ));

        list.add(m(
                "Ricketts · L1 / A-Pg · inclinación",
                TWO_LINES,
                p("II borde", "II ápice", "A", "Pg"),
                18.0,
                26.0,
                "22° ± 4° · referencia de Ricketts",
                "Marque el eje del incisivo inferior y la línea A-Pg.",
                "Incisivo inferior relativamente menos inclinado respecto a A-Pg para esta referencia.",
                "Dentro de 22° ± 4° de la referencia de Ricketts.",
                "Incisivo inferior relativamente más inclinado respecto a A-Pg para esta referencia.",
                true
        ));

        list.add(m(
                "Base craneal · N-S-Ba",
                THREE_POINTS,
                p("N", "S", "Ba"),
                127.0,
                135.0,
                "131° ± 4° · referencia cefalométrica clásica publicada",
                "Marque N, S y Ba; S es el vértice.",
                "Ángulo de base craneal menor que 127° para la referencia adoptada; describa la flexión craneal y correlacione con las relaciones sagitales.",
                "N-S-Ba dentro de 131° ± 4° de la referencia adoptada.",
                "Ángulo de base craneal mayor que 135° para la referencia adoptada; describa la flexión craneal y correlacione con las relaciones sagitales.",
                false
        ));

        list.add(m(
                "SN / plano palatino · ENA-ENP",
                TWO_LINES,
                p("S", "N", "ENA", "ENP"),
                5.5,
                11.5,
                "8.5° ± 3° · referencia publicada; existe variación poblacional",
                "Marque S-N y ENA-ENP/PNS.",
                "Plano palatino con menor inclinación respecto a SN para esta referencia.",
                "SN/plano palatino dentro de 8.5° ± 3° de la referencia publicada adoptada.",
                "Plano palatino con mayor inclinación respecto a SN para esta referencia.",
                true
        ));

        list.add(m(
                "Plano mandibular / plano oclusal · Go-Me / OP",
                TWO_LINES,
                p("Go", "Me", "Oclusal 1", "Oclusal 2"),
                12.4,
                22.4,
                "17.4° ± 5° · referencia publicada tipo Jarabak",
                "Marque Go-Me y los dos puntos del plano oclusal.",
                "Divergencia mandibular-oclusal menor para la referencia adoptada.",
                "Dentro de 17.4° ± 5° de la referencia publicada adoptada.",
                "Divergencia mandibular-oclusal mayor para la referencia adoptada.",
                true
        ));

'''
    m = m.replace(steiner_anchor, ceph_additions + steiner_anchor, 1)

vertebral_anchor = '''        return list;\n    }\n\n    /** Módulo: Perfil facial de tejidos blandos. */'''
if vertebral_anchor not in m:
    raise RuntimeError('Could not locate craniocervical catalog insertion point')

if 'Solow/Tallgren · OPT / CVT' not in m:
    cervical_additions = r'''        // Relaciones cráneo-cervicales de Solow/Tallgren y literatura posterior.
        // Se mantienen descriptivas porque los valores publicados dependen de la muestra,
        // postura natural de la cabeza, edad, sexo y protocolo de adquisición.
        list.add(m(
                "Solow/Tallgren · OPT / CVT · curvatura cervical",
                TWO_LINES,
                p("CV2tg", "CV2ip", "CV2tg", "CV4ip"),
                Double.NaN,
                Double.NaN,
                "Medida descriptiva OPT/CVT; no existe un umbral universal único",
                "OPT = CV2tg-CV2ip y CVT = CV2tg-CV4ip.",
                "",
                "Describe la angulación entre OPT y CVT. Informe el valor y compárelo solo con una referencia que use la misma postura y definición.",
                "",
                false
        ));

        list.add(m(
                "Solow/Tallgren · NL / OPT · ENA-ENP / OPT",
                TWO_LINES,
                p("ENA", "ENP", "CV2tg", "CV2ip"),
                Double.NaN,
                Double.NaN,
                "Medida descriptiva NL/OPT; valores de muestra publicados no son normalidad universal",
                "NL = ENA-ENP/PNS; OPT = CV2tg-CV2ip.",
                "",
                "Relaciona la inclinación maxilar/palatina con la columna cervical superior. Interpretar en posición natural de la cabeza.",
                "",
                true
        ));

        list.add(m(
                "Solow/Tallgren · NL / CVT · ENA-ENP / CVT",
                TWO_LINES,
                p("ENA", "ENP", "CV2tg", "CV4ip"),
                Double.NaN,
                Double.NaN,
                "Medida descriptiva NL/CVT; valores de muestra publicados no son normalidad universal",
                "NL = ENA-ENP/PNS; CVT = CV2tg-CV4ip.",
                "",
                "Relaciona el plano palatino con la tangente cervical CVT. Interpretar junto con SN/CVT, SN/OPT y la postura de adquisición.",
                "",
                true
        ));

        list.add(m(
                "Postura · FH / OPT",
                TWO_LINES,
                p("Po", "Or", "CV2tg", "CV2ip"),
                Double.NaN,
                Double.NaN,
                "Medida descriptiva FH/OPT; depende de postura/protocolo",
                "FH = Po-Or; OPT = CV2tg-CV2ip.",
                "",
                "Describe la relación de Frankfort con la tangente cervical superior OPT.",
                "",
                true
        ));

        list.add(m(
                "Postura · FH / CVT",
                TWO_LINES,
                p("Po", "Or", "CV2tg", "CV4ip"),
                Double.NaN,
                Double.NaN,
                "Medida descriptiva FH/CVT; depende de postura/protocolo",
                "FH = Po-Or; CVT = CV2tg-CV4ip.",
                "",
                "Describe la relación de Frankfort con la tangente cervical CVT.",
                "",
                true
        ));

'''
    m = m.replace(vertebral_anchor, cervical_additions + vertebral_anchor, 1)

catalog.write_text(m, encoding='utf-8')

# -----------------------------------------------------------------------------
# 2) CVM: provide skeletal-maturation stage and an age REFERENCE, not a false
#    exact bone age. Values come from the 2022 systematic review/meta-analysis
#    of Baccetti stages (41 studies, n=9867); sex and continent influence age.
# -----------------------------------------------------------------------------
logic = java_dir / 'RadiographicAssessmentLogic.java'
s = logic.read_text(encoding='utf-8')

if 'cvmAgeReference(' not in s:
    insert_before = '''    public static String nollaStageDescription(double stage) {'''
    if insert_before not in s:
        raise RuntimeError('Could not locate CVM logic insertion point')
    cvm_helpers = r'''    /**
     * Chronological-age reference associated with a Baccetti CVM stage.
     * This is NOT an exact skeletal/bone age. It is a pooled chronological-age
     * estimate from a systematic review/meta-analysis and is shown only to give
     * the student context for the selected maturation stage.
     *
     * sex: 0 = unspecified/combined, 1 = female, 2 = male.
     */
    public static String cvmAgeReference(String stage, int sex) {
        int index = cvmStageIndex(stage);
        if (index < 0) return "No se asigna edad de referencia a un patrón intermedio.";

        final double[] totalMean = {9.7, 10.8, 12.0, 13.4, 14.7, 15.8};
        final double[] totalLo   = {9.4, 10.5, 11.7, 13.2, 14.4, 15.3};
        final double[] totalHi   = {10.1, 11.1, 12.2, 13.6, 15.1, 16.3};

        final double[] femaleMean = {9.4, 10.4, 11.5, 13.1, 14.5, 15.6};
        final double[] femaleLo   = {9.0, 10.1, 11.3, 12.8, 14.2, 15.0};
        final double[] femaleHi   = {9.7, 10.7, 11.8, 13.4, 14.9, 16.2};

        final double[] maleMean = {10.2, 11.2, 12.6, 13.9, 15.3, 16.5};
        final double[] maleLo   = {9.8, 10.9, 12.2, 13.7, 14.9, 16.0};
        final double[] maleHi   = {10.6, 11.6, 12.9, 14.2, 15.7, 17.0};

        double mean;
        double lo;
        double hi;
        String group;
        if (sex == 1) {
            mean = femaleMean[index]; lo = femaleLo[index]; hi = femaleHi[index];
            group = "mujeres";
        } else if (sex == 2) {
            mean = maleMean[index]; lo = maleLo[index]; hi = maleHi[index];
            group = "varones";
        } else {
            mean = totalMean[index]; lo = totalLo[index]; hi = totalHi[index];
            group = "muestra combinada";
        }

        return String.format(
                Locale.US,
                "Edad cronológica de referencia asociada: %.1f años (IC95%% %.1f–%.1f; %s).",
                mean, lo, hi, group
        );
    }

    public static String cvmGrowthTiming(String stage) {
        if (stage == null) return "";
        switch (stage) {
            case "CS1": return "Pico de crecimiento: no se espera antes de aproximadamente 2 años.";
            case "CS2": return "Pico de crecimiento: suele comenzar aproximadamente 1 año después.";
            case "CS3": return "Pico de crecimiento: puede comenzar dentro del año alrededor de este estadio.";
            case "CS4": return "Pico de crecimiento: generalmente ocurrió aproximadamente 1–2 años antes.";
            case "CS5": return "Pico de crecimiento: generalmente terminó aproximadamente 1 año antes.";
            case "CS6": return "Pico de crecimiento: generalmente terminó al menos aproximadamente 2 años antes.";
            default: return "Pico de crecimiento: no estimable con una combinación vertebral intermedia/no concluyente.";
        }
    }

    private static int cvmStageIndex(String stage) {
        if ("CS1".equals(stage)) return 0;
        if ("CS2".equals(stage)) return 1;
        if ("CS3".equals(stage)) return 2;
        if ("CS4".equals(stage)) return 3;
        if ("CS5".equals(stage)) return 4;
        if ("CS6".equals(stage)) return 5;
        return -1;
    }

'''
    s = s.replace(insert_before, cvm_helpers + insert_before, 1)
logic.write_text(s, encoding='utf-8')

activity = java_dir / 'RadiographicAssessmentActivity.java'
a = activity.read_text(encoding='utf-8')

if 'private Spinner spCvmSex;' not in a:
    a = a.replace(
        '    private Spinner spC4Shape;\n',
        '    private Spinner spC4Shape;\n    private Spinner spCvmSex;\n',
        1
    )

cvm_intro = '''        addSmallText("Observe solamente C2, C3 y C4. Marque «presente» solo cuando la concavidad inferior sea clara.");'''
if 'Sexo para referencia etaria' not in a:
    if cvm_intro not in a:
        raise RuntimeError('Could not locate CVM UI intro')
    a = a.replace(
        cvm_intro,
        cvm_intro + '''\n        spCvmSex = addSpinnerRow("Sexo para referencia etaria", new String[]{"No especificado", "Femenino", "Masculino"});\n        addSmallText("El sexo solo ajusta la edad cronológica de referencia asociada al estadio. No modifica los criterios morfológicos CS1–CS6.");''',
        1
    )

old_result = '''        txtResult.setText(\n                result.stage + "\\n\\n" + result.summary +\n                "\\n\\nInterpretación: estimación de maduración esquelética; no equivale a edad cronológica y debe correlacionarse con el contexto clínico."\n        );'''
new_result = '''        int cvmSex = spCvmSex == null ? 0 : spCvmSex.getSelectedItemPosition();\n        String ageReference = RadiographicAssessmentLogic.cvmAgeReference(result.stage, cvmSex);\n        String growthTiming = RadiographicAssessmentLogic.cvmGrowthTiming(result.stage);\n        txtResult.setText(\n                "Maduración esquelética por CVM: " + result.stage +\n                "\\n\\n" + result.summary +\n                "\\n\\n" + growthTiming +\n                "\\n\\n" + ageReference +\n                "\\n\\nImportante: el estadio CVM es una estimación de maduración esquelética. La edad en años mostrada es una referencia cronológica poblacional asociada al estadio, NO una edad ósea exacta individual. Sexo, población y variación biológica modifican esos intervalos."\n        );'''
if old_result in a:
    a = a.replace(old_result, new_result, 1)
elif 'RadiographicAssessmentLogic.cvmAgeReference' not in a:
    raise RuntimeError('Could not locate CVM result block')

activity.write_text(a, encoding='utf-8')

# -----------------------------------------------------------------------------
# 3) Build-time tests/guardrails.
# -----------------------------------------------------------------------------
test_dir = Path('app/src/test/java/com/cefalo/angulos')
test_dir.mkdir(parents=True, exist_ok=True)
test_file = test_dir / 'ComplementaryCephCvmAgeTest.java'
test_file.write_text(r'''package com.cefalo.angulos;

import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

public class ComplementaryCephCvmAgeTest {
    @Test
    public void complementaryCephalometricAnglesArePresent() {
        String joined = MeasurementCatalog.steiner().toString();
        assertTrue(joined.contains("Downs · Ángulo facial"));
        assertTrue(joined.contains("Downs · Eje Y"));
        assertTrue(joined.contains("Ricketts · Profundidad maxilar"));
        assertTrue(joined.contains("Ricketts · U1 / A-Pg"));
        assertTrue(joined.contains("Base craneal · N-S-Ba"));
        assertTrue(joined.contains("SN / plano palatino"));
        assertTrue(joined.contains("Plano mandibular / plano oclusal"));
    }

    @Test
    public void craniocervicalAnglesArePresent() {
        String joined = MeasurementCatalog.vertebral().toString();
        assertTrue(joined.contains("OPT / CVT"));
        assertTrue(joined.contains("NL / OPT"));
        assertTrue(joined.contains("NL / CVT"));
    }

    @Test
    public void cvmAgeReferenceUsesSexSpecificMetaAnalysisValues() {
        assertTrue(RadiographicAssessmentLogic.cvmAgeReference("CS3", 1).contains("11.5"));
        assertTrue(RadiographicAssessmentLogic.cvmAgeReference("CS3", 2).contains("12.6"));
        assertTrue(RadiographicAssessmentLogic.cvmAgeReference("CS6", 0).contains("15.8"));
        assertTrue(RadiographicAssessmentLogic.cvmAgeReference("Patrón intermedio", 0).contains("No se asigna"));
    }

    @Test
    public void cvmGrowthTimingMatchesBaccettiFramework() {
        assertTrue(RadiographicAssessmentLogic.cvmGrowthTiming("CS1").contains("2 años"));
        assertTrue(RadiographicAssessmentLogic.cvmGrowthTiming("CS4").contains("1–2 años"));
        assertTrue(RadiographicAssessmentLogic.cvmGrowthTiming("CS6").contains("al menos"));
    }
}
''', encoding='utf-8')

# Version follows the embedded Nolla-reference pass (1.30 / code 31).
gradle = Path('app/build.gradle')
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+31\b', 'versionCode 32', g, count=1)
g = re.sub(r"versionName\s+'1\.30'", "versionName '1.31'", g, count=1)
gradle.write_text(g, encoding='utf-8')

checks = {
    'Downs facial angle': 'Downs · Ángulo facial · FH / N-Pg' in catalog.read_text(encoding='utf-8'),
    'Ricketts maxillary depth': 'Ricketts · Profundidad maxilar · FH / N-A' in catalog.read_text(encoding='utf-8'),
    'cervical OPT/CVT': 'Solow/Tallgren · OPT / CVT' in catalog.read_text(encoding='utf-8'),
    'CVM age reference': 'cvmAgeReference' in logic.read_text(encoding='utf-8'),
    'CVM sex selector': 'Sexo para referencia etaria' in activity.read_text(encoding='utf-8'),
    'version 1.31': "versionName '1.31'" in gradle.read_text(encoding='utf-8'),
}
missing = [name for name, ok in checks.items() if not ok]
if missing:
    raise RuntimeError('Complementary cephalometric/CVM pass incomplete: ' + ', '.join(missing))

print('Complementary Downs/Ricketts/craniocervical angles and CVM age-reference context applied; build version set to 1.31.')
