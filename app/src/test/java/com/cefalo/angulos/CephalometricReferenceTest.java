package com.cefalo.angulos;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

import java.util.List;

public class CephalometricReferenceTest {

    private MeasurementDefinition angular(
            List<MeasurementDefinition> list,
            String name
    ) {
        for (MeasurementDefinition def : list) {
            if (name.equals(def.name)) return def;
        }
        throw new AssertionError("Missing angular definition: " + name);
    }

    private LinearMeasurementDefinition linear(
            List<LinearMeasurementDefinition> list,
            String name
    ) {
        for (LinearMeasurementDefinition def : list) {
            if (name.equals(def.name)) return def;
        }
        throw new AssertionError("Missing linear definition: " + name);
    }

    @Test
    public void steinerCoreReferencesRemainConsistent() {
        List<MeasurementDefinition> defs = MeasurementCatalog.steiner();

        MeasurementDefinition sna = angular(defs, "SNA");
        assertEquals(80.0, sna.normalMin, 0.001);
        assertEquals(84.0, sna.normalMax, 0.001);

        MeasurementDefinition snb = angular(defs, "SNB");
        assertEquals(78.0, snb.normalMin, 0.001);
        assertEquals(82.0, snb.normalMax, 0.001);

        MeasurementDefinition anb = angular(defs, "ANB");
        assertEquals(MeasurementDefinition.Type.SIGNED_ANB, anb.type);
        assertArrayEquals(
                new String[]{"S", "N", "A", "B"},
                anb.pointLabels
        );
        assertEquals(0.0, anb.normalMin, 0.001);
        assertEquals(4.0, anb.normalMax, 0.001);

        MeasurementDefinition mpSn = angular(defs, "Go-Gn / SN");
        assertEquals(27.0, mpSn.normalMin, 0.001);
        assertEquals(37.0, mpSn.normalMax, 0.001);

        MeasurementDefinition upperNa = angular(defs, "IS / NA (angular)");
        assertEquals(20.0, upperNa.normalMin, 0.001);
        assertEquals(24.0, upperNa.normalMax, 0.001);

        MeasurementDefinition lowerNb = angular(defs, "II / NB (angular)");
        assertEquals(23.0, lowerNb.normalMin, 0.001);
        assertEquals(27.0, lowerNb.normalMax, 0.001);
    }

    @Test
    public void vertebralAnbUsesSameSignedDefinitionAsSteiner() {
        MeasurementDefinition anb =
                angular(MeasurementCatalog.vertebral(), "ANB");

        assertEquals(MeasurementDefinition.Type.SIGNED_ANB, anb.type);
        assertArrayEquals(
                new String[]{"S", "N", "A", "B"},
                anb.pointLabels
        );
    }

    @Test
    public void snFrankfortReferenceDoesNotChangeBetweenModules() {
        MeasurementDefinition steiner =
                angular(
                        MeasurementCatalog.steiner(),
                        "SN / Frankfort (complementaria)"
                );

        MeasurementDefinition vertebral =
                angular(
                        MeasurementCatalog.vertebral(),
                        "SN / Frankfort"
                );

        assertEquals(steiner.normalMin, vertebral.normalMin, 0.001);
        assertEquals(steiner.normalMax, vertebral.normalMax, 0.001);
        assertEquals(4.0, vertebral.normalMin, 0.001);
        assertEquals(10.0, vertebral.normalMax, 0.001);
    }

    @Test
    public void tweedCentralReferencesRemainCoherent() {
        List<MeasurementDefinition> defs = MeasurementCatalog.tweed();

        MeasurementDefinition fma = angular(defs, "FMA");
        MeasurementDefinition fmia = angular(defs, "FMIA");
        MeasurementDefinition impa = angular(defs, "IMPA");

        assertEquals(20.0, fma.normalMin, 0.001);
        assertEquals(30.0, fma.normalMax, 0.001);

        assertEquals(60.0, fmia.normalMin, 0.001);
        assertEquals(70.0, fmia.normalMax, 0.001);

        assertEquals(85.0, impa.normalMin, 0.001);
        assertEquals(95.0, impa.normalMax, 0.001);
    }

    @Test
    public void cervicalDepthUsesPenningRocabadoBoundaries() {
        LinearMeasurementDefinition depth =
                linear(
                        LinearMeasurementCatalog.rocabado(),
                        "Profundidad de la columna cervical"
                );

        assertTrue(depth.diagnosis(1.9).contains("<2 mm"));
        assertTrue(depth.diagnosis(2.0).contains("2 a <8 mm"));
        assertTrue(depth.diagnosis(7.9).contains("2 a <8 mm"));
        assertTrue(depth.diagnosis(8.0).contains("8 a 12 mm"));
        assertTrue(depth.diagnosis(12.0).contains("8 a 12 mm"));
        assertTrue(depth.diagnosis(12.1).contains(">12 mm"));
    }

    @Test
    public void hyoidPublishedReferenceIsDisplayed() {
        LinearMeasurementDefinition hyoid =
                linear(
                        LinearMeasurementCatalog.rocabado(),
                        "Posición vertical H respecto a RGn-C3"
                );

        assertTrue(hyoid.normText.contains("4.80"));
        assertTrue(hyoid.normText.contains("4.64"));
    }
}
