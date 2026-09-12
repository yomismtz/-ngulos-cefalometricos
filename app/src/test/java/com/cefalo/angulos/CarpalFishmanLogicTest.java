package com.cefalo.angulos;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public class CarpalFishmanLogicTest {
    @Test public void validatesFishmanRange() {
        assertFalse(CarpalFishmanLogic.isValidSmi(0));
        assertTrue(CarpalFishmanLogic.isValidSmi(1));
        assertTrue(CarpalFishmanLogic.isValidSmi(11));
        assertFalse(CarpalFishmanLogic.isValidSmi(12));
    }

    @Test public void descriptionsCoverKeyTransitions() {
        assertTrue(CarpalFishmanLogic.stageDescription(4).contains("sesamoideo"));
        assertTrue(CarpalFishmanLogic.stageDescription(8).contains("fusión"));
        assertTrue(CarpalFishmanLogic.stageDescription(11).contains("radio"));
    }

    @Test public void reportDoesNotClaimExactAgeInYears() {
        String report = CarpalFishmanLogic.report(6);
        assertTrue(report.contains("SMI 6"));
        assertTrue(report.contains("no convierte automáticamente"));
        assertTrue(report.contains("edad exacta en años"));
    }
}
