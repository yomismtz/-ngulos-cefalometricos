package com.cefalo.angulos;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public class LandmarkCatalogIntegrityTest {
    @Test
    public void airwayDoesNotExposeUnverifiedAd3() {
        for (LinearMeasurementDefinition def : LinearMeasurementCatalog.airway()) {
            assertFalse(def.name.startsWith("AD3"));
            for (String p : def.pointLabels) {
                assertFalse("Uptp".equals(p));
            }
        }
    }

    @Test
    public void cervicalTangentsUseSharedReproduciblePoints() {
        boolean cvt = false;
        boolean opt = false;
        for (MeasurementDefinition def : MeasurementCatalog.vertebral()) {
            if ("SN / CVT".equals(def.name)) {
                cvt = contains(def.pointLabels, "Cv2tg") && contains(def.pointLabels, "Cv4ip");
            }
            if ("SN / OPT".equals(def.name)) {
                opt = contains(def.pointLabels, "Cv2tg") && contains(def.pointLabels, "Cv2ip");
            }
            assertFalse("McGregor–C4".equals(def.name));
        }
        assertTrue(cvt);
        assertTrue(opt);
    }

    private boolean contains(String[] values, String expected) {
        for (String value : values) {
            if (expected.equals(value)) return true;
        }
        return false;
    }
}
