package com.cefalo.angulos;

import java.util.ArrayList;
import java.util.List;

import static com.cefalo.angulos.LinearMeasurementDefinition.Interpretation.CERVICAL_DEPTH;
import static com.cefalo.angulos.LinearMeasurementDefinition.Interpretation.HYOID_TRIANGLE;
import static com.cefalo.angulos.LinearMeasurementDefinition.Interpretation.RANGE;
import static com.cefalo.angulos.LinearMeasurementDefinition.Type.DISTANCE;
import static com.cefalo.angulos.LinearMeasurementDefinition.Type.SIGNED_PERPENDICULAR;

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
