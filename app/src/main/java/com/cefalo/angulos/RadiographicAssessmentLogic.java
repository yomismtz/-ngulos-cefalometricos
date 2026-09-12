package com.cefalo.angulos;

import java.util.Locale;

/**
 * Pure-Java clinical helper logic for radiographic assessments that do not
 * require free landmark placement. Keeping this class Android-free makes the
 * algorithms unit-testable.
 *
 * Educational use only. Reference values are population- and method-dependent.
 */
public final class RadiographicAssessmentLogic {

    public enum VertebralShape {
        TRAPEZOID,
        RECTANGULAR_HORIZONTAL,
        SQUARE,
        RECTANGULAR_VERTICAL,
        UNKNOWN
    }

    public static final class CvmResult {
        public final String stage;
        public final String summary;
        public final boolean conclusive;

        CvmResult(String stage, String summary, boolean conclusive) {
            this.stage = stage;
            this.summary = summary;
            this.conclusive = conclusive;
        }
    }

    // Nolla norms for the sum of seven permanent teeth, excluding the third
    // molar. Rows correspond to ages 3 through 17 years. Source: Nolla-derived
    // age-norm tables reproduced in contemporary validation literature.
    private static final double[] NOLLA_BOYS_MANDIBULAR = {
            22.3, 30.3, 37.1, 43.0, 48.7, 53.7, 57.9, 61.5,
            64.0, 66.3, 67.8, 69.0, 69.7, 70.0, 70.0
    };
    private static final double[] NOLLA_GIRLS_MANDIBULAR = {
            24.6, 32.7, 40.1, 46.6, 52.4, 57.4, 58.4, 64.8,
            66.3, 67.9, 68.9, 69.4, 69.8, 70.0, 70.0
    };
    private static final double[] NOLLA_BOYS_MAXILLARY = {
            18.9, 26.1, 33.1, 39.6, 45.5, 50.8, 55.5, 59.5,
            62.6, 65.3, 67.3, 68.5, 69.3, 70.0, 70.0
    };
    private static final double[] NOLLA_GIRLS_MAXILLARY = {
            22.2, 29.6, 37.9, 43.4, 49.5, 54.9, 59.6, 63.4,
            64.0, 67.8, 69.2, 69.7, 69.8, 70.0, 70.0
    };

    private RadiographicAssessmentLogic() {}

    /**
     * Modified Baccetti/McNamara CVM classification using C2, C3 and C4.
     * The three booleans indicate presence of a definite inferior concavity.
     */
    public static CvmResult classifyCvm(
            boolean c2Concave,
            boolean c3Concave,
            boolean c4Concave,
            VertebralShape c3Shape,
            VertebralShape c4Shape
    ) {
        if (c3Shape == null) c3Shape = VertebralShape.UNKNOWN;
        if (c4Shape == null) c4Shape = VertebralShape.UNKNOWN;

        boolean bothTrapezoid =
                c3Shape == VertebralShape.TRAPEZOID
                        && c4Shape == VertebralShape.TRAPEZOID;

        boolean c3C4Early = isOneOf(
                c3Shape,
                VertebralShape.TRAPEZOID,
                VertebralShape.RECTANGULAR_HORIZONTAL
        ) && isOneOf(
                c4Shape,
                VertebralShape.TRAPEZOID,
                VertebralShape.RECTANGULAR_HORIZONTAL
        );

        if (!c2Concave && !c3Concave && !c4Concave && bothTrapezoid) {
            return new CvmResult(
                    "CS1",
                    "Etapa prepuberal. Los bordes inferiores de C2-C4 son planos y C3-C4 son trapezoidales. El pico de crecimiento mandibular todavía se encuentra alejado; la referencia clásica lo sitúa al menos alrededor de 2 años después de CS1.",
                    true
            );
        }

        if (c2Concave && !c3Concave && !c4Concave && bothTrapezoid) {
            return new CvmResult(
                    "CS2",
                    "Etapa prepuberal. Aparece concavidad en C2, mientras C3 y C4 conservan borde inferior plano y forma trapezoidal. El pico puberal suele aproximarse durante el año siguiente, con variabilidad individual.",
                    true
            );
        }

        if (c2Concave && c3Concave && !c4Concave && c3C4Early) {
            return new CvmResult(
                    "CS3",
                    "Etapa circumpuberal. Hay concavidad en C2 y C3; C4 todavía no muestra una concavidad definida. C3-C4 son trapezoidales o rectangulares horizontales. Corresponde a la fase ascendente alrededor del pico de crecimiento.",
                    true
            );
        }

        if (c2Concave && c3Concave && c4Concave
                && c3Shape == VertebralShape.RECTANGULAR_HORIZONTAL
                && c4Shape == VertebralShape.RECTANGULAR_HORIZONTAL) {
            return new CvmResult(
                    "CS4",
                    "Etapa circumpuberal tardía. C2-C4 presentan concavidad inferior y C3-C4 son rectangulares horizontales. El pico de crecimiento mandibular generalmente ya ocurrió recientemente.",
                    true
            );
        }

        if (c2Concave && c3Concave && c4Concave
                && (c3Shape == VertebralShape.SQUARE || c4Shape == VertebralShape.SQUARE)
                && c3Shape != VertebralShape.RECTANGULAR_VERTICAL
                && c4Shape != VertebralShape.RECTANGULAR_VERTICAL) {
            return new CvmResult(
                    "CS5",
                    "Etapa postpuberal. Las tres vértebras muestran concavidad y al menos C3 o C4 es cuadrada; la otra puede permanecer rectangular horizontal. La mayor parte del pico puberal ya pasó.",
                    true
            );
        }

        if (c2Concave && c3Concave && c4Concave
                && (c3Shape == VertebralShape.RECTANGULAR_VERTICAL
                || c4Shape == VertebralShape.RECTANGULAR_VERTICAL)) {
            return new CvmResult(
                    "CS6",
                    "Etapa postpuberal. Las concavidades inferiores están presentes y al menos C3 o C4 es rectangular vertical. Representa una fase madura posterior al pico puberal.",
                    true
            );
        }

        return new CvmResult(
                "Patrón intermedio",
                "La combinación seleccionada no cumple de forma limpia los criterios de una sola etapa CS1-CS6. Revise la presencia real de las concavidades y la forma de C3/C4. Es preferible informar un estadio intermedio (por ejemplo CS2-3) que forzar una clasificación.",
                false
        );
    }

    private static boolean isOneOf(
            VertebralShape shape,
            VertebralShape a,
            VertebralShape b
    ) {
        return shape == a || shape == b;
    }

    public static String nollaStageDescription(double stage) {
        int base = (int) Math.floor(stage + 1e-6);
        switch (base) {
            case 0: return "0 · Ausencia de cripta";
            case 1: return "1 · Cripta presente";
            case 2: return "2 · Calcificación inicial";
            case 3: return "3 · Un tercio de corona formado";
            case 4: return "4 · Dos tercios de corona formados";
            case 5: return "5 · Corona casi completa";
            case 6: return "6 · Corona completa";
            case 7: return "7 · Un tercio de raíz formado";
            case 8: return "8 · Dos tercios de raíz formados";
            case 9: return "9 · Raíz casi completa, ápice abierto";
            case 10: return "10 · Raíz completa y cierre apical";
            default: return "Etapa no válida";
        }
    }

    /**
     * Valid Nolla scores are integer stages 0-10 or intermediate additions
     * recommended by Nolla (.2, .5, .7). This method deliberately does not
     * silently round a value entered by the user.
     */
    public static boolean isValidNollaScore(double score) {
        if (score < 0.0 || score > 10.0) return false;
        double fraction = score - Math.floor(score);
        return close(fraction, 0.0)
                || close(fraction, 0.2)
                || close(fraction, 0.5)
                || close(fraction, 0.7);
    }

    private static boolean close(double a, double b) {
        return Math.abs(a - b) < 0.001;
    }

    /**
     * Estimates dental age from the sum of seven Nolla stages. The result is a
     * linear interpolation between adjacent age-norm rows and is therefore an
     * estimate, never an exact chronological age.
     *
     * @return age in decimal years, or NaN when the sum lies outside the table.
     */
    public static double estimateNollaAge(
            boolean female,
            boolean maxillary,
            double sum
    ) {
        double[] table = nollaTable(female, maxillary);
        if (sum < table[0] - 1e-6 || sum > 70.0 + 1e-6) {
            return Double.NaN;
        }

        // At full maturation the table plateaus; report the first age at which
        // 70 points is reached instead of implying precision beyond the table.
        if (sum >= 70.0 - 1e-6) {
            for (int i = 0; i < table.length; i++) {
                if (table[i] >= 70.0 - 1e-6) return 3.0 + i;
            }
        }

        for (int i = 0; i < table.length - 1; i++) {
            double lo = table[i];
            double hi = table[i + 1];
            if (sum < lo - 1e-6 || sum > hi + 1e-6) continue;

            if (Math.abs(hi - lo) < 1e-9) {
                return 3.0 + i;
            }

            double fraction = (sum - lo) / (hi - lo);
            return 3.0 + i + fraction;
        }

        return Double.NaN;
    }

    private static double[] nollaTable(boolean female, boolean maxillary) {
        if (female) {
            return maxillary ? NOLLA_GIRLS_MAXILLARY : NOLLA_GIRLS_MANDIBULAR;
        }
        return maxillary ? NOLLA_BOYS_MAXILLARY : NOLLA_BOYS_MANDIBULAR;
    }

    public static String formatDentalAge(double ageYears) {
        if (Double.isNaN(ageYears)) {
            return "Fuera del intervalo cubierto por la tabla de referencia";
        }
        int years = (int) Math.floor(ageYears + 1e-9);
        int months = (int) Math.round((ageYears - years) * 12.0);
        if (months >= 12) {
            years++;
            months = 0;
        }
        return String.format(Locale.US, "%d años %d meses (≈ %.2f años)", years, months, ageYears);
    }

    public static String resorptionInterpretation(String stage) {
        if (stage == null) return "Seleccione un estadio.";
        switch (stage) {
            case "SIN_REABSORCION":
                return "Raíz temporal completa o sin reabsorción radiográfica evidente. Correlacione con el desarrollo y posición del sucesor permanente.";
            case "INICIAL":
                return "Inicio de reabsorción radicular. Se observan cambios iniciales, habitualmente en la región apical o en la superficie próxima al sucesor.";
            case "R1_4":
                return "Reabsorción aproximada de un cuarto de la longitud/estructura radicular. Es una categoría morfológica, no una fecha exacta de exfoliación.";
            case "R1_2":
                return "Reabsorción aproximada de la mitad de la raíz. Valore movilidad clínica, posición del sucesor y espacio disponible.";
            case "R3_4":
                return "Reabsorción avanzada, cercana a tres cuartos. El soporte radicular remanente es reducido; correlacione con clínica y erupción del sucesor.";
            case "COMPLETA":
                return "Reabsorción prácticamente completa/exfoliación. Si el sucesor no muestra una trayectoria esperada, requiere valoración clínica individual.";
            default:
                return "Estadio no reconocido.";
        }
    }
}
