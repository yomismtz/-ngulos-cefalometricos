package com.cefalo.angulos;

import org.junit.Test;

import static com.cefalo.angulos.RadiographicAssessmentLogic.VertebralShape.RECTANGULAR_HORIZONTAL;
import static com.cefalo.angulos.RadiographicAssessmentLogic.VertebralShape.RECTANGULAR_VERTICAL;
import static com.cefalo.angulos.RadiographicAssessmentLogic.VertebralShape.SQUARE;
import static com.cefalo.angulos.RadiographicAssessmentLogic.VertebralShape.TRAPEZOID;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

public class RadiographicAssessmentLogicTest {

    @Test
    public void classifiesCvmStagesOneThroughSix() {
        assertEquals("CS1", RadiographicAssessmentLogic.classifyCvm(
                false, false, false, TRAPEZOID, TRAPEZOID).stage);
        assertEquals("CS2", RadiographicAssessmentLogic.classifyCvm(
                true, false, false, TRAPEZOID, TRAPEZOID).stage);
        assertEquals("CS3", RadiographicAssessmentLogic.classifyCvm(
                true, true, false, TRAPEZOID, RECTANGULAR_HORIZONTAL).stage);
        assertEquals("CS4", RadiographicAssessmentLogic.classifyCvm(
                true, true, true, RECTANGULAR_HORIZONTAL, RECTANGULAR_HORIZONTAL).stage);
        assertEquals("CS5", RadiographicAssessmentLogic.classifyCvm(
                true, true, true, SQUARE, RECTANGULAR_HORIZONTAL).stage);
        assertEquals("CS6", RadiographicAssessmentLogic.classifyCvm(
                true, true, true, RECTANGULAR_VERTICAL, SQUARE).stage);
    }

    @Test
    public void doesNotForceAnInconsistentCvmPattern() {
        RadiographicAssessmentLogic.CvmResult result =
                RadiographicAssessmentLogic.classifyCvm(
                        false, true, false, TRAPEZOID, TRAPEZOID);
        assertFalse(result.conclusive);
        assertEquals("Patrón intermedio", result.stage);
    }

    @Test
    public void nollaReferenceTableReturnsExactFemaleMandibularAgeEight() {
        double age = RadiographicAssessmentLogic.estimateNollaAge(
                true,
                false,
                57.4
        );
        assertEquals(8.0, age, 0.0001);
    }

    @Test
    public void nollaReferenceTableInterpolatesBetweenAdjacentRows() {
        // Boys, mandibular: age 8 = 53.7 and age 9 = 57.9.
        double midpoint = (53.7 + 57.9) / 2.0;
        double age = RadiographicAssessmentLogic.estimateNollaAge(
                false,
                false,
                midpoint
        );
        assertEquals(8.5, age, 0.0001);
    }

    @Test
    public void nollaAcceptsRecommendedIntermediateStageFractionsOnly() {
        assertTrue(RadiographicAssessmentLogic.isValidNollaScore(7.0));
        assertTrue(RadiographicAssessmentLogic.isValidNollaScore(7.2));
        assertTrue(RadiographicAssessmentLogic.isValidNollaScore(7.5));
        assertTrue(RadiographicAssessmentLogic.isValidNollaScore(7.7));
        assertFalse(RadiographicAssessmentLogic.isValidNollaScore(7.3));
        assertFalse(RadiographicAssessmentLogic.isValidNollaScore(10.2));
    }

    @Test
    public void fullyMatureNollaScoreUsesFirstAgeAtPlateau() {
        assertEquals(16.0, RadiographicAssessmentLogic.estimateNollaAge(
                false, false, 70.0), 0.0001);
        assertEquals(16.0, RadiographicAssessmentLogic.estimateNollaAge(
                true, true, 70.0), 0.0001);
    }
}
