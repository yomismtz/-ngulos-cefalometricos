package com.cefalo.angulos;

import org.junit.Test;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

public class AssessmentInputValidatorTest {

    @Test
    public void cvmRequiresEverySelectionToBeExplicit() {
        assertFalse(AssessmentInputValidator.cvmSelectionsComplete(0, 1, 1, 1, 1));
        assertFalse(AssessmentInputValidator.cvmSelectionsComplete(1, 1, 1, 0, 1));
        assertTrue(AssessmentInputValidator.cvmSelectionsComplete(1, 2, 1, 3, 2));
    }

    @Test
    public void nollaRequiresSexArchAndSide() {
        assertFalse(AssessmentInputValidator.nollaSelectionsComplete(0, 1, 1));
        assertFalse(AssessmentInputValidator.nollaSelectionsComplete(1, 0, 1));
        assertFalse(AssessmentInputValidator.nollaSelectionsComplete(1, 1, 0));
        assertTrue(AssessmentInputValidator.nollaSelectionsComplete(2, 2, 2));
    }

    @Test
    public void resorptionRequiresToothAndStage() {
        assertFalse(AssessmentInputValidator.resorptionSelectionsComplete(0, 1));
        assertFalse(AssessmentInputValidator.resorptionSelectionsComplete(1, 0));
        assertTrue(AssessmentInputValidator.resorptionSelectionsComplete(5, 3));
    }

    @Test
    public void chronologicalAgeRejectsImpossibleValues() {
        assertTrue(AssessmentInputValidator.chronologicalAgeValid(12, 0));
        assertTrue(AssessmentInputValidator.chronologicalAgeValid(0, 11));
        assertFalse(AssessmentInputValidator.chronologicalAgeValid(-1, 0));
        assertFalse(AssessmentInputValidator.chronologicalAgeValid(12, 12));
        assertFalse(AssessmentInputValidator.chronologicalAgeValid(121, 0));
    }
}
