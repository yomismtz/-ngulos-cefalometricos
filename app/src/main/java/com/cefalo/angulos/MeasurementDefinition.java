package com.cefalo.angulos;

public class MeasurementDefinition {
    public enum Type { THREE_POINTS, TWO_LINES }

    public final String name;
    public final Type type;
    public final String[] pointLabels;
    public final double normalMin;
    public final double normalMax;
    public final String normText;
    public final String instruction;
    public final String lowDiagnosis;
    public final String normalDiagnosis;
    public final String highDiagnosis;
    public final boolean chooseSupplementClosestToNorm;

    public MeasurementDefinition(
            String name,
            Type type,
            String[] pointLabels,
            double normalMin,
            double normalMax,
            String normText,
            String instruction,
            String lowDiagnosis,
            String normalDiagnosis,
            String highDiagnosis,
            boolean chooseSupplementClosestToNorm) {
        this.name = name;
        this.type = type;
        this.pointLabels = pointLabels;
        this.normalMin = normalMin;
        this.normalMax = normalMax;
        this.normText = normText;
        this.instruction = instruction;
        this.lowDiagnosis = lowDiagnosis;
        this.normalDiagnosis = normalDiagnosis;
        this.highDiagnosis = highDiagnosis;
        this.chooseSupplementClosestToNorm = chooseSupplementClosestToNorm;
    }

    public String diagnosis(double value) {
        if (Double.isNaN(normalMin) || Double.isNaN(normalMax)) {
            return normalDiagnosis == null || normalDiagnosis.trim().isEmpty()
                    ? "Medida descriptiva; no se aplica clasificación automática."
                    : normalDiagnosis;
        }

        if (value < normalMin) return lowDiagnosis;
        if (value > normalMax) return highDiagnosis;
        return normalDiagnosis;
    }

    @Override
    public String toString() {
        return name;
    }
}
