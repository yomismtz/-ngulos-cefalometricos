package com.cefalo.angulos;

/**
 * Pure-Java validation helpers for assessment screens. Position 0 is reserved
 * for an explicit "Seleccione" placeholder so no clinical result can be
 * produced from an untouched default value.
 */
public final class AssessmentInputValidator {
    private AssessmentInputValidator() {}

    public static boolean isExplicitSelection(int position) {
        return position > 0;
    }

    public static boolean cvmSelectionsComplete(
            int c2Concavity,
            int c3Concavity,
            int c4Concavity,
            int c3Shape,
            int c4Shape
    ) {
        return isExplicitSelection(c2Concavity)
                && isExplicitSelection(c3Concavity)
                && isExplicitSelection(c4Concavity)
                && isExplicitSelection(c3Shape)
                && isExplicitSelection(c4Shape);
    }

    public static boolean nollaSelectionsComplete(
            int sex,
            int arch,
            int side
    ) {
        return isExplicitSelection(sex)
                && isExplicitSelection(arch)
                && isExplicitSelection(side);
    }

    public static boolean resorptionSelectionsComplete(
            int tooth,
            int stage
    ) {
        return isExplicitSelection(tooth)
                && isExplicitSelection(stage);
    }

    public static boolean chronologicalAgeValid(int years, int months) {
        return years >= 0
                && years <= 120
                && months >= 0
                && months <= 11;
    }
}
