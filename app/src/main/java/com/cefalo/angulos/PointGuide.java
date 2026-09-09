package com.cefalo.angulos;

import java.util.HashMap;
import java.util.Map;

public final class PointGuide {
    private static final Map<String, String> GUIDE = new HashMap<>();

    static {
        GUIDE.put("S", "Sella (S): centro geométrico de la silla turca.");
        GUIDE.put("N", "Nasion (N): punto más anterior de la sutura frontonasal.");
        GUIDE.put("A", "Punto A: punto más profundo de la concavidad anterior del maxilar, entre la espina nasal anterior y el proceso alveolar.");
        GUIDE.put("B", "Punto B: punto más profundo de la concavidad anterior de la sínfisis mandibular.");
        GUIDE.put("D", "Punto D: punto ubicado en el centro de la sínfisis mandibular, usado en el análisis de Steiner.");
        GUIDE.put("Po", "Porion (Po): punto más superior del borde del conducto auditivo externo.");
        GUIDE.put("Or", "Orbitale (Or): punto más inferior del reborde orbitario.");
        GUIDE.put("ENA", "Espina nasal anterior (ENA): extremo anterior de la espina nasal anterior.");
        GUIDE.put("ENP", "Espina nasal posterior (ENP): extremo posterior del paladar duro.");
        GUIDE.put("Ar", "Articulare (Ar): punto construido en la intersección del borde posterior de la rama mandibular con la base del cráneo.");
        GUIDE.put("Go", "Gonion (Go): punto del ángulo mandibular determinado por la zona posteroinferior de la mandíbula.");
        GUIDE.put("Me", "Menton (Me): punto más inferior de la sínfisis mandibular.");
        GUIDE.put("Gn", "Gnathion (Gn): punto más anteroinferior del contorno de la sínfisis mandibular.");
        GUIDE.put("IS borde", "Borde del incisivo superior: marque el borde incisal del incisivo central superior usado para el trazado.");
        GUIDE.put("IS ápice", "Ápice del incisivo superior: marque el ápice radicular del mismo incisivo central superior.");
        GUIDE.put("II borde", "Borde del incisivo inferior: marque el borde incisal del incisivo central inferior usado para el trazado.");
        GUIDE.put("II ápice", "Ápice del incisivo inferior: marque el ápice radicular del mismo incisivo central inferior.");
        GUIDE.put("Oclusal 1", "Plano oclusal, punto 1: elija un punto representativo del plano oclusal según su protocolo.");
        GUIDE.put("Oclusal 2", "Plano oclusal, punto 2: elija el segundo punto del mismo plano oclusal.");
        GUIDE.put("CVT sup.", "CVT superior: punto superior utilizado por su protocolo para construir la tangente cervical CVT.");
        GUIDE.put("CVT inf.", "CVT inferior: punto inferior utilizado por su protocolo para construir la tangente cervical CVT.");
        GUIDE.put("OPT sup.", "OPT superior: punto superior utilizado para construir la tangente del proceso odontoideo OPT.");
        GUIDE.put("OPT inf.", "OPT inferior: punto inferior utilizado para construir la tangente del proceso odontoideo OPT.");
        GUIDE.put("Occipital", "Occipital: punto de la base del occipital utilizado para formar el plano de McGregor.");
        GUIDE.put("C4-1", "C4-1: primer punto de referencia de C4 según el protocolo con el que trace McGregor–C4.");
        GUIDE.put("C4-2", "C4-2: segundo punto de referencia de C4 según el protocolo con el que trace McGregor–C4.");
        GUIDE.put("Odontoides ápice", "Ápice de la odontoides: punto más superior del proceso odontoideo de C2.");
        GUIDE.put("C2 anteroinf.", "C2 anteroinferior: ángulo/punto anteroinferior del cuerpo del axis (C2).");
        GUIDE.put("C1 posterior", "C1 posterior: marque el punto del arco posterior del atlas utilizado para la distancia C0-C1.");
        GUIDE.put("C3", "C3: ángulo más anteroinferior del cuerpo de la tercera vértebra cervical.");
        GUIDE.put("RGn", "RGn o retrognation: punto más posteroinferior de la sínfisis mandibular.");
        GUIDE.put("H", "H o hyoidale: punto más superior y anterior del cuerpo del hioides.");
        GUIDE.put("AA", "AA: punto más anterior del cuerpo del atlas.");
        GUIDE.put("C2 post-sup.", "C2 post-sup.: margen posterosuperior del ápice del proceso odontoides de la segunda vértebra cervical, usado para la tangente cervical.");
        GUIDE.put("C7 post-inf.", "C7 post-inf.: punto posteroinferior del cuerpo de la séptima vértebra cervical, usado para la tangente cervical.");
        GUIDE.put("Profundidad cervical", "Profundidad cervical: marque el punto de máxima profundidad de la curvatura cervical respecto a la tangente C2-C7.");
    }

    private PointGuide() {}

    public static String description(String label) {
        String value = GUIDE.get(label);
        if (value != null) return value;
        return label + ": marque este punto anatómico según el protocolo cefalométrico que utiliza.";
    }
}
