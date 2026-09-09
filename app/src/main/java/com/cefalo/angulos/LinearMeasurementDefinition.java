package com.cefalo.angulos;

public class LinearMeasurementDefinition {

    public enum Type {
        DISTANCE,
        SIGNED_PERPENDICULAR,
        PERPENDICULAR_ABS
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
                return "H está por debajo de la línea C3-RGn (triángulo hioideo positivo). Es una descripción cefalométrica y no un diagnóstico respiratorio.";
            }

            if (valueMm < -0.01) {
                return "H está por encima de la línea C3-RGn (triángulo hioideo negativo). Es una descripción cefalométrica y no un diagnóstico respiratorio.";
            }

            return "H se encuentra prácticamente sobre la línea C3-RGn. Interpretar junto con el resto del trazado.";
        }

        if (interpretation == Interpretation.COMPARATIVE) {
            return normalDiagnosis;
        }

        if (interpretation == Interpretation.CERVICAL_DEPTH) {
            if (valueMm < 2.0) {
                return "Profundidad <2 mm: patrón cifótico según la referencia de Penning/Rocabado; requiere correlación clínica.";
            }

            if (valueMm < 8.0) {
                return "Profundidad de 2 a <8 mm: rectificación de la curvatura cervical según la referencia empleada.";
            }

            if (valueMm <= 12.0) {
                return "Profundidad de 8 a 12 mm: dentro del intervalo de referencia empleado.";
            }

            return "Profundidad >12 mm: curvatura lordótica aumentada según la referencia empleada; correlacionar clínicamente.";
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
