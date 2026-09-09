package com.cefalo.angulos;

public class LinearMeasurementDefinition {

    public enum Type {
        DISTANCE,
        SIGNED_PERPENDICULAR
    }

    public enum Interpretation {
        RANGE,
        HYOID_TRIANGLE,
        CERVICAL_DEPTH
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
                return "Triángulo hioideo positivo: H se encuentra por debajo del plano RGn-C3.";
            }
            if (valueMm < -0.01) {
                return "Triángulo hioideo negativo: H se encuentra por encima del plano RGn-C3.";
            }
            return "H se encuentra sobre el plano RGn-C3.";
        }

        if (interpretation == Interpretation.CERVICAL_DEPTH) {
            if (valueMm < 0) {
                return "Cifótica: el valor se expresa en cifra negativa.";
            }
            if (valueMm < 8.0) {
                return "Rectificación de la lordosis cervical.";
            }
            if (valueMm > 12.0) {
                return "Lordótica.";
            }
            return "Profundidad cervical dentro de la norma.";
        }

        if (valueMm < normalMin) return lowDiagnosis;
        if (valueMm > normalMax) return highDiagnosis;
        return normalDiagnosis;
    }
}
