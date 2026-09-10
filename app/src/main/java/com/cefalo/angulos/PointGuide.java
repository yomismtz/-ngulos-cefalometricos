package com.cefalo.angulos;

import java.util.HashMap;
import java.util.Map;

public final class PointGuide {
    private static final Map<String, String> GUIDE = new HashMap<>();

    static {
        GUIDE.put("S", "Sella (S): centro geométrico de la silla turca.");
        GUIDE.put("N", "Nasion (N): punto más anterior de la sutura frontonasal en el plano medio.");
        GUIDE.put("A", "Punto A o subespinal: punto más profundo de la concavidad anterior del maxilar entre la espina nasal anterior y el proceso alveolar.");
        GUIDE.put("B", "Punto B o supramentale: punto más profundo de la concavidad anterior de la sínfisis mandibular, entre infradentale y pogonion.");
        GUIDE.put("D", "Punto D: centro geométrico de la sínfisis mandibular, utilizado en el análisis de Steiner.");
        GUIDE.put("Po", "Porion (Po): punto más superior del borde óseo del conducto auditivo externo.");
        GUIDE.put("Or", "Orbitale (Or): punto más inferior del reborde orbitario óseo.");
        GUIDE.put("ENA", "Espina nasal anterior (ENA/ANS): extremo anterior de la espina nasal anterior.");
        GUIDE.put("ENP", "Espina nasal posterior (ENP/PNS): extremo posterior del paladar duro.");
        GUIDE.put("Ar", "Articulare (Ar): punto construido en la intersección del borde posterior de la rama mandibular con la base craneal posterior.");
        GUIDE.put("Go", "Gonion (Go): punto construido sobre el ángulo mandibular, en la bisectriz formada por la tangente al borde posterior de la rama y la tangente al borde inferior del cuerpo mandibular.");
        GUIDE.put("Me", "Menton (Me): punto más inferior de la sínfisis mandibular.");
        GUIDE.put("Gn", "Gnathion (Gn): punto más anteroinferior del contorno óseo de la sínfisis mandibular; puede construirse entre pogonion y menton según el protocolo.");
        GUIDE.put("IS borde", "Borde incisal del incisivo superior: marque el borde incisal del incisivo central superior elegido para el trazado.");
        GUIDE.put("IS ápice", "Ápice del incisivo superior: marque el ápice radicular del mismo incisivo central superior utilizado para el borde incisal.");
        GUIDE.put("II borde", "Borde incisal del incisivo inferior: marque el borde incisal del incisivo central inferior elegido para el trazado.");
        GUIDE.put("II ápice", "Ápice del incisivo inferior: marque el ápice radicular del mismo incisivo central inferior utilizado para el borde incisal.");
        GUIDE.put("Oclusal 1", "Plano oclusal, punto anterior: marque un punto reproducible en la región anterior del plano oclusal funcional, siguiendo el protocolo del análisis utilizado.");
        GUIDE.put("Oclusal 2", "Plano oclusal, punto posterior: marque un segundo punto reproducible en la región posterior del mismo plano oclusal funcional.");
        GUIDE.put("CVT sup.", "CVT superior: punto superior de la tangente cervical posterior, sobre el contorno posterior de las vértebras cervicales altas definido por el protocolo postural utilizado.");
        GUIDE.put("CVT inf.", "CVT inferior: punto inferior de la misma tangente cervical posterior; debe pertenecer al mismo contorno usado para CVT superior.");
        GUIDE.put("OPT sup.", "OPT superior: punto superior de la tangente posterior del proceso odontoideo de C2.");
        GUIDE.put("OPT inf.", "OPT inferior: punto inferior de esa misma tangente posterior del proceso odontoideo de C2.");
        GUIDE.put("Occipital", "Punto occipital del plano de McGregor: punto más caudal del contorno occipital utilizado para unirlo con ENP/PNS y formar la línea de McGregor.");
        GUIDE.put("C4-1", "C4, punto 1: primer punto claramente identificable del borde de C4 empleado para construir la referencia de C4 del protocolo seleccionado.");
        GUIDE.put("C4-2", "C4, punto 2: segundo punto del mismo borde de C4 empleado para construir la referencia de C4. Ambos puntos deben definir una sola línea anatómica reproducible.");
        GUIDE.put("Odontoides ápice", "Ápice de la odontoides: punto más superior del proceso odontoideo de C2.");
        GUIDE.put("C2 anteroinf.", "C2 anteroinferior: ángulo anteroinferior del cuerpo del axis (C2).");
        GUIDE.put("C1 posterior", "C1 posterior: punto posterior del arco posterior del atlas utilizado para medir el espacio C0-C1 en el análisis de Rocabado.");
        GUIDE.put("C3", "C3: ángulo anteroinferior del cuerpo de la tercera vértebra cervical.");
        GUIDE.put("RGn", "RGn o retrognathion: punto más posteroinferior de la sínfisis mandibular utilizado en el triángulo hioideo.");
        GUIDE.put("H", "H o hyoidale: punto más anterosuperior del cuerpo del hueso hioides.");
        GUIDE.put("AA", "AA: punto más anterior del arco anterior del atlas (C1).");
        GUIDE.put("C2 post-sup.", "C2 posterosuperior: punto posterosuperior del proceso odontoideo/cuerpo de C2 usado para construir la tangente cervical del protocolo.");
        GUIDE.put("C7 post-inf.", "C7 posteroinferior: punto posteroinferior del cuerpo de C7 usado como extremo inferior de la tangente cervical.");
        GUIDE.put("Profundidad cervical", "Profundidad cervical: punto del contorno cervical posterior con mayor distancia perpendicular respecto a la tangente trazada entre C2 y C7.");
        GUIDE.put("G'", "Glabela de tejidos blandos (G'): punto más prominente de la frente en el perfil blando.");
        GUIDE.put("N'", "Nasion de tejidos blandos (N'): punto de máxima concavidad en la raíz nasal del perfil blando.");
        GUIDE.put("Pr", "Pronasale (Pr): punto más anterior de la punta de la nariz.");
        GUIDE.put("Pg'", "Pogonion de tejidos blandos (Pg'): punto más anterior del mentón blando.");
        GUIDE.put("Me'", "Menton de tejidos blandos (Me'): punto más inferior del contorno del mentón blando.");
        GUIDE.put("C", "Punto cervical (C): punto más profundo de la concavidad entre la región submandibular y el cuello en el perfil blando.");
        GUIDE.put("Ba", "Basion (Ba): punto medio del borde anterior del foramen magno.");
        GUIDE.put("AD1", "AD1: punto de la pared posterior de la nasofaringe donde intersecta la línea ENP/PNS-Ba. En trazados que usan el tejido adenoideo, corresponde al punto más prominente de la adenoides sobre esa línea.");
        GUIDE.put("AD2", "AD2: punto de la pared posterior de la nasofaringe sobre la línea que parte de ENP/PNS y es perpendicular a S-Ba; en trazados adenoideos se marca el punto más prominente del tejido adenoideo sobre esa dirección.");
        GUIDE.put("Uptp", "Uptp: punto anterior de referencia de la medición AD3. Debe identificarse sobre el contorno del paladar blando o región pterigomaxilar superior según el protocolo AD3 utilizado; no lo coloque por una tabla numérica. Si la fuente docente original define otra construcción, esa definición debe prevalecer.");
        GUIDE.put("Adenoides", "Adenoides: punto del contorno del tejido adenoideo que se utiliza como extremo posterior de la medición AD3; marque el punto anatómico sobre la masa adenoidea indicado por el protocolo, no un valor tomado de una tabla.");
        GUIDE.put("Faringe sup ant.", "Faringe superior anterior de McNamara: punto del contorno posterior del paladar blando desde el cual se obtiene la distancia mínima hacia la pared faríngea posterior.");
        GUIDE.put("Faringe sup post.", "Faringe superior posterior de McNamara: punto más cercano de la pared faríngea posterior al punto anterior de la vía aérea superior.");
        GUIDE.put("Faringe inf ant.", "Faringe inferior anterior de McNamara: punto donde el contorno posterior de la lengua cruza el borde inferior de la mandíbula; desde aquí se mide la distancia mínima a la pared faríngea posterior.");
        GUIDE.put("Faringe inf post.", "Faringe inferior posterior de McNamara: punto más cercano de la pared faríngea posterior a la altura del punto anterior inferior.");
        GUIDE.put("LM sup.", "Línea media maxilar superior de Levandoski: punto superior sobre la línea media vertical del maxilar, siguiendo el eje del tabique nasal visible en la panorámica.");
        GUIDE.put("LM inf.", "Línea media maxilar inferior de Levandoski: segundo punto sobre la misma línea media vertical maxilar para completar una recta que siga el tabique nasal.");
        GUIDE.put("LM mandibular", "Línea media mandibular: punto medio mandibular usado para comparar la coincidencia con la línea media maxilar; ubíquelo en la región de la sínfisis y la línea interincisiva mandibular según el trazado elegido.");
        GUIDE.put("Cd der.", "Condylion derecho (Cd): punto más superior de la cabeza condilar derecha.");
        GUIDE.put("Cd izq.", "Condylion izquierdo (Cd): punto más superior de la cabeza condilar izquierda.");
        GUIDE.put("Go der.", "Gonion derecho (Go): punto más externo del ángulo mandibular derecho, definido de manera reproducible.");
        GUIDE.put("Go izq.", "Gonion izquierdo (Go): punto más externo del ángulo mandibular izquierdo, definido de la misma forma que el lado derecho.");
        GUIDE.put("Kr der.", "Koronion/Coronoid derecho (Kr/Cor): punto más superior de la apófisis coronoides derecha.");
        GUIDE.put("Kr izq.", "Koronion/Coronoid izquierdo (Kr/Cor): punto más superior de la apófisis coronoides izquierda.");
        GUIDE.put("IC max der.", "Incisivo central maxilar derecho: punto de contacto/incisal usado por el trazado de Levandoski para comparar la distancia desde el cóndilo derecho con el lado contrario.");
        GUIDE.put("IC max izq.", "Incisivo central maxilar izquierdo: punto equivalente del lado izquierdo, usando exactamente el mismo criterio anatómico que a la derecha.");
        GUIDE.put("IC mand der.", "Incisivo central mandibular derecho: punto de contacto/incisal usado por el trazado de Levandoski para comparar la distancia desde el cóndilo derecho.");
        GUIDE.put("IC mand izq.", "Incisivo central mandibular izquierdo: punto equivalente del lado izquierdo, usando exactamente el mismo criterio anatómico que a la derecha.");
        GUIDE.put("Cuerpo Md der.", "Cuerpo mandibular derecho: punto de referencia elegido sobre el borde/cuerpo mandibular derecho para comparar su distancia perpendicular a la línea media; use el mismo nivel anatómico a ambos lados.");
        GUIDE.put("Cuerpo Md izq.", "Cuerpo mandibular izquierdo: punto homólogo al del lado derecho, al mismo nivel anatómico, para la comparación con la línea media.");
        GUIDE.put("M2 distal der.", "Segundo molar derecho: punto más distal del segundo molar derecho usado para comparar su distancia perpendicular a la línea media.");
        GUIDE.put("M2 distal izq.", "Segundo molar izquierdo: punto más distal del segundo molar izquierdo usado con el mismo criterio.");
        GUIDE.put("Rama ant der.", "Rama mandibular derecha, borde anterior: punto sobre el borde anterior de la rama al nivel definido para medir su ancho; use el mismo nivel vertical en ambos lados.");
        GUIDE.put("Rama post der.", "Rama mandibular derecha, borde posterior: punto sobre el borde posterior de la rama al mismo nivel que el punto anterior.");
        GUIDE.put("Rama ant izq.", "Rama mandibular izquierda, borde anterior: punto homólogo al derecho, al mismo nivel vertical.");
        GUIDE.put("Rama post izq.", "Rama mandibular izquierda, borde posterior: punto homólogo al derecho y al mismo nivel que el punto anterior izquierdo.");
    }

    private PointGuide() {}

    public static String description(String label) {
        String value = GUIDE.get(label);
        if (value != null) return value;
        return label + ": marque este punto anatómico según el protocolo cefalométrico específico del análisis que utiliza.";
    }
}
