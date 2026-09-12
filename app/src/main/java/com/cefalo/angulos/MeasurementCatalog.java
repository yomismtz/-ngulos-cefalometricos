package com.cefalo.angulos;

import java.util.ArrayList;
import java.util.List;

import static com.cefalo.angulos.MeasurementDefinition.Type.THREE_POINTS;
import static com.cefalo.angulos.MeasurementDefinition.Type.TWO_LINES;
import static com.cefalo.angulos.MeasurementDefinition.Type.SIGNED_ANB;

/**
 * Catálogo angular de YomCeph organizado por tema clínico.
 *
 * Los nombres históricos de los métodos se conservan en las referencias de cada
 * medición cuando corresponde, pero los módulos ya no se presentan como copias
 * literales de un análisis de autor.
 */
public final class MeasurementCatalog {
    private MeasurementCatalog() {}

    /** Módulo: Análisis cefalométrico. */
    public static List<MeasurementDefinition> steiner() {
        List<MeasurementDefinition> list = new ArrayList<>();

        list.add(m(
                "SNA",
                THREE_POINTS,
                p("S", "N", "A"),
                80, 84,
                "82° ± 2°",
                "Marque S, N y A. N es el vértice.",
                "SNA por debajo del intervalo de referencia: posición maxilar relativamente posterior respecto a SN; corroborar con otras medidas.",
                "SNA dentro del intervalo 82° ± 2° de la referencia adoptada.",
                "SNA por encima del intervalo de referencia: posición maxilar relativamente anterior respecto a SN; corroborar con otras medidas.",
                false
        ));

        list.add(m(
                "SNB",
                THREE_POINTS,
                p("S", "N", "B"),
                78, 82,
                "80° ± 2°",
                "Marque S, N y B. N es el vértice.",
                "SNB por debajo del intervalo de referencia: posición mandibular relativamente posterior respecto a SN; corroborar con otras medidas.",
                "SNB dentro del intervalo 80° ± 2° de la referencia adoptada.",
                "SNB por encima del intervalo de referencia: posición mandibular relativamente anterior respecto a SN; corroborar con otras medidas.",
                false
        ));

        list.add(m(
                "ANB",
                SIGNED_ANB,
                p("S", "N", "A", "B"),
                0, 4,
                "2° ± 2°",
                "Marque S, N, A y B. El software conserva el signo de SNA-SNB.",
                "ANB por debajo del intervalo: compatible con una relación sagital más hacia Clase III; confirmar con otras medidas y el examen clínico.",
                "ANB dentro del intervalo de referencia para una relación sagital cercana a Clase I.",
                "ANB por encima del intervalo: compatible con una relación sagital más hacia Clase II; confirmar con otras medidas y el examen clínico.",
                false
        ));

        list.add(m(
                "SND",
                THREE_POINTS,
                p("S", "N", "D"),
                74, 78,
                "76° ± 2°",
                "Marque S, N y D. N es el vértice.",
                "SND por debajo del intervalo de referencia: región sinfisaria/mentón relativamente posterior respecto a la base craneal.",
                "SND dentro del intervalo 76° ± 2° de la referencia adoptada.",
                "SND por encima del intervalo de referencia: región sinfisaria/mentón relativamente anterior respecto a la base craneal.",
                false
        ));

        list.add(m(
                "SN / Go-Gn",
                TWO_LINES,
                p("S", "N", "Go", "Gn"),
                28, 36,
                "32° ± 4°",
                "Marque S-N y Go-Gn.",
                "Ángulo menor al intervalo de referencia: patrón mandibular relativamente más hipodivergente/rotación anterior.",
                "SN/Go-Gn dentro del intervalo 32° ± 4° de la referencia adoptada.",
                "Ángulo mayor al intervalo de referencia: patrón mandibular relativamente más hiperdivergente/rotación posterior.",
                true
        ));

        list.add(m(
                "Eje Y · NS / S-Gn",
                TWO_LINES,
                p("N", "S", "S", "Gn"),
                62, 68,
                "65° ± 3° · referencia cefalométrica publicada",
                "Marque N-S y S-Gn.",
                "Eje Y menor al intervalo de referencia; describir la dirección de crecimiento junto con otras variables verticales.",
                "Eje Y dentro del intervalo de referencia adoptado.",
                "Eje Y mayor al intervalo de referencia; describir la dirección de crecimiento junto con otras variables verticales.",
                false
        ));

        list.add(m(
                "Incisivo superior / SN",
                TWO_LINES,
                p("IS borde", "IS ápice", "S", "N"),
                99, 107,
                "103° ± 4°",
                "Marque el eje del incisivo superior y S-N.",
                "Incisivo superior relativamente retroinclinado respecto a SN.",
                "Incisivo superior dentro del intervalo angular de referencia respecto a SN.",
                "Incisivo superior relativamente proinclinado respecto a SN.",
                true
        ));

        list.add(m(
                "Incisivo superior / NA · angular",
                TWO_LINES,
                p("IS borde", "IS ápice", "N", "A"),
                16, 28,
                "22° ± 6°",
                "Marque el eje del incisivo superior y la línea N-A.",
                "Incisivo superior relativamente retroinclinado respecto a NA.",
                "Incisivo superior dentro del intervalo angular 22° ± 6° de la referencia adoptada.",
                "Incisivo superior relativamente proinclinado respecto a NA.",
                true
        ));

        list.add(m(
                "Incisivo inferior / NB · angular",
                TWO_LINES,
                p("II borde", "II ápice", "N", "B"),
                21, 29,
                "25° ± 4°",
                "Marque el eje del incisivo inferior y la línea N-B.",
                "Incisivo inferior relativamente retroinclinado respecto a NB.",
                "Incisivo inferior dentro del intervalo angular 25° ± 4° de la referencia adoptada.",
                "Incisivo inferior relativamente proinclinado respecto a NB.",
                true
        ));

        list.add(m(
                "Plano oclusal / SN",
                TWO_LINES,
                p("Oclusal 1", "Oclusal 2", "S", "N"),
                11, 17,
                "14° ± 3°",
                "Construya el plano oclusal con sus dos puntos y compárelo con S-N.",
                "Plano oclusal con inclinación menor que el intervalo de referencia respecto a SN.",
                "Plano oclusal dentro del intervalo 14° ± 3° de la referencia adoptada.",
                "Plano oclusal con inclinación mayor que el intervalo de referencia respecto a SN.",
                true
        ));

        list.add(m(
                "Ángulo interincisal",
                TWO_LINES,
                p("IS borde", "IS ápice", "II borde", "II ápice"),
                127, 135,
                "131° ± 4°",
                "Marque los ejes longitudinales de los incisivos superior e inferior.",
                "Ángulo interincisal menor: mayor proinclinación relativa de los incisivos respecto a esta referencia.",
                "Ángulo interincisal dentro del intervalo 131° ± 4° de la referencia adoptada.",
                "Ángulo interincisal mayor: mayor retroinclinación relativa de los incisivos respecto a esta referencia.",
                true
        ));

        list.add(m(
                "Ángulo goníaco Ar-Go-Me · complementario",
                THREE_POINTS,
                p("Ar", "Go", "Me"),
                123, 137,
                "130° ± 7° / 123°–137° · referencia Björk-Jarabak",
                "Marque Ar, Go y Me. Go es el vértice.",
                "Ángulo goníaco menor de 123°: patrón mandibular relativamente más cerrado/hipodivergente en esta referencia.",
                "Ángulo goníaco dentro del intervalo 123°–137° de la referencia adoptada.",
                "Ángulo goníaco mayor de 137°: patrón mandibular relativamente más abierto/hiperdivergente en esta referencia.",
                false
        ));

        return list;
    }

    /** Módulo: Postura cráneo-cervical. */
    public static List<MeasurementDefinition> vertebral() {
        List<MeasurementDefinition> list = new ArrayList<>();

        list.add(m(
                "Ángulo cráneo-odontoideo · McGregor / OP",
                TWO_LINES,
                p("Occipital", "ENP", "Odontoides ápice", "C2 anteroinf."),
                96, 106,
                "101° ± 5° · intervalo funcional 96°–106°",
                "Trace el plano de McGregor entre ENP/PNS y la base occipital; después trace el plano odontoideo entre el ápice de la odontoides y el punto anteroinferior de C2.",
                "Menor de 96°: rotación posterior/extensión relativa del cráneo según la referencia cráneo-cervical adoptada.",
                "Dentro de 96°–106°: intervalo funcional de referencia del ángulo cráneo-odontoideo.",
                "Mayor de 106°: rotación anterior/flexión relativa del cráneo según la referencia cráneo-cervical adoptada.",
                true
        ));

        list.add(m(
                "SN / OPT",
                TWO_LINES,
                p("S", "N", "CV2tg", "CV2ip"),
                93.1, 106.9,
                "≈100.0° ± 6.9° · valor de muestra publicado; no es umbral universal de normalidad",
                "Marque S-N y OPT, formada por CV2tg-CV2ip.",
                "Valor inferior al intervalo de la muestra de referencia. Describir la relación cráneo-odontoidea; no diagnosticar postura por esta medida aislada.",
                "Dentro de ±1 DE de la muestra de referencia publicada; no implica normalidad clínica por sí sola.",
                "Valor superior al intervalo de la muestra de referencia. Describir la relación cráneo-odontoidea; no diagnosticar postura por esta medida aislada.",
                true
        ));

        list.add(m(
                "SN / CVT",
                TWO_LINES,
                p("S", "N", "CV2tg", "CV4ip"),
                97.3, 108.7,
                "≈103.0° ± 5.7° · valor de muestra publicado; no es umbral universal de normalidad",
                "Marque S-N y CVT, formada por CV2tg-CV4ip.",
                "Valor inferior al intervalo de la muestra de referencia. Interpretar en posición natural de la cabeza y junto con otras variables posturales.",
                "Dentro de ±1 DE de la muestra de referencia publicada; no implica normalidad clínica por sí sola.",
                "Valor superior al intervalo de la muestra de referencia. Interpretar en posición natural de la cabeza y junto con otras variables posturales.",
                true
        ));

        list.add(m(
                "Curvatura cervical · CVT / EVT",
                TWO_LINES,
                p("CV2tg", "CV4ip", "CV4ip", "CV6ip"),
                Double.NaN,
                Double.NaN,
                "Ángulo entre CVT (CV2tg-CV4ip) y EVT (CV4ip-CV6ip) · medida descriptiva",
                "Marque CV2tg, CV4ip y CV6ip. El software forma CVT y EVT.",
                "",
                "Describe la angulación entre la porción cervical superior e inferior. No se aplica un umbral universal automático; para rectificación/cifosis/lordosis se usa la profundidad de Penning en el bloque lineal.",
                "",
                false
        ));

        return list;
    }

    /** Módulo: Perfil facial de tejidos blandos. */
    public static List<MeasurementDefinition> powell() {
        List<MeasurementDefinition> list = new ArrayList<>();

        list.add(m(
                "Nasofrontal",
                THREE_POINTS,
                p("G'", "N'", "Pr"),
                115, 130,
                "115°–130°",
                "Marque G', N' y Pr. N' es el vértice.",
                "Ángulo nasofrontal menor al intervalo de referencia de Powell.",
                "Ángulo nasofrontal dentro del intervalo de referencia de Powell.",
                "Ángulo nasofrontal mayor al intervalo de referencia de Powell.",
                false
        ));

        list.add(m(
                "Nasofacial",
                TWO_LINES,
                p("G'", "Pg'", "N'", "Pr"),
                30, 40,
                "30°–40°",
                "Marque el plano facial G'-Pg' y el eje nasal N'-Pr.",
                "Proyección nasal relativa menor respecto al plano facial según esta medida.",
                "Ángulo nasofacial dentro del intervalo estético de referencia de Powell.",
                "Proyección nasal relativa mayor respecto al plano facial según esta medida.",
                true
        ));

        list.add(m(
                "Nasomental",
                THREE_POINTS,
                p("N'", "Pr", "Pg'"),
                120, 132,
                "120°–132°",
                "Marque N', Pr y Pg'. Pr es el vértice.",
                "Ángulo nasomental menor al intervalo de Powell; interpretar la relación nariz-mentón en conjunto.",
                "Ángulo nasomental dentro del intervalo estético de referencia de Powell.",
                "Ángulo nasomental mayor al intervalo de Powell; interpretar la relación nariz-mentón en conjunto.",
                false
        ));

        list.add(m(
                "Mentocervical",
                TWO_LINES,
                p("G'", "Pg'", "Me'", "C"),
                80, 95,
                "80°–95° · algunas publicaciones utilizan un intervalo más estrecho",
                "Marque el plano facial G'-Pg' y la línea mentocervical Me'-C.",
                "Ángulo mentocervical menor al intervalo adoptado; valorar junto con el perfil facial completo.",
                "Ángulo mentocervical dentro del intervalo de referencia adoptado.",
                "Ángulo mentocervical mayor al intervalo adoptado; valorar junto con el contorno submentoniano y el perfil completo.",
                true
        ));

        return list;
    }

    /** Módulo: Triángulo dentofacial. */
    public static List<MeasurementDefinition> tweed() {
        List<MeasurementDefinition> list = new ArrayList<>();

        list.add(m(
                "FMA",
                TWO_LINES,
                p("Po", "Or", "Go", "Me"),
                20, 30,
                "25° ± 5° · referencia clásica del triángulo",
                "Trace Frankfort Po-Or y el plano mandibular Go-Me.",
                "FMA menor de 20°: patrón mandibular relativamente más hipodivergente respecto a esta referencia.",
                "FMA dentro de 25° ± 5°.",
                "FMA mayor de 30°: patrón mandibular relativamente más hiperdivergente respecto a esta referencia.",
                true
        ));

        list.add(m(
                "FMIA",
                TWO_LINES,
                p("Po", "Or", "II borde", "II ápice"),
                60, 70,
                "65° ± 5° · ideal clásico 65°; interpretar junto con FMA e IMPA",
                "Trace Frankfort Po-Or y el eje axial del incisivo inferior.",
                "FMIA por debajo del intervalo central de referencia; interpretar junto con FMA e IMPA.",
                "FMIA dentro del intervalo central 65° ± 5°.",
                "FMIA por encima del intervalo central de referencia; interpretar junto con FMA e IMPA.",
                true
        ));

        list.add(m(
                "IMPA",
                TWO_LINES,
                p("Go", "Me", "II borde", "II ápice"),
                85, 95,
                "90° ± 5° · referencia clásica",
                "Trace el plano mandibular Go-Me y el eje axial del incisivo inferior.",
                "Incisivo inferior relativamente retroinclinado respecto al plano mandibular.",
                "IMPA dentro de 90° ± 5°.",
                "Incisivo inferior relativamente proinclinado respecto al plano mandibular.",
                true
        ));

        return list;
    }

    /**
     * Módulo: Vía aérea superior.
     * Las medidas principales verificadas en esta auditoría son lineales y se encuentran
     * en LinearMeasurementCatalog.airway(). Se retiran los antiguos ángulos 126°/63°
     * procedentes de una tabla docente que no se pudo validar como umbral clínico.
     */
    public static List<MeasurementDefinition> airwayAngles() {
        return new ArrayList<>();
    }

    private static MeasurementDefinition m(
            String name,
            MeasurementDefinition.Type type,
            String[] labels,
            double min,
            double max,
            String norm,
            String instruction,
            String low,
            String normal,
            String high,
            boolean supplement
    ) {
        return new MeasurementDefinition(
                name,
                type,
                labels,
                min,
                max,
                norm,
                instruction,
                low,
                normal,
                high,
                supplement
        );
    }

    private static String[] p(String... values) {
        return values;
    }
}
