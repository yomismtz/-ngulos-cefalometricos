package com.cefalo.angulos;

public class LinearMeasurementDefinition {

    public enum Type {
        DISTANCE,
        SIGNED_PERPENDICULAR,
        PERPENDICULAR_ABS,
        AXIAL_PROJECTION
    }

    public enum Interpretation {
        RANGE,
        HYOID_TRIANGLE,
        CERVICAL_DEPTH,
        COMPARATIVE
    }

    public final String name;
    public final Type type;
    public final Interpretation interpretation;
    public final String[] pointLabels;
    public final double normalMin;
    public final double normalMax;
    public final String normText;
    public final String lowDiagnosis;
    public final String normalDiagnosis;
    public final String highDiagnosis;

    public LinearMeasurementDefinition(
            String name,
            Type type,
            Interpretation interpretation,
            String[] pointLabels,
            double normalMin,
            double normalMax,
            String normText,
            String lowDiagnosis,
            String normalDiagnosis,
            String highDiagnosis
    ) {
        this.name = name;
        this.type = type;
        this.interpretation = interpretation;
        this.pointLabels = pointLabels;
        this.normalMin = normalMin;
        this.normalMax = normalMax;
        this.normText = normText;
        this.lowDiagnosis = lowDiagnosis;
        this.normalDiagnosis = normalDiagnosis;
        this.highDiagnosis = highDiagnosis;
    }

    public String diagnosis(double valueMm) {
        if (interpretation == Interpretation.HYOID_TRIANGLE) {
            if (valueMm > 0.01) {
                return "H está por debajo de la línea C3-RGn (triángulo hioideo positivo). Es una descripción cefalométrica; la magnitud debe interpretarse con la referencia utilizada y no diagnostica por sí sola una alteración respiratoria o postural.";
            }

            if (valueMm < -0.01) {
                return "H está por encima de la línea C3-RGn (triángulo hioideo negativo/invertido). Es una descripción cefalométrica y requiere correlación clínica.";
            }

            return "H se encuentra prácticamente sobre la línea C3-RGn (triángulo lineal). Interpretar junto con el resto del trazado.";
        }

        if (interpretation == Interpretation.COMPARATIVE) {
            return normalDiagnosis;
        }

        if (interpretation == Interpretation.CERVICAL_DEPTH) {
            if (valueMm < 0.0) {
                return "Profundidad negativa: curvatura cervical cifótica/invertida según el método de Penning; correlacionar clínicamente.";
            }

            if (valueMm < 8.0) {
                return "Profundidad de 0 a <8 mm: rectificación de la curvatura cervical según el método de Penning.";
            }

            if (valueMm <= 12.0) {
                return "Profundidad de 8 a 12 mm: intervalo fisiológico de referencia del método de Penning (10 ± 2 mm).";
            }

            return "Profundidad >12 mm: lordosis cervical aumentada/hiperlordosis según el método de Penning; correlacionar clínicamente.";
        }

        if (Double.isNaN(normalMin) || Double.isNaN(normalMax)) {
            return normalDiagnosis == null || normalDiagnosis.trim().isEmpty()
                    ? "Medida descriptiva; no se aplica clasificación automática."
                    : normalDiagnosis;
        }

        if (valueMm < normalMin) return lowDiagnosis;
        if (valueMm > normalMax) return highDiagnosis;
        return normalDiagnosis;
    }
}
