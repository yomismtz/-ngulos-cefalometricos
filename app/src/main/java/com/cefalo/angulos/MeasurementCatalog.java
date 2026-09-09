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
        list.add(m("McGregor–C4", TWO_LINES, p("McGregor 1","McGregor 2","C4-1","C4-2"),100,110,"100°–110°","Marque el plano de McGregor y luego la línea hacia C4 según su protocolo.","Flexión / tendencia a rectificación cervical","Relación equilibrada cráneo-columna cervical","Extensión craneocervical / incremento de lordosis",true));
        list.add(m("Plano de McGregor / proceso odontoideo", TWO_LINES, p("Occipital","ENP","Odontoides ápice","C2 anteroinf."),96,106,"96°–106°","Marque occipital y ENP para McGregor; después ápice de odontoides y punto anteroinferior de C2.","Flexión craneocervical / cabeza hacia adelante","Relación adecuada entre cráneo y C2","Extensión craneocervical / cabeza hacia atrás",true));
        return list;
    }

    private static MeasurementDefinition m(String name, MeasurementDefinition.Type type, String[] labels,
        double min, double max, String norm, String instruction,
        String low, String normal, String high, boolean supplement) {
        return new MeasurementDefinition(name,type,labels,min,max,norm,instruction,low,normal,high,supplement);
    }
    private static String[] p(String... values){ return values; }
}
