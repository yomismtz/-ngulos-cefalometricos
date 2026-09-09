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
                "4-9 mm",
                "Por debajo del intervalo de referencia.",
                "Dentro del intervalo de referencia C0-C1.",
                "Por encima del intervalo de referencia."
        ));

        list.add(m(
                "C3-RGn",
                DISTANCE,
                RANGE,
                p("C3", "RGn"),
                60.6,
                73.8,
                "67.20 mm ± 6.6 mm",
                "Por debajo del promedio de referencia del triángulo hioideo.",
                "Dentro de ±1 DE del promedio de referencia.",
                "Por encima del promedio de referencia del triángulo hioideo."
        ));

        list.add(m(
                "C3-H",
                DISTANCE,
                RANGE,
                p("C3", "H"),
                28.86,
                34.66,
                "31.76 mm ± 2.9 mm",
                "Por debajo del promedio de referencia del triángulo hioideo.",
                "Dentro de ±1 DE del promedio de referencia.",
                "Por encima del promedio de referencia del triángulo hioideo."
        ));

        list.add(m(
                "H-RGn",
                DISTANCE,
                RANGE,
                p("H", "RGn"),
                31.03,
                42.63,
                "36.83 mm ± 5.8 mm",
                "Por debajo del promedio de referencia del triángulo hioideo.",
                "Dentro de ±1 DE del promedio de referencia.",
                "Por encima del promedio de referencia del triángulo hioideo."
        ));

        list.add(m(
                "Posición vertical H respecto a RGn-C3",
                SIGNED_PERPENDICULAR,
                HYOID_TRIANGLE,
                p("C3", "RGn", "H"),
                Double.NaN,
                Double.NaN,
                "Positivo: H debajo de RGn-C3",
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
                "10 ± 2 mm",
                "",
                "",
                ""
        ));

        list.add(m(
                "Dimensión AP de la nasofaringe (AA-PNS/ENP)",
                DISTANCE,
                RANGE,
                p("AA", "ENP"),
                29.2,
                36.6,
                "32.9 mm ± 3.7 mm",
                "Por debajo del intervalo de referencia.",
                "Dentro del intervalo de referencia.",
                "Por encima del intervalo de referencia."
        ));

        return list;
    }


    public static List<LinearMeasurementDefinition> levandoski() {
        List<LinearMeasurementDefinition> list = new ArrayList<>();

        list.add(m("Desviación línea media mandibular", PERPENDICULAR_ABS, COMPARATIVE,
                p("LM sup.", "LM inf.", "LM mandibular"), Double.NaN, Double.NaN,
                "Comparación con línea media maxilar", "", "Comparativa; sin norma estándar", ""));

        list.add(m("Cóndilo a incisivo central maxilar derecho", DISTANCE, COMPARATIVE,
                p("Cd der.", "IC max der."), Double.NaN, Double.NaN,
                "Comparar D/I", "", "Comparar con lado izquierdo", ""));
        list.add(m("Cóndilo a incisivo central maxilar izquierdo", DISTANCE, COMPARATIVE,
                p("Cd izq.", "IC max izq."), Double.NaN, Double.NaN,
                "Comparar D/I", "", "Comparar con lado derecho", ""));

        list.add(m("Cóndilo a incisivo central mandibular derecho", DISTANCE, COMPARATIVE,
                p("Cd der.", "IC mand der."), Double.NaN, Double.NaN,
                "Comparar D/I", "", "Comparar con lado izquierdo", ""));
        list.add(m("Cóndilo a incisivo central mandibular izquierdo", DISTANCE, COMPARATIVE,
                p("Cd izq.", "IC mand izq."), Double.NaN, Double.NaN,
                "Comparar D/I", "", "Comparar con lado derecho", ""));

        list.add(m("Cóndilo-Gonion derecho", DISTANCE, COMPARATIVE,
                p("Cd der.", "Go der."), Double.NaN, Double.NaN,
                "Comparar D/I", "", "Altura condilar/ramal comparativa", ""));
        list.add(m("Cóndilo-Gonion izquierdo", DISTANCE, COMPARATIVE,
                p("Cd izq.", "Go izq."), Double.NaN, Double.NaN,
                "Comparar D/I", "", "Altura condilar/ramal comparativa", ""));

        list.add(m("Gonion-Coronoides derecho", DISTANCE, COMPARATIVE,
                p("Go der.", "Kr der."), Double.NaN, Double.NaN,
                "Comparar D/I", "", "Altura coronoidea comparativa", ""));
        list.add(m("Gonion-Coronoides izquierdo", DISTANCE, COMPARATIVE,
                p("Go izq.", "Kr izq."), Double.NaN, Double.NaN,
                "Comparar D/I", "", "Altura coronoidea comparativa", ""));

        list.add(m("Línea media a cóndilo derecho", PERPENDICULAR_ABS, COMPARATIVE,
                p("LM sup.", "LM inf.", "Cd der."), Double.NaN, Double.NaN,
                "Comparar D/I", "", "Comparar con lado izquierdo", ""));
        list.add(m("Línea media a cóndilo izquierdo", PERPENDICULAR_ABS, COMPARATIVE,
                p("LM sup.", "LM inf.", "Cd izq."), Double.NaN, Double.NaN,
                "Comparar D/I", "", "Comparar con lado derecho", ""));

        list.add(m("Línea media a cuerpo mandibular derecho", PERPENDICULAR_ABS, COMPARATIVE,
                p("LM sup.", "LM inf.", "Cuerpo Md der."), Double.NaN, Double.NaN,
                "Comparar D/I", "", "Comparar con lado izquierdo", ""));
        list.add(m("Línea media a cuerpo mandibular izquierdo", PERPENDICULAR_ABS, COMPARATIVE,
                p("LM sup.", "LM inf.", "Cuerpo Md izq."), Double.NaN, Double.NaN,
                "Comparar D/I", "", "Comparar con lado derecho", ""));

        list.add(m("Distal 2º molar derecho a línea media", PERPENDICULAR_ABS, COMPARATIVE,
                p("LM sup.", "LM inf.", "M2 distal der."), Double.NaN, Double.NaN,
                "Comparar D/I", "", "Comparar con lado izquierdo", ""));
        list.add(m("Distal 2º molar izquierdo a línea media", PERPENDICULAR_ABS, COMPARATIVE,
                p("LM sup.", "LM inf.", "M2 distal izq."), Double.NaN, Double.NaN,
                "Comparar D/I", "", "Comparar con lado derecho", ""));

        list.add(m("Ancho de rama mandibular derecha", DISTANCE, COMPARATIVE,
                p("Rama ant der.", "Rama post der."), Double.NaN, Double.NaN,
                "Comparar D/I", "", "Comparar con lado izquierdo", ""));
        list.add(m("Ancho de rama mandibular izquierda", DISTANCE, COMPARATIVE,
                p("Rama ant izq.", "Rama post izq."), Double.NaN, Double.NaN,
                "Comparar D/I", "", "Comparar con lado derecho", ""));

        return list;
    }

    public static List<LinearMeasurementDefinition> airway() {
        List<LinearMeasurementDefinition> list = new ArrayList<>();

        list.add(m("AD1 · ENP-AD1", DISTANCE, RANGE,
                p("ENP", "AD1"), Double.NaN, Double.NaN,
                "Según edad y sexo", "", "Referencia dependiente de edad/sexo", ""));
        list.add(m("AD2 · ENP-AD2", DISTANCE, RANGE,
                p("ENP", "AD2"), Double.NaN, Double.NaN,
                "Según edad y sexo", "", "Referencia dependiente de edad/sexo", ""));
        list.add(m("AD3 · Uptp-Adenoides", DISTANCE, RANGE,
                p("Uptp", "Adenoides"), Double.NaN, Double.NaN,
                "6 años: 7.02±3.7 · 16 años: 14.56±4.70", "", "Referencia dependiente de edad", ""));
        list.add(m("Faringe superior", DISTANCE, RANGE,
                p("Faringe sup ant.", "Faringe sup post."), Double.NaN, Double.NaN,
                "F: 17.4±3.4 · M: 17.4±4.3", "", "Referencia dependiente de sexo", ""));
        list.add(m("Faringe posterior o inferior", DISTANCE, RANGE,
                p("Faringe inf ant.", "Faringe inf post."), Double.NaN, Double.NaN,
                "F: 11.3±3.3 · M: 13.5±4.3", "", "Referencia dependiente de sexo", ""));

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
