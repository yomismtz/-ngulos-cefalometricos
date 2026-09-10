package com.cefalo.angulos;

import java.util.ArrayList;
import java.util.List;
import static com.cefalo.angulos.MeasurementDefinition.Type.THREE_POINTS;
import static com.cefalo.angulos.MeasurementDefinition.Type.TWO_LINES;
import static com.cefalo.angulos.MeasurementDefinition.Type.SIGNED_ANB;

public final class MeasurementCatalog {
    private MeasurementCatalog() {}

    public static List<MeasurementDefinition> steiner() {
        List<MeasurementDefinition> list = new ArrayList<>();

        list.add(m(
                "SNA",
                THREE_POINTS,
                p("S","N","A"),
                80,84,
                "82° ± 2°",
                "Marque S, N y A. N es el vértice.",
                "Posición maxilar relativamente posterior respecto a la base craneal SN; corroborar con el resto del análisis.",
                "Dentro del rango de referencia de Steiner.",
                "Posición maxilar relativamente anterior respecto a la base craneal SN; corroborar con el resto del análisis.",
                false
        ));

        list.add(m(
                "SN / Frankfort (complementaria)",
                TWO_LINES,
                p("S","N","Po","Or"),
                4,10,
                "7° ± 3° · referencia complementaria",
                "Marque S-N y después Po-Or.",
                "Ángulo SN-Frankfort por debajo del rango de referencia; no define por sí solo el biotipo facial.",
                "Ángulo SN-Frankfort dentro del rango de referencia adoptado.",
                "Ángulo SN-Frankfort por encima del rango de referencia; no define por sí solo el biotipo facial.",
                true
        ));

        list.add(m(
                "Frankfort / plano palatino (complementaria)",
                TWO_LINES,
                p("Po","Or","ENA","ENP"),
                3,7,
                "5° ± 2° · referencia del protocolo aportado",
                "Marque Po-Or y después ENA-ENP.",
                "Valor por debajo del rango del protocolo; no diagnostica mordida abierta o profunda de forma aislada.",
                "Dentro del rango de referencia del protocolo.",
                "Valor por encima del rango del protocolo; no diagnostica mordida abierta o profunda de forma aislada.",
                true
        ));

        list.add(m(
                "SNB",
                THREE_POINTS,
                p("S","N","B"),
                78,82,
                "80° ± 2°",
                "Marque S, N y B. N es el vértice.",
                "Posición mandibular relativamente posterior respecto a la base craneal SN; corroborar con otras medidas.",
                "Dentro del rango de referencia de Steiner.",
                "Posición mandibular relativamente anterior respecto a la base craneal SN; corroborar con otras medidas.",
                false
        ));

        list.add(m(
                "SND",
                THREE_POINTS,
                p("S","N","D"),
                74,78,
                "76° ± 2°",
                "Marque S, N y D. N es el vértice.",
                "Mentón/sínfisis relativamente posterior respecto a la referencia; esta medida es complementaria.",
                "Dentro del rango de referencia.",
                "Mentón/sínfisis relativamente anterior respecto a la referencia; esta medida es complementaria.",
                false
        ));

        list.add(m(
                "Ángulo goníaco Ar-Go-Me",
                THREE_POINTS,
                p("Ar","Go","Me"),
                123,137,
                "123°–137° · referencia publicada",
                "Marque Ar, Go y Me. Go es el vértice.",
                "Ángulo goníaco disminuido; compatible con un patrón más hipodivergente, a corroborar con otros parámetros.",
                "Dentro del rango de referencia publicado.",
                "Ángulo goníaco aumentado; compatible con un patrón más hiperdivergente, a corroborar con otros parámetros.",
                false
        ));

        list.add(m(
                "Go-Gn / SN",
                TWO_LINES,
                p("Go","Gn","S","N"),
                27,37,
                "32° ± 5°",
                "Marque Go-Gn y después S-N.",
                "Ángulo disminuido; compatible con patrón mandibular más hipodivergente/rotación anterior. No determina la mordida por sí solo.",
                "Dentro del rango de referencia de Steiner.",
                "Ángulo aumentado; compatible con patrón mandibular más hiperdivergente/rotación posterior. No determina la mordida por sí solo.",
                true
        ));

        list.add(m(
                "ANB",
                SIGNED_ANB,
                p("S","N","A","B"),
                0,4,
                "2° ± 2°",
                "Marque A, N y B. N es el vértice.",
                "ANB por debajo del rango: compatible con tendencia esquelética Clase III; confirmar con otras medidas sagitales.",
                "ANB dentro del rango de referencia para relación esquelética Clase I.",
                "ANB por encima del rango: compatible con tendencia esquelética Clase II; confirmar con otras medidas sagitales.",
                false
        ));

        list.add(m(
                "AB / Go-Gn (complementaria)",
                TWO_LINES,
                p("A","B","Go","Gn"),
                72,76,
                "74° ± 2° · referencia del protocolo aportado",
                "Marque A-B y después Go-Gn.",
                "Valor por debajo del rango del protocolo; no diagnostica por sí solo una mordida abierta.",
                "Dentro del rango de referencia del protocolo.",
                "Valor por encima del rango del protocolo; no diagnostica por sí solo una mordida profunda.",
                true
        ));

        list.add(m(
                "IS / SN",
                TWO_LINES,
                p("IS borde","IS ápice","S","N"),
                99,107,
                "103° ± 4°",
                "Marque el eje del incisivo superior y después S-N.",
                "Incisivo superior relativamente retroinclinado respecto a SN.",
                "Dentro del rango de referencia.",
                "Incisivo superior relativamente proinclinado respecto a SN.",
                true
        ));

        list.add(m(
                "IS / NA (angular)",
                TWO_LINES,
                p("IS borde","IS ápice","N","A"),
                20,24,
                "22° ± 2°",
                "Marque el eje del incisivo superior y después N-A.",
                "Incisivo superior relativamente retroinclinado respecto a NA.",
                "Dentro del rango de referencia.",
                "Incisivo superior relativamente proinclinado respecto a NA.",
                true
        ));

        list.add(m(
                "II / NB (angular)",
                TWO_LINES,
                p("II borde","II ápice","N","B"),
                23,27,
                "25° ± 2°",
                "Marque el eje del incisivo inferior y después N-B.",
                "Incisivo inferior relativamente retroinclinado respecto a NB.",
                "Dentro del rango de referencia.",
                "Incisivo inferior relativamente proinclinado respecto a NB.",
                true
        ));

        list.add(m(
                "Plano oclusal / SN",
                TWO_LINES,
                p("Oclusal 1","Oclusal 2","S","N"),
                12,16,
                "14° ± 2°",
                "Marque dos puntos del plano oclusal y después S-N.",
                "Plano oclusal con inclinación menor que el rango de referencia.",
                "Dentro del rango de referencia.",
                "Plano oclusal con inclinación mayor que el rango de referencia.",
                true
        ));

        list.add(m(
                "Ángulo interincisal",
                TWO_LINES,
                p("IS borde","IS ápice","II borde","II ápice"),
                125,137,
                "131° ± 6°",
                "Marque el eje del incisivo superior y después el eje del incisivo inferior.",
                "Ángulo interincisal disminuido; mayor proinclinación relativa de los incisivos.",
                "Dentro del rango de referencia.",
                "Ángulo interincisal aumentado; mayor retroinclinación relativa de los incisivos.",
                true
        ));

        return list;
    }

    public static List<MeasurementDefinition> vertebral() {
        List<MeasurementDefinition> list = new ArrayList<>();

        list.add(m(
                "ANB",
                SIGNED_ANB,
                p("S","N","A","B"),
                0,4,
                "2° ± 2°",
                "Marque A, N y B. N es el vértice.",
                "Compatible con tendencia esquelética Clase III; confirmar con otras medidas sagitales.",
                "Dentro del rango de referencia para relación esquelética Clase I.",
                "Compatible con tendencia esquelética Clase II; confirmar con otras medidas sagitales.",
                false
        ));

        list.add(m(
                "SN / Go-Gn",
                TWO_LINES,
                p("S","N","Go","Gn"),
                27,37,
                "32° ± 5°",
                "Marque S-N y después Go-Gn.",
                "Ángulo disminuido; compatible con patrón mandibular más hipodivergente/rotación anterior.",
                "Dentro del rango de referencia.",
                "Ángulo aumentado; compatible con patrón mandibular más hiperdivergente/rotación posterior.",
                true
        ));

        list.add(m(
                "SN / Frankfort",
                TWO_LINES,
                p("S","N","Po","Or"),
                4,10,
                "7° ± 3° · referencia complementaria",
                "Marque S-N y después Po-Or.",
                "Valor por debajo del rango de referencia; describa la inclinación, sin diagnosticar postura por esta medida aislada.",
                "Dentro del rango de referencia adoptado.",
                "Valor por encima del rango de referencia; describa la inclinación, sin diagnosticar postura por esta medida aislada.",
                true
        ));

        list.add(m(
                "SN / CVT",
                TWO_LINES,
                p("S","N","CVT sup.","CVT inf."),
                96,102,
                "96°–102° · rango del protocolo",
                "Marque S-N y luego dos puntos de la tangente cervical CVT.",
                "Valor menor al rango del protocolo; interpretación postural orientativa y dependiente de la posición natural de la cabeza.",
                "Dentro del rango del protocolo; no implica normalidad clínica por sí solo.",
                "Valor mayor al rango del protocolo; interpretación postural orientativa y dependiente de la posición natural de la cabeza.",
                true
        ));

        list.add(m(
                "SN / OPT",
                TWO_LINES,
                p("S","N","OPT sup.","OPT inf."),
                94,100,
                "94°–100° · rango del protocolo",
                "Marque S-N y luego dos puntos de la tangente del proceso odontoideo OPT.",
                "Valor menor al rango del protocolo; interpretación postural orientativa.",
                "Dentro del rango del protocolo; no implica normalidad clínica por sí solo.",
                "Valor mayor al rango del protocolo; interpretación postural orientativa.",
                true
        ));

        list.add(m(
                "McGregor–C4",
                TWO_LINES,
                p("Occipital","ENP","C4-1","C4-2"),
                100,110,
                "100°–110° · referencia del protocolo aportado",
                "Use Occipital-ENP como plano de McGregor y después marque dos puntos que definan la referencia de C4.",
                "Valor por debajo del rango del protocolo. La evidencia externa para un umbral diagnóstico aislado es limitada.",
                "Dentro del rango del protocolo. No debe interpretarse como diagnóstico independiente.",
                "Valor por encima del rango del protocolo. La evidencia externa para un umbral diagnóstico aislado es limitada.",
                true
        ));

        list.add(m(
                "Ángulo posteroinferior (API) · McGregor / OP",
                TWO_LINES,
                p("Occipital","ENP","Odontoides ápice","C2 anteroinf."),
                96,106,
                "96°–106°",
                "Marque occipital y ENP para McGregor; después ápice de odontoides y punto anteroinferior de C2.",
                "Menor de 96°: rotación posterior del cráneo según la referencia de Rocabado; correlacionar clínicamente.",
                "Dentro del intervalo funcional de referencia de Rocabado.",
                "Mayor de 106°: rotación anterior del cráneo según la referencia de Rocabado; correlacionar clínicamente.",
                true
        ));

        return list;
    }

    public static List<MeasurementDefinition> powell() {
        List<MeasurementDefinition> list = new ArrayList<>();

        list.add(m(
                "Nasofrontal",
                THREE_POINTS,
                p("G'","N'","Pr"),
                115,130,
                "115°–130°",
                "Marque G', N' y Pr. N' es el vértice.",
                "Ángulo nasofrontal menor al rango de Powell.",
                "Dentro del rango estético de referencia de Powell.",
                "Ángulo nasofrontal mayor al rango de Powell.",
                false
        ));

        list.add(m(
                "Nasofacial",
                TWO_LINES,
                p("G'","Pg'","N'","Pr"),
                30,40,
                "30°–40°",
                "Marque el plano facial G'-Pg' y el eje nasal N'-Pr.",
                "Menor proyección nasal relativa al plano facial según esta medida.",
                "Dentro del rango estético de referencia de Powell.",
                "Mayor proyección nasal relativa al plano facial según esta medida.",
                true
        ));

        list.add(m(
                "Nasomental",
                THREE_POINTS,
                p("N'","Pr","Pg'"),
                120,132,
                "120°–132°",
                "Marque N', Pr y Pg'. Pr es el vértice.",
                "Ángulo nasomental menor al rango de Powell; interpretar la relación nariz-mentón en conjunto.",
                "Dentro del rango estético de referencia de Powell.",
                "Ángulo nasomental aumentado; puede reflejar mayor prominencia relativa del mentón o menor proyección nasal.",
                false
        ));

        list.add(m(
                "Mentocervical",
                TWO_LINES,
                p("G'","Pg'","Me'","C"),
                80,95,
                "80°–95° · algunas publicaciones citan 80°–85°",
                "Marque el plano facial G'-Pg' y la línea mentocervical Me'-C.",
                "Ángulo mentocervical menor al rango de Powell; valorar junto con el perfil facial completo.",
                "Dentro del rango estético de referencia de Powell.",
                "Ángulo mentocervical mayor al rango de Powell; valorar junto con el contorno submentoniano y el perfil facial.",
                true
        ));

        return list;
    }

    public static List<MeasurementDefinition> tweed() {
        List<MeasurementDefinition> list = new ArrayList<>();

        list.add(m(
                "FMA",
                TWO_LINES,
                p("Po","Or","Go","Me"),
                20,30,
                "25° ± 5° · rango histórico publicado 16°–35°",
                "Plano de Frankfort Po-Or con plano mandibular Go-Me.",
                "FMA menor al intervalo central 25° ± 5°; patrón mandibular relativamente hipodivergente.",
                "FMA dentro del intervalo central 25° ± 5°.",
                "FMA mayor al intervalo central 25° ± 5°; patrón mandibular relativamente hiperdivergente.",
                true
        ));

        list.add(m(
                "FMIA",
                TWO_LINES,
                p("Po","Or","II borde","II ápice"),
                60,75,
                "65° · rango histórico 60°–75°; Tweed lo relaciona con FMA",
                "Plano de Frankfort Po-Or con eje axial del incisivo inferior.",
                "FMIA por debajo del rango de referencia; interpretar junto con FMA e IMPA.",
                "FMIA dentro del rango de referencia publicado.",
                "FMIA por encima del rango de referencia; interpretar junto con FMA e IMPA.",
                true
        ));

        list.add(m(
                "IMPA",
                TWO_LINES,
                p("Go","Me","II borde","II ápice"),
                85,95,
                "90° ± 5°",
                "Plano mandibular Go-Me con eje axial del incisivo inferior.",
                "Incisivo inferior relativamente retroinclinado respecto al plano mandibular.",
                "IMPA dentro del rango clásico de referencia.",
                "Incisivo inferior relativamente proinclinado respecto al plano mandibular.",
                true
        ));

        return list;
    }

    public static List<MeasurementDefinition> airwayAngles() {
        List<MeasurementDefinition> list = new ArrayList<>();

        list.add(m(
                "Ba-S-NA",
                THREE_POINTS,
                p("Ba","S","N"),
                Double.NaN,
                Double.NaN,
                "Tabla docente aportada: 126° · sin umbral diagnóstico automático",
                "Marque Ba, S y N. S es el vértice.",
                "",
                "Medida del ángulo de la base craneal. La literatura muestra variación por edad, sexo y población; no permite clasificar por sí sola «buen» o «mal desarrollo» ni diagnosticar vía aérea.",
                "",
                false
        ));

        list.add(m(
                "Ba-S-ENP",
                THREE_POINTS,
                p("Ba","S","ENP"),
                Double.NaN,
                Double.NaN,
                "Tabla docente aportada: 63° · sin umbral diagnóstico automático",
                "Marque Ba, S y ENP. S es el vértice.",
                "",
                "Medida estructural cefalométrica. No se encontró evidencia suficiente para convertir 63° en un umbral diagnóstico de vía aérea adecuada/inadecuada; se muestra solo como referencia docente.",
                "",
                false
        ));

        return list;
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
