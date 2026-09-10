package com.cefalo.angulos;

import java.util.ArrayList;
import java.util.List;

import static com.cefalo.angulos.LinearMeasurementDefinition.Interpretation.CERVICAL_DEPTH;
import static com.cefalo.angulos.LinearMeasurementDefinition.Interpretation.HYOID_TRIANGLE;
import static com.cefalo.angulos.LinearMeasurementDefinition.Interpretation.RANGE;
import static com.cefalo.angulos.LinearMeasurementDefinition.Interpretation.COMPARATIVE;
import static com.cefalo.angulos.LinearMeasurementDefinition.Type.DISTANCE;
import static com.cefalo.angulos.LinearMeasurementDefinition.Type.SIGNED_PERPENDICULAR;
import static com.cefalo.angulos.LinearMeasurementDefinition.Type.PERPENDICULAR_ABS;
import static com.cefalo.angulos.LinearMeasurementDefinition.Type.AXIAL_PROJECTION;

public final class LinearMeasurementCatalog {

    private LinearMeasurementCatalog() {}

    /**
     * Medidas lineales del módulo cefalométrico lateral.
     * SL y SE son proyecciones construidas sobre SN: el usuario marca el punto anatómico
     * y el software obtiene L/E de forma geométrica, sin pedir puntos construidos extra.
     */
    public static List<LinearMeasurementDefinition> cephalometric() {
        List<LinearMeasurementDefinition> list = new ArrayList<>();

        list.add(m(
                "Segmento SL",
                AXIAL_PROJECTION,
                RANGE,
                p("S", "N", "Pg"),
                47.0,
                55.0,
                "51 ± 4 mm · referencia cefalométrica clásica",
                "SL menor que el intervalo de referencia: el pogonion proyectado sobre SN queda relativamente más próximo a S. Interpretar junto con las relaciones sagitales.",
                "SL dentro de 51 ± 4 mm de la referencia adoptada.",
                "SL mayor que el intervalo de referencia: el pogonion proyectado sobre SN queda relativamente más alejado de S. Interpretar junto con las relaciones sagitales."
        ));

        list.add(m(
                "Segmento SE",
                AXIAL_PROJECTION,
                RANGE,
                p("S", "N", "Cóndilo posterior"),
                19.0,
                25.0,
                "22 ± 3 mm · referencia cefalométrica clásica",
                "SE menor que el intervalo de referencia: la proyección del contorno condilar posterior sobre SN queda relativamente más próxima a S.",
                "SE dentro de 22 ± 3 mm de la referencia adoptada.",
                "SE mayor que el intervalo de referencia: la proyección del contorno condilar posterior sobre SN queda relativamente más alejada de S."
        ));

        list.add(m(
                "Incisivo superior a NA · lineal",
                PERPENDICULAR_ABS,
                RANGE,
                p("N", "A", "IS borde"),
                Double.NaN,
                Double.NaN,
                "4 mm · valor clásico; sin tolerancia automática adoptada",
                "",
                "Distancia perpendicular del borde incisal superior a la línea NA. El valor clásico de referencia es 4 mm; interpretar con edad, población y el resto del análisis.",
                ""
        ));

        list.add(m(
                "Incisivo inferior a NB · lineal",
                PERPENDICULAR_ABS,
                RANGE,
                p("N", "B", "II borde"),
                Double.NaN,
                Double.NaN,
                "4 mm · valor clásico; sin tolerancia automática adoptada",
                "",
                "Distancia perpendicular del borde incisal inferior a la línea NB. El valor clásico de referencia es 4 mm; interpretar con edad, población y el resto del análisis.",
                ""
        ));

        return list;
    }

    /**
     * Módulo temático de postura cráneo-cervical e hioides.
     * Conserva referencias históricas solo cuando la geometría está claramente definida.
     */
    public static List<LinearMeasurementDefinition> rocabado() {
        List<LinearMeasurementDefinition> list = new ArrayList<>();

        list.add(m(
                "Espacio C0-C1",
                PERPENDICULAR_ABS,
                RANGE,
                p("ENP", "Occipital", "C1 sup. posterior"),
                4.0,
                9.0,
                "4–9 mm · distancia perpendicular desde el plano de McGregor al arco posterior del atlas",
                "C0-C1 <4 mm: espacio suboccipital disminuido respecto al intervalo de referencia; correlacionar con el ángulo cráneo-odontoideo y la posición de la cabeza.",
                "C0-C1 dentro del intervalo funcional de referencia de 4–9 mm.",
                "C0-C1 >9 mm: espacio suboccipital aumentado respecto al intervalo de referencia; correlacionar con el ángulo cráneo-odontoideo y la posición de la cabeza."
        ));

        list.add(m(
                "Espacio C1-C2",
                DISTANCE,
                RANGE,
                p("C1 inf. posterior", "C2 espinosa sup. posterior"),
                4.0,
                9.0,
                "4–9 mm · arco posterior del atlas a apófisis espinosa de C2",
                "C1-C2 <4 mm: segundo espacio suboccipital disminuido respecto al intervalo de referencia.",
                "C1-C2 dentro del intervalo funcional de referencia de 4–9 mm.",
                "C1-C2 >9 mm: segundo espacio suboccipital aumentado respecto al intervalo de referencia."
        ));

        list.add(m(
                "C3-RGn",
                DISTANCE,
                RANGE,
                p("C3", "RGn"),
                60.6,
                73.8,
                "67.2 ± 6.6 mm · referencia histórica Bibby/Preston",
                "Por debajo de ±1 DE de la muestra histórica. No constituye un diagnóstico aislado.",
                "Dentro de ±1 DE de la muestra histórica de referencia.",
                "Por encima de ±1 DE de la muestra histórica. No constituye un diagnóstico aislado."
        ));

        list.add(m(
                "C3-H",
                DISTANCE,
                RANGE,
                p("C3", "H"),
                28.86,
                34.66,
                "31.76 ± 2.9 mm · referencia histórica Bibby/Preston",
                "Por debajo de ±1 DE de la muestra histórica; interpretar con edad, postura y patrón esqueletal.",
                "Dentro de ±1 DE de la muestra histórica.",
                "Por encima de ±1 DE de la muestra histórica; interpretar con edad, postura y patrón esqueletal."
        ));

        list.add(m(
                "H-RGn",
                DISTANCE,
                RANGE,
                p("H", "RGn"),
                31.00,
                42.66,
                "36.83 ± 5.83 mm · referencia histórica Bibby/Preston",
                "Por debajo de ±1 DE de la muestra histórica; no constituye diagnóstico.",
                "Dentro de ±1 DE de la muestra histórica.",
                "Por encima de ±1 DE de la muestra histórica; no constituye diagnóstico."
        ));

        list.add(m(
                "Altura / posición del hioides respecto a C3-RGn",
                SIGNED_PERPENDICULAR,
                HYOID_TRIANGLE,
                p("C3", "RGn", "H"),
                Double.NaN,
                Double.NaN,
                "Triángulo C3-RGn-H · se informa signo y magnitud; referencias históricas describen H por debajo de C3-RGn",
                "",
                "",
                ""
        ));

        list.add(m(
                "Profundidad de la columna cervical · Penning",
                SIGNED_PERPENDICULAR,
                CERVICAL_DEPTH,
                p("C2 post-sup.", "C7 post-inf.", "Profundidad cervical"),
                8.0,
                12.0,
                "10 ± 2 mm · rectificada <8 · cifótica si negativa · lordosis aumentada >12",
                "",
                "",
                ""
        ));

        list.add(m(
                "Dimensión AP ósea de nasofaringe (AA-ENP) · complementaria",
                DISTANCE,
                RANGE,
                p("AA", "ENP"),
                29.25,
                36.57,
                "32.91 ± 3.66 mm · referencia histórica Bibby/Preston",
                "Por debajo de ±1 DE de la muestra histórica. Esta distancia ósea no diagnostica obstrucción de vía aérea.",
                "Dentro de ±1 DE de la muestra histórica. No descarta trastorno respiratorio.",
                "Por encima de ±1 DE de la muestra histórica. Esta distancia ósea no diagnostica normalidad respiratoria."
        ));

        return list;
    }

    public static List<LinearMeasurementDefinition> levandoski() {
        List<LinearMeasurementDefinition> list = new ArrayList<>();

        list.add(m("Cóndilo a incisivo central maxilar derecho", DISTANCE, COMPARATIVE,
                p("Cd der.", "IC max der."), Double.NaN, Double.NaN,
                "Comparación D/I", "", "Comparar con lado izquierdo; la panorámica presenta magnificación y distorsión.", ""));
        list.add(m("Cóndilo a incisivo central maxilar izquierdo", DISTANCE, COMPARATIVE,
                p("Cd izq.", "IC max izq."), Double.NaN, Double.NaN,
                "Comparación D/I", "", "Comparar con lado derecho; la panorámica presenta magnificación y distorsión.", ""));

        list.add(m("Cóndilo a incisivo central mandibular derecho", DISTANCE, COMPARATIVE,
                p("Cd der.", "IC mand der."), Double.NaN, Double.NaN,
                "Comparación D/I", "", "Comparar con lado izquierdo; usar como tamizaje de asimetría.", ""));
        list.add(m("Cóndilo a incisivo central mandibular izquierdo", DISTANCE, COMPARATIVE,
                p("Cd izq.", "IC mand izq."), Double.NaN, Double.NaN,
                "Comparación D/I", "", "Comparar con lado derecho; usar como tamizaje de asimetría.", ""));

        list.add(m("Cóndilo-Gonion derecho", DISTANCE, COMPARATIVE,
                p("Cd der.", "Go der."), Double.NaN, Double.NaN,
                "Comparación D/I", "", "Comparar con lado izquierdo; no diagnostica asimetría por sí sola.", ""));
        list.add(m("Cóndilo-Gonion izquierdo", DISTANCE, COMPARATIVE,
                p("Cd izq.", "Go izq."), Double.NaN, Double.NaN,
                "Comparación D/I", "", "Comparar con lado derecho; no diagnostica asimetría por sí sola.", ""));

        list.add(m("Gonion-Coronoides derecho", DISTANCE, COMPARATIVE,
                p("Go der.", "Kr der."), Double.NaN, Double.NaN,
                "Comparación D/I", "", "Comparar con lado izquierdo; no diagnostica hiperplasia coronoidea por sí sola.", ""));
        list.add(m("Gonion-Coronoides izquierdo", DISTANCE, COMPARATIVE,
                p("Go izq.", "Kr izq."), Double.NaN, Double.NaN,
                "Comparación D/I", "", "Comparar con lado derecho; no diagnostica hiperplasia coronoidea por sí sola.", ""));

        list.add(m("Línea media a cóndilo derecho", PERPENDICULAR_ABS, COMPARATIVE,
                p("LM sup.", "LM inf.", "Cd der."), Double.NaN, Double.NaN,
                "Comparación D/I", "", "Comparar con lado izquierdo; interpretar con cautela por distorsión panorámica.", ""));
        list.add(m("Línea media a cóndilo izquierdo", PERPENDICULAR_ABS, COMPARATIVE,
                p("LM sup.", "LM inf.", "Cd izq."), Double.NaN, Double.NaN,
                "Comparación D/I", "", "Comparar con lado derecho; interpretar con cautela por distorsión panorámica.", ""));

        list.add(m("Línea media a cuerpo mandibular derecho", PERPENDICULAR_ABS, COMPARATIVE,
                p("LM sup.", "LM inf.", "Cuerpo Md der."), Double.NaN, Double.NaN,
                "Comparación D/I", "", "Comparar con lado izquierdo; usar como orientación, no como diagnóstico definitivo.", ""));
        list.add(m("Línea media a cuerpo mandibular izquierdo", PERPENDICULAR_ABS, COMPARATIVE,
                p("LM sup.", "LM inf.", "Cuerpo Md izq."), Double.NaN, Double.NaN,
                "Comparación D/I", "", "Comparar con lado derecho; usar como orientación, no como diagnóstico definitivo.", ""));

        list.add(m("Distal 2º molar derecho a línea media", PERPENDICULAR_ABS, COMPARATIVE,
                p("LM sup.", "LM inf.", "M2 distal der."), Double.NaN, Double.NaN,
                "Comparación D/I", "", "Comparar con lado izquierdo.", ""));
        list.add(m("Distal 2º molar izquierdo a línea media", PERPENDICULAR_ABS, COMPARATIVE,
                p("LM sup.", "LM inf.", "M2 distal izq."), Double.NaN, Double.NaN,
                "Comparación D/I", "", "Comparar con lado derecho.", ""));

        list.add(m("Ancho de rama mandibular derecha", DISTANCE, COMPARATIVE,
                p("Rama ant der.", "Rama post der."), Double.NaN, Double.NaN,
                "Comparación D/I", "", "Comparar con lado izquierdo; la medición panorámica puede distorsionarse.", ""));
        list.add(m("Ancho de rama mandibular izquierda", DISTANCE, COMPARATIVE,
                p("Rama ant izq.", "Rama post izq."), Double.NaN, Double.NaN,
                "Comparación D/I", "", "Comparar con lado derecho; la medición panorámica puede distorsionarse.", ""));

        return list;
    }

    /**
     * Vía aérea superior. Las dimensiones 2D se presentan como evaluación cefalométrica,
     * no como diagnóstico de obstrucción, hipertrofia adenoidea o apnea del sueño.
     */
    public static List<LinearMeasurementDefinition> airway() {
        List<LinearMeasurementDefinition> list = new ArrayList<>();

        list.add(m("AD1 · ENP-AD1", DISTANCE, RANGE,
                p("ENP", "AD1"), Double.NaN, Double.NaN,
                "Construcción: ENP/PNS-Ba hasta el contorno adenoideo/pared faríngea posterior · referencia dependiente de edad y población", "",
                "Medida anatómica reproducible. No se aplica un umbral automático único para hipertrofia u obstrucción.", ""));

        list.add(m("AD2 · ENP-AD2", DISTANCE, RANGE,
                p("ENP", "AD2"), Double.NaN, Double.NaN,
                "Construcción: desde ENP/PNS sobre una perpendicular a S-Ba hasta el contorno adenoideo/pared faríngea posterior", "",
                "Medida anatómica reproducible. No se aplica un umbral automático único; interpretar según edad y protocolo de referencia.", ""));

        list.add(m("AD3 · tu-ad3", DISTANCE, RANGE,
                p("tu", "AD3"), Double.NaN, Double.NaN,
                "Solow et al.: distancia desde tu a la adenoides/pared faríngea dorsal más cercana · sin umbral diagnóstico automático", "",
                "AD3 se informa como diámetro cefalométrico descriptivo. La nomenclatura y los valores dependen del protocolo; no diagnostica por sí sola hipertrofia adenoidea ni obstrucción.", ""));

        list.add(m("Faringe superior", DISTANCE, RANGE,
                p("Faringe sup ant.", "Faringe sup post."), Double.NaN, Double.NaN,
                "Referencia cefalométrica de McNamara; interpretar con edad y protocolo", "",
                "Comparar con la referencia apropiada. Una telerradiografía lateral 2D no diagnostica obstrucción ni apnea del sueño.", ""));

        list.add(m("Faringe posterior o inferior", DISTANCE, RANGE,
                p("Faringe inf ant.", "Faringe inf post."), Double.NaN, Double.NaN,
                "Referencia cefalométrica de McNamara; interpretar con edad y protocolo", "",
                "Comparar con la referencia apropiada. Una telerradiografía lateral 2D no diagnostica apnea ni hipertrofia amigdalina.", ""));

        list.add(m("MP-H · hioides a plano mandibular", PERPENDICULAR_ABS, RANGE,
                p("Go", "Me", "H"), 12.4, 18.4,
                "15.4 ± 3 mm · referencia cefalométrica clásica de vía aérea", 
                "MP-H por debajo del intervalo de referencia adoptado; describe una posición relativamente más próxima del hioides al plano mandibular.",
                "MP-H dentro del intervalo 15.4 ± 3 mm de la referencia adoptada.",
                "MP-H por encima del intervalo de referencia adoptado; describe un hioides relativamente más alejado/inferior respecto al plano mandibular. No diagnostica apnea por sí solo."
        ));

        list.add(m("PNS-P · longitud del paladar blando", DISTANCE, RANGE,
                p("ENP", "P"), 34.0, 40.0,
                "37 ± 3 mm · referencia cefalométrica clásica de vía aérea",
                "Longitud PNS-P por debajo del intervalo de referencia adoptado; describir sin inferir función velofaríngea de forma aislada.",
                "PNS-P dentro del intervalo 37 ± 3 mm de la referencia adoptada.",
                "Longitud PNS-P por encima del intervalo de referencia adoptado; el paladar blando es relativamente largo para esta referencia, sin constituir diagnóstico por sí solo."
        ));

        return list;
    }

    private static LinearMeasurementDefinition m(
            String name,
            LinearMeasurementDefinition.Type type,
            LinearMeasurementDefinition.Interpretation interpretation,
            String[] labels,
            double min,
            double max,
            String norm,
            String low,
            String normal,
            String high
    ) {
        return new LinearMeasurementDefinition(
                name,
                type,
                interpretation,
                labels,
                min,
                max,
                norm,
                low,
                normal,
                high
        );
    }

    private static String[] p(String... values) {
        return values;
    }
}
