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

public final class LinearMeasurementCatalog {

    private LinearMeasurementCatalog() {}

    public static List<LinearMeasurementDefinition> rocabado() {
        List<LinearMeasurementDefinition> list = new ArrayList<>();

        list.add(m(
                "Distancia C0-C1",
                DISTANCE,
                RANGE,
                p("Occipital", "C1 posterior"),
                4.0,
                9.0,
                "4–9 mm",
                "Distancia suboccipital menor de 4 mm según la referencia de Rocabado; correlacionar clínicamente.",
                "Dentro del intervalo funcional de referencia C0-C1.",
                "Distancia suboccipital mayor de 9 mm según la referencia de Rocabado; correlacionar clínicamente."
        ));

        list.add(m(
                "C3-RGn",
                DISTANCE,
                RANGE,
                p("C3", "RGn"),
                60.6,
                73.8,
                "67.2 ± 6.6 mm · Bibby/Preston",
                "Por debajo de ±1 DE de la muestra de referencia histórica del triángulo hioideo; no constituye diagnóstico.",
                "Dentro de ±1 DE de la muestra de referencia histórica del triángulo hioideo.",
                "Por encima de ±1 DE de la muestra de referencia histórica del triángulo hioideo; no constituye diagnóstico."
        ));

        list.add(m(
                "C3-H",
                DISTANCE,
                RANGE,
                p("C3", "H"),
                28.86,
                34.66,
                "31.76 ± 2.9 mm · Bibby/Preston",
                "Por debajo de ±1 DE de la muestra de referencia histórica; interpretar con edad, postura y patrón esqueletal.",
                "Dentro de ±1 DE de la muestra de referencia histórica.",
                "Por encima de ±1 DE de la muestra de referencia histórica; interpretar con edad, postura y patrón esqueletal."
        ));

        list.add(m(
                "H-RGn",
                DISTANCE,
                RANGE,
                p("H", "RGn"),
                31.00,
                42.66,
                "36.83 ± 5.83 mm · Bibby/Preston",
                "Por debajo de ±1 DE de la muestra de referencia histórica; no constituye diagnóstico.",
                "Dentro de ±1 DE de la muestra de referencia histórica.",
                "Por encima de ±1 DE de la muestra de referencia histórica; no constituye diagnóstico."
        ));

        list.add(m(
                "Posición vertical H respecto a RGn-C3",
                SIGNED_PERPENDICULAR,
                HYOID_TRIANGLE,
                p("C3", "RGn", "H"),
                Double.NaN,
                Double.NaN,
                "Positivo: H debajo de C3-RGn",
                "",
                "",
                ""
        ));

        list.add(m(
                "Profundidad de la columna cervical",
                SIGNED_PERPENDICULAR,
                CERVICAL_DEPTH,
                p("C2 post-sup.", "C7 post-inf.", "Profundidad cervical"),
                8.0,
                12.0,
                "8–12 mm · referencia Penning/Rocabado",
                "",
                "",
                ""
        ));

        list.add(m(
                "Dimensión AP ósea de nasofaringe (AA-ENP)",
                DISTANCE,
                RANGE,
                p("AA", "ENP"),
                29.25,
                36.57,
                "32.91 ± 3.66 mm · Bibby/Preston",
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

    public static List<LinearMeasurementDefinition> airway() {
        List<LinearMeasurementDefinition> list = new ArrayList<>();

        list.add(m("AD1 · ENP-AD1", DISTANCE, RANGE,
                p("ENP", "AD1"), Double.NaN, Double.NaN,
                "Referencia docente aportada para 6 y 16 años", "",
                "Se muestra como referencia tabular; no usar como diagnóstico de obstrucción/adenoides.", ""));

        list.add(m("AD2 · ENP-AD2", DISTANCE, RANGE,
                p("ENP", "AD2"), Double.NaN, Double.NaN,
                "Referencia docente aportada para 6 y 16 años", "",
                "Se muestra como referencia tabular; no usar como diagnóstico de obstrucción/adenoides.", ""));

        list.add(m("AD3 · Uptp-Adenoides", DISTANCE, RANGE,
                p("Uptp", "Adenoides"), Double.NaN, Double.NaN,
                "Tabla aportada: 6 a 7.02±3.70 · 16 a 14.56±4.70 mm", "",
                "Se muestra como referencia tabular; no usar como diagnóstico respiratorio.", ""));

        list.add(m("Faringe superior", DISTANCE, RANGE,
                p("Faringe sup ant.", "Faringe sup post."), Double.NaN, Double.NaN,
                "McNamara: H 17.4±4.3 · M 17.4±3.4 mm", "",
                "Comparar con referencia de McNamara; una cefalometría 2D no diagnostica obstrucción.", ""));

        list.add(m("Faringe posterior o inferior", DISTANCE, RANGE,
                p("Faringe inf ant.", "Faringe inf post."), Double.NaN, Double.NaN,
                "McNamara: H 13.5±4.3 · M 11.3±3.3 mm", "",
                "Comparar con referencia de McNamara; una cefalometría 2D no diagnostica apnea ni hipertrofia amigdalina.", ""));

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
