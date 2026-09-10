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
    public void cephalometricCoreReferencesMatchAuditedCatalog() {
        List<MeasurementDefinition> defs = MeasurementCatalog.steiner();

        MeasurementDefinition sna = angular(defs, "SNA");
        assertEquals(80.0, sna.normalMin, 0.001);
        assertEquals(84.0, sna.normalMax, 0.001);

        MeasurementDefinition snb = angular(defs, "SNB");
        assertEquals(78.0, snb.normalMin, 0.001);
        assertEquals(82.0, snb.normalMax, 0.001);

        MeasurementDefinition anb = angular(defs, "ANB");
        assertEquals(MeasurementDefinition.Type.SIGNED_ANB, anb.type);
        assertArrayEquals(new String[]{"S", "N", "A", "B"}, anb.pointLabels);
        assertEquals(0.0, anb.normalMin, 0.001);
        assertEquals(4.0, anb.normalMax, 0.001);

        MeasurementDefinition mpSn = angular(defs, "SN / Go-Gn");
        assertEquals(27.0, mpSn.normalMin, 0.001);
        assertEquals(37.0, mpSn.normalMax, 0.001);

        MeasurementDefinition upperNa = angular(defs, "Incisivo superior / NA · angular");
        assertEquals(20.0, upperNa.normalMin, 0.001);
        assertEquals(24.0, upperNa.normalMax, 0.001);

        MeasurementDefinition lowerNb = angular(defs, "Incisivo inferior / NB · angular");
        assertEquals(21.0, lowerNb.normalMin, 0.001);
        assertEquals(29.0, lowerNb.normalMax, 0.001);

        MeasurementDefinition occlusal = angular(defs, "Plano oclusal / SN");
        assertEquals(11.0, occlusal.normalMin, 0.001);
        assertEquals(17.0, occlusal.normalMax, 0.001);

        MeasurementDefinition interincisal = angular(defs, "Ángulo interincisal");
        assertEquals(127.0, interincisal.normalMin, 0.001);
        assertEquals(135.0, interincisal.normalMax, 0.001);

        MeasurementDefinition snFh = angular(defs, "Inclinación SN / Frankfort");
        assertTrue(Double.isNaN(snFh.normalMin));
        assertTrue(Double.isNaN(snFh.normalMax));
        assertArrayEquals(new String[]{"S", "N", "Po", "Or"}, snFh.pointLabels);
    }

    @Test
    public void cephalometricLinearSegmentsUseConstructedProjections() {
        List<LinearMeasurementDefinition> defs = LinearMeasurementCatalog.cephalometric();

        LinearMeasurementDefinition sl = linear(defs, "Segmento SL");
        assertEquals(LinearMeasurementDefinition.Type.AXIAL_PROJECTION, sl.type);
        assertArrayEquals(new String[]{"S", "N", "Pg"}, sl.pointLabels);
        assertEquals(47.0, sl.normalMin, 0.001);
        assertEquals(55.0, sl.normalMax, 0.001);

        LinearMeasurementDefinition se = linear(defs, "Segmento SE");
        assertEquals(LinearMeasurementDefinition.Type.AXIAL_PROJECTION, se.type);
        assertArrayEquals(new String[]{"S", "N", "Cóndilo posterior"}, se.pointLabels);
        assertEquals(20.0, se.normalMin, 0.001);
        assertEquals(24.0, se.normalMax, 0.001);

        LinearMeasurementDefinition upper = linear(defs, "Incisivo superior a NA · lineal");
        assertEquals(2.0, upper.normalMin, 0.001);
        assertEquals(6.0, upper.normalMax, 0.001);

        LinearMeasurementDefinition lower = linear(defs, "Incisivo inferior a NB · lineal");
        assertEquals(3.0, lower.normalMin, 0.001);
        assertEquals(5.0, lower.normalMax, 0.001);
    }

    @Test
    public void postureModuleUsesDefinedCervicalLandmarks() {
        List<MeasurementDefinition> defs = MeasurementCatalog.vertebral();

        MeasurementDefinition opt = angular(defs, "SN / OPT");
        assertArrayEquals(new String[]{"S", "N", "CV2tg", "CV2ip"}, opt.pointLabels);

        MeasurementDefinition cvt = angular(defs, "SN / CVT");
        assertArrayEquals(new String[]{"S", "N", "CV2tg", "CV4ip"}, cvt.pointLabels);

        MeasurementDefinition curve = angular(defs, "Curvatura cervical · CVT / EVT");
        assertArrayEquals(new String[]{"CV2tg", "CV4ip", "CV4ip", "CV6ip"}, curve.pointLabels);
    }

    @Test
    public void tweedCentralReferencesRemainCoherent() {
        List<MeasurementDefinition> defs = MeasurementCatalog.tweed();

        MeasurementDefinition fma = angular(defs, "FMA");
        MeasurementDefinition fmia = angular(defs, "FMIA");
        MeasurementDefinition impa = angular(defs, "IMPA");

        assertEquals(21.0, fma.normalMin, 0.001);
        assertEquals(29.0, fma.normalMax, 0.001);
        assertEquals(61.0, fmia.normalMin, 0.001);
        assertEquals(69.0, fmia.normalMax, 0.001);
        assertEquals(86.0, impa.normalMin, 0.001);
        assertEquals(94.0, impa.normalMax, 0.001);
    }

    @Test
    public void cervicalDepthUsesAuditedPenningBoundaries() {
        LinearMeasurementDefinition depth = linear(
                LinearMeasurementCatalog.rocabado(),
                "Profundidad de la columna cervical · Penning"
        );

        assertTrue(depth.diagnosis(-0.1).contains("cifótica"));
        assertTrue(depth.diagnosis(0.0).contains("rectificación"));
        assertTrue(depth.diagnosis(7.9).contains("rectificación"));
        assertTrue(depth.diagnosis(8.0).contains("8 a 12 mm"));
        assertTrue(depth.diagnosis(12.0).contains("8 a 12 mm"));
        assertTrue(depth.diagnosis(12.1).contains("lordosis cervical aumentada"));
    }

    @Test
    public void hyoidTriangleIsExplicitlyRepresented() {
        LinearMeasurementDefinition hyoid = linear(
                LinearMeasurementCatalog.rocabado(),
                "Altura / posición del hioides respecto a C3-RGn"
        );

        assertEquals(LinearMeasurementDefinition.Interpretation.HYOID_TRIANGLE, hyoid.interpretation);
        assertArrayEquals(new String[]{"C3", "RGn", "H"}, hyoid.pointLabels);
        assertTrue(hyoid.normText.contains("C3-RGn-H"));
    }
}
