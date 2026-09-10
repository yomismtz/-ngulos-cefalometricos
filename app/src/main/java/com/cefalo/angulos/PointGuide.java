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
        GUIDE.put("Go", "Gonion (Go): punto construido en el ángulo mandibular, sobre la bisectriz entre la tangente al borde posterior de la rama y la tangente al borde inferior del cuerpo mandibular.");
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
        GUIDE.put("Occipital", "Occipital: punto más caudal de la curva occipital. Junto con ENP/PNS define la línea de McGregor.");
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
        GUIDE.put("G'", "Glabela de tejidos blandos: punto más prominente de la frente en el perfil.");
        GUIDE.put("N'", "Nasion de tejidos blandos: punto de mayor concavidad en la raíz nasal.");
        GUIDE.put("Pr", "Pronasale: punto más anterior y prominente de la punta de la nariz.");
        GUIDE.put("Pg'", "Pogonion de tejidos blandos: punto más anterior del mentón.");
        GUIDE.put("Me'", "Mentón de tejidos blandos: punto más inferior de la región mentoniana.");
        GUIDE.put("C", "Punto cervical: punto más profundo de la concavidad entre la región submandibular y el cuello.");
        GUIDE.put("Ba", "Basion (Ba): punto medio en el borde anterior del foramen magno.");
        GUIDE.put("AD1", "AD1: punto más cercano del tejido adenoideo sobre la línea ENP-Ba.");
        GUIDE.put("AD2", "AD2: punto más cercano del tejido adenoideo sobre una línea desde ENP perpendicular a S-Ba.");
        GUIDE.put("Uptp", "Uptp: punto de referencia superior utilizado en la medición AD3 de la tabla proporcionada.");
        GUIDE.put("Adenoides", "Adenoides: punto del tejido adenoideo usado para la medición AD3.");
        GUIDE.put("Faringe sup ant.", "Faringe superior anterior (McNamara): punto en el contorno posterior del paladar blando, aproximadamente a mitad de su longitud, desde donde se mide la distancia más corta a la pared faríngea posterior.");
        GUIDE.put("Faringe sup post.", "Faringe superior posterior (McNamara): punto de la pared faríngea posterior más cercano al punto anterior del paladar blando.");
        GUIDE.put("Faringe inf ant.", "Faringe inferior anterior (McNamara): intersección del borde posterior de la lengua con el borde inferior de la mandíbula.");
        GUIDE.put("Faringe inf post.", "Faringe inferior posterior (McNamara): punto más cercano de la pared faríngea posterior a la altura del punto anterior inferior.");
        GUIDE.put("LM sup.", "Levandoski: punto superior de la línea media maxilar, sobre el septum nasal.");
        GUIDE.put("LM inf.", "Levandoski: punto inferior de la línea media maxilar, sobre la referencia central inferior.");
        GUIDE.put("LM mandibular", "Levandoski: punto de la línea media mandibular para compararlo con la línea media maxilar.");
        GUIDE.put("Cd der.", "Condylion derecho: punto más superior del cóndilo mandibular derecho.");
        GUIDE.put("Cd izq.", "Condylion izquierdo: punto más superior del cóndilo mandibular izquierdo.");
        GUIDE.put("Go der.", "Gonion derecho: punto del ángulo mandibular derecho.");
        GUIDE.put("Go izq.", "Gonion izquierdo: punto del ángulo mandibular izquierdo.");
        GUIDE.put("Kr der.", "Koronion derecho: punto más superior de la apófisis coronoides derecha.");
        GUIDE.put("Kr izq.", "Koronion izquierdo: punto más superior de la apófisis coronoides izquierda.");
        GUIDE.put("IC max der.", "Punto del incisivo central maxilar del lado derecho usado en la línea comparativa de Levandoski.");
        GUIDE.put("IC max izq.", "Punto del incisivo central maxilar del lado izquierdo usado en la línea comparativa de Levandoski.");
        GUIDE.put("IC mand der.", "Punto del incisivo central mandibular del lado derecho usado en la línea comparativa de Levandoski.");
        GUIDE.put("IC mand izq.", "Punto del incisivo central mandibular del lado izquierdo usado en la línea comparativa de Levandoski.");
        GUIDE.put("Cuerpo Md der.", "Punto de referencia del cuerpo mandibular derecho para medir su distancia a la línea media.");
        GUIDE.put("Cuerpo Md izq.", "Punto de referencia del cuerpo mandibular izquierdo para medir su distancia a la línea media.");
        GUIDE.put("M2 distal der.", "Punto distal del segundo molar derecho para medir la distancia a la línea media.");
        GUIDE.put("M2 distal izq.", "Punto distal del segundo molar izquierdo para medir la distancia a la línea media.");
        GUIDE.put("Rama ant der.", "Punto del borde anterior de la rama mandibular derecha, usado para medir su ancho.");
        GUIDE.put("Rama post der.", "Punto del borde posterior de la rama mandibular derecha, usado para medir su ancho.");
        GUIDE.put("Rama ant izq.", "Punto del borde anterior de la rama mandibular izquierda, usado para medir su ancho.");
        GUIDE.put("Rama post izq.", "Punto del borde posterior de la rama mandibular izquierda, usado para medir su ancho.");
    }

    private PointGuide() {}

    public static String description(String label) {
        String value = GUIDE.get(label);
        if (value != null) return value;
        return label + ": marque este punto anatómico según el protocolo cefalométrico que utiliza.";
    }
}
