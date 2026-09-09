package com.cefalo.angulos;

import java.util.ArrayList;
import java.util.List;
import static com.cefalo.angulos.MeasurementDefinition.Type.THREE_POINTS;
import static com.cefalo.angulos.MeasurementDefinition.Type.TWO_LINES;

public final class MeasurementCatalog {
    private MeasurementCatalog() {}

    public static List<MeasurementDefinition> steiner() {
        List<MeasurementDefinition> list = new ArrayList<>();
        list.add(m("SNA", THREE_POINTS, p("S","N","A"),80,84,"82° ± 2°","Marque S, luego N y luego A. N es el vértice.","Retrognatismo maxilar","Posición maxilar normal","Prognatismo maxilar",false));
        list.add(m("S-N / Po-Or", TWO_LINES, p("S","N","Po","Or"),4,10,"7° ± 3°","Marque S-N y después Po-Or.","Tendencia a patrón horizontal o braquifacial","Relación craneal normal con Frankfort","Tendencia a patrón vertical o dolicofacial",true));
        list.add(m("Po-Or / ENA-ENP", TWO_LINES, p("Po","Or","ENA","ENP"),3,7,"5° ± 2°","Marque Po-Or y después ENA-ENP (plano palatino).","Tendencia a mordida abierta o rotación posterior del maxilar","Relación normal Frankfort-plano palatino","Tendencia a mordida profunda o rotación anterior del maxilar",true));
        list.add(m("SNB", THREE_POINTS, p("S","N","B"),78,82,"80° ± 2°","Marque S, N y B. N es el vértice.","Retrognatismo mandibular","Mandíbula en posición normal","Prognatismo mandibular",false));
        list.add(m("SND", THREE_POINTS, p("S","N","D"),74,78,"76° ± 2°","Marque S, N y D. N es el vértice.","Retrognatismo de la sínfisis mandibular","Sínfisis en posición normal","Prognatismo de la sínfisis mandibular",false));
        list.add(m("Ángulo goníaco Ar-Go-Me", THREE_POINTS, p("Ar","Go","Me"),123,127,"125° ± 2°","Marque Ar, Go y Me. Go es el vértice.","Crecimiento horizontal / rotación antihoraria","Mesofacial","Crecimiento vertical / rotación horaria",false));
        list.add(m("Go-Gn / SN", TWO_LINES, p("Go","Gn","S","N"),27,37,"32° ± 5°","Marque Go-Gn y después S-N.","Patrón horizontal / rotación antihoraria / tendencia a mordida profunda","Mesofacial","Patrón vertical / rotación horaria / tendencia a mordida abierta",true));
        list.add(m("ANB", THREE_POINTS, p("A","N","B"),1,3,"2° ± 1°","Marque A, N y B. N es el vértice.","Clase III","Clase I","Clase II",false));
        list.add(m("AB / Go-Gn", TWO_LINES, p("A","B","Go","Gn"),72,76,"74° ± 2°","Marque A-B y después Go-Gn.","Tendencia a mordida abierta","Relación vertical normal","Tendencia a mordida profunda",true));
        list.add(m("IS / SN", TWO_LINES, p("IS borde","IS ápice","S","N"),102,106,"104° ± 2°","Marque el eje del incisivo superior y después S-N.","Retroinclinación","Incisivo superior en norma","Proinclinación",true));
        list.add(m("IS / NA (angular)", TWO_LINES, p("IS borde","IS ápice","N","A"),20,24,"22° ± 2°","Marque el eje del incisivo superior y después N-A.","Palatinización","Incisivo superior en norma","Vestibularización",true));
        list.add(m("II / NB (angular)", TWO_LINES, p("II borde","II ápice","N","B"),24,26,"25° ± 1°","Marque el eje del incisivo inferior y después N-B.","Lingualización","Incisivo inferior en norma","Vestibularización",true));
        list.add(m("Plano oclusal / SN", TWO_LINES, p("Oclusal 1","Oclusal 2","S","N"),13,15,"14° ± 1°","Marque dos puntos del plano oclusal y después S-N.","Plano oclusal cerrado","Inclinación normal","Plano oclusal abierto",true));
        list.add(m("Ángulo interincisal", TWO_LINES, p("IS borde","IS ápice","II borde","II ápice"),131,139,"135° ± 4°","Marque el eje del incisivo superior y después el eje del incisivo inferior.","Tendencia a mordida abierta","Relación incisiva normal","Tendencia a mordida profunda",true));
        return list;
    }

    public static List<MeasurementDefinition> vertebral() {
        List<MeasurementDefinition> list = new ArrayList<>();
        list.add(m("ANB", THREE_POINTS, p("A","N","B"),0,4,"2° ± 2°","Marque A, N y B. N es el vértice.","Tendencia a Clase III esqueletal","Relación Clase I esqueletal","Tendencia a Clase II esqueletal",false));
        list.add(m("SN / Go-Gn", TWO_LINES, p("S","N","Go","Gn"),27,37,"32° ± 5°","Marque S-N y después Go-Gn.","Patrón horizontal / rotación anterior","Equilibrio vertical y sagital","Patrón vertical / rotación posterior",true));
        list.add(m("SN / Po-Or", TWO_LINES, p("S","N","Po","Or"),6,10,"6°–10°","Marque S-N y después Po-Or.","Protracción cefálica","Orientación craneal equilibrada","Extensión de la cabeza",true));
        list.add(m("SN / CVT", TWO_LINES, p("S","N","CVT sup.","CVT inf."),96,102,"96°–102°","Marque S-N y luego dos puntos de la tangente cervical CVT.","Flexión de cabeza / protracción cefálica","Relación equilibrada cráneo-columna cervical","Extensión de cabeza / tendencia a patrón vertical",true));
        list.add(m("SN / OPT", TWO_LINES, p("S","N","OPT sup.","OPT inf."),94,100,"94°–100°","Marque S-N y luego dos puntos de la tangente del proceso odontoideo OPT.","Flexión de cabeza / protracción cefálica","Relación equilibrada cráneo-columna cervical","Extensión de cabeza / rotación mandibular posterior",true));
        list.add(m("McGregor–C4", TWO_LINES, p("Occipital","ENP","C4-1","C4-2"),100,110,"100°–110°","Use Occipital-ENP como plano de McGregor y después marque dos puntos que definan la referencia de C4.","Flexión / tendencia a rectificación cervical","Relación equilibrada cráneo-columna cervical","Extensión craneocervical / incremento de lordosis",true));
        list.add(m("Ángulo posteroinferior (API) · McGregor / OP", TWO_LINES, p("Occipital","ENP","Odontoides ápice","C2 anteroinf."),96,106,"96°–106°","Marque occipital y ENP para McGregor; después ápice de odontoides y punto anteroinferior de C2.","Flexión craneocervical / cabeza hacia adelante","Relación adecuada entre cráneo y C2","Extensión craneocervical / cabeza hacia atrás",true));
        return list;
    }


    public static List<MeasurementDefinition> powell() {
        List<MeasurementDefinition> list = new ArrayList<>();

        list.add(m(
                "Nasofrontal",
                THREE_POINTS,
                p("G'","N'","Pr"),
                115,130,
                "115°-130°",
                "Marque G', N' y Pr. N' es el vértice.",
                "Transición frente-raíz nasal más marcada / región nasofrontal más angulada",
                "Relación armónica entre frente y raíz nasal",
                "Transición frente-raíz nasal más abierta o menos marcada",
                false
        ));

        list.add(m(
                "Nasofacial",
                TWO_LINES,
                p("G'","Pg'","N'","Pr"),
                30,40,
                "30°-40°",
                "Marque el plano facial G'-Pg' y el eje nasal N'-Pr.",
                "Menor proyección nasal relativa al plano facial",
                "Relación equilibrada entre proyección nasal y plano facial",
                "Mayor proyección nasal relativa al plano facial",
                true
        ));

        list.add(m(
                "Nasomental",
                THREE_POINTS,
                p("N'","Pr","Pg'"),
                120,132,
                "120°-132°",
                "Marque N', Pr y Pg'. Pr es el vértice.",
                "Puede asociarse a mayor proyección nasal relativa o menor proyección anterior del mentón",
                "Relación proporcional entre proyección nasal y mentoniana",
                "Puede asociarse a menor proyección nasal relativa o mayor prominencia del mentón",
                false
        ));

        list.add(m(
                "Mentocervical",
                TWO_LINES,
                p("G'","Pg'","Me'","C"),
                80,95,
                "80°-95°",
                "Marque el plano facial G'-Pg' y la línea mentocervical Me'-C.",
                "Ángulo mentocervical disminuido",
                "Relación equilibrada entre mentón y región cervical",
                "Ángulo mentocervical aumentado",
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
                21,29,
                "25° ± 4°",
                "Plano de Frankfort Po-Or con plano mandibular Go-Me.",
                "FMA disminuido",
                "FMA dentro del rango ideal",
                "FMA aumentado",
                true
        ));

        list.add(m(
                "FMIA",
                TWO_LINES,
                p("Po","Or","II borde","II ápice"),
                65,65,
                "Objetivo 65°",
                "Plano de Frankfort Po-Or con eje axial del incisivo inferior.",
                "FMIA por debajo de 65°",
                "FMIA de 65°",
                "FMIA por encima de 65°",
                true
        ));

        list.add(m(
                "IMPA",
                TWO_LINES,
                p("Go","Me","II borde","II ápice"),
                90,90,
                "Objetivo 90°",
                "Plano mandibular Go-Me con eje axial del incisivo inferior.",
                "Incisivo inferior relativamente retroinclinado",
                "IMPA de 90°",
                "Incisivo inferior relativamente proinclinado",
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
                126,126,
                "126°",
                "Marque Ba, S y N. S es el vértice.",
                "Mal desarrollo respecto a la referencia de la tabla",
                "Valor de referencia",
                "Buen desarrollo respecto a la referencia de la tabla",
                false
        ));

        list.add(m(
                "Ba-S-ENP",
                THREE_POINTS,
                p("Ba","S","ENP"),
                63,63,
                "63°",
                "Marque Ba, S y ENP. S es el vértice.",
                "Vía aérea estructuralmente inadecuada respecto a la referencia",
                "Valor de referencia",
                "Vía aérea estructuralmente adecuada respecto a la referencia",
                false
        ));

        return list;
    }

    private static MeasurementDefinition m(String name, MeasurementDefinition.Type type, String[] labels,
        double min, double max, String norm, String instruction,
        String low, String normal, String high, boolean supplement) {
        return new MeasurementDefinition(name,type,labels,min,max,norm,instruction,low,normal,high,supplement);
    }
    private static String[] p(String... values){ return values; }
}
