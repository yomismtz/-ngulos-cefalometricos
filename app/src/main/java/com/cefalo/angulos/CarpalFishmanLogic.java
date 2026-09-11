package com.cefalo.angulos;

/**
 * Educational interpretation helpers for Fishman's hand-wrist Skeletal Maturity
 * Indicators (SMI 1-11). The method stages skeletal maturation; it must not be
 * presented as an exact chronological age in years because age distributions
 * vary by sex, ancestry/population and study design.
 */
public final class CarpalFishmanLogic {
    private CarpalFishmanLogic() {}

    public static boolean isValidSmi(int smi) {
        return smi >= 1 && smi <= 11;
    }

    public static String stageDescription(int smi) {
        switch (smi) {
            case 1:
                return "SMI 1 · PP3: epífisis de la falange proximal del 3.er dedo con anchura igual a la diáfisis.";
            case 2:
                return "SMI 2 · MP3: epífisis de la falange media del 3.er dedo con anchura igual a la diáfisis.";
            case 3:
                return "SMI 3 · MP5: epífisis de la falange media del 5.º dedo con anchura igual a la diáfisis.";
            case 4:
                return "SMI 4 · Aparición/ossificación del sesamoideo aductor del pulgar.";
            case 5:
                return "SMI 5 · DP3cap: capping de la epífisis de la falange distal del 3.er dedo.";
            case 6:
                return "SMI 6 · MP3cap: capping de la epífisis de la falange media del 3.er dedo.";
            case 7:
                return "SMI 7 · MP5cap: capping de la epífisis de la falange media del 5.º dedo.";
            case 8:
                return "SMI 8 · DP3u: fusión epífisis-diáfisis de la falange distal del 3.er dedo.";
            case 9:
                return "SMI 9 · PP3u: fusión epífisis-diáfisis de la falange proximal del 3.er dedo.";
            case 10:
                return "SMI 10 · MP3u: fusión epífisis-diáfisis de la falange media del 3.er dedo.";
            case 11:
                return "SMI 11 · Ru: fusión epífisis-diáfisis del radio.";
            default:
                return "SMI no válido.";
        }
    }

    public static String maturationPhase(int smi) {
        if (smi >= 1 && smi <= 3) {
            return "Fase prepuberal · antes del pico de crecimiento.";
        }
        if (smi == 4) {
            return "Fase de aceleración puberal · aproximándose al pico de crecimiento.";
        }
        if (smi >= 5 && smi <= 7) {
            return "Fase puberal de alta velocidad · alrededor del pico de crecimiento.";
        }
        if (smi == 8) {
            return "Transición pospico · inicio de desaceleración del crecimiento.";
        }
        if (smi == 9 || smi == 10) {
            return "Fase de desaceleración / pospuberal · crecimiento residual progresivamente menor.";
        }
        if (smi == 11) {
            return "Fase pospuberal avanzada · maduración esquelética muy avanzada y crecimiento remanente limitado.";
        }
        return "Fase no determinada.";
    }

    public static String orthodonticContext(int smi) {
        if (smi >= 1 && smi <= 3) {
            return "Existe potencial de crecimiento importante. Para decisiones ortopédicas, correlacione con CVM, crecimiento clínico y sexo/edad del paciente.";
        }
        if (smi >= 4 && smi <= 7) {
            return "Periodo clínicamente relevante para valorar terapias dependientes del crecimiento. El momento exacto del pico no debe inferirse de un único indicador aislado.";
        }
        if (smi == 8) {
            return "El pico de crecimiento probablemente ya ha ocurrido o está terminando; correlacione con otros indicadores antes de concluir el potencial residual.";
        }
        if (smi >= 9 && smi <= 11) {
            return "Maduración avanzada. El potencial de modificación ortopédica por crecimiento suele ser menor, pero la decisión clínica no debe basarse únicamente en la radiografía carpal.";
        }
        return "Seleccione un SMI válido para obtener contexto clínico.";
    }

    public static String report(int smi) {
        if (!isValidSmi(smi)) {
            return "No se pudo determinar un SMI válido.";
        }
        return "Edad ósea / maduración esquelética carpal · Fishman\n\n"
                + stageDescription(smi) + "\n"
                + maturationPhase(smi) + "\n\n"
                + orthodonticContext(smi) + "\n\n"
                + "Importante: Fishman clasifica maduración esquelética (SMI 1–11). "
                + "YOM no convierte automáticamente el SMI en una edad exacta en años porque "
                + "las edades cronológicas asociadas cambian entre sexos y poblaciones. "
                + "Uso educativo y de apoyo clínico; correlacionar con antecedentes, exploración y otros indicadores de crecimiento.";
    }
}
