package com.cefalo.angulos;

import java.util.HashMap;
import java.util.Map;

/**
 * Landmark placement guide. Definitions are intentionally operational: they
 * describe a reproducible radiographic location rather than a diagnosis.
 */
public final class PointGuide {
    private static final Map<String, String> GUIDE = new HashMap<>();

    static {
        // Craniofacial hard-tissue landmarks.
        GUIDE.put("S", "Sella (S): centro geométrico de la fosa hipofisaria/silla turca.");
        GUIDE.put("N", "Nasion (N): punto más anterior de la sutura frontonasal en el plano medio.");
        GUIDE.put("A", "Punto A (subespinal): punto más profundo de la concavidad anterior del maxilar entre la espina nasal anterior y el reborde alveolar del incisivo superior.");
        GUIDE.put("B", "Punto B (supramental): punto más profundo de la concavidad anterior de la sínfisis mandibular entre el reborde alveolar inferior y el pogonion óseo.");
        GUIDE.put("D", "Punto D de Steiner: centro geométrico del cuerpo de la sínfisis mandibular; úselo como referencia interna de la sínfisis, no como punto del contorno.");
        GUIDE.put("Po", "Porion (Po): punto más superior del contorno radiográfico del conducto auditivo externo utilizado para construir el plano de Frankfort.");
        GUIDE.put("Or", "Orbitale (Or): punto más inferior del reborde orbitario.");
        GUIDE.put("ENA", "Espina nasal anterior (ENA/ANS): extremo más anterior de la espina nasal anterior.");
        GUIDE.put("ENP", "Espina nasal posterior (ENP/PNS): extremo más posterior del paladar duro, en la espina nasal posterior.");
        GUIDE.put("Ba", "Basion (Ba): punto más inferior y posterior del borde anterior del foramen magno, en el plano sagital medio.");
        GUIDE.put("Ar", "Articulare (Ar): punto construido en la intersección del borde posterior de la rama mandibular con el contorno inferior de la base craneal.");
        GUIDE.put("Go", "Gonion (Go): punto construido sobre el ángulo mandibular, en la bisectriz entre la tangente al borde posterior de la rama y la tangente al borde inferior del cuerpo mandibular.");
        GUIDE.put("Me", "Menton (Me): punto más inferior del contorno de la sínfisis mandibular.");
        GUIDE.put("Gn", "Gnathion (Gn): punto construido a mitad del arco entre Pogonion y Menton; corresponde a la región más anteroinferior de la sínfisis.");

        // Dental landmarks and Steiner occlusal plane.
        GUIDE.put("IS borde", "Incisivo superior, borde: centro del borde incisal del incisivo central superior que se está trazando.");
        GUIDE.put("IS ápice", "Incisivo superior, ápice: ápice radicular del mismo incisivo central superior usado para el borde incisal; ambos puntos forman su eje largo.");
        GUIDE.put("II borde", "Incisivo inferior, borde: centro del borde incisal del incisivo central inferior que se está trazando.");
        GUIDE.put("II ápice", "Incisivo inferior, ápice: ápice radicular del mismo incisivo central inferior; junto con el borde incisal forma su eje largo.");
        GUIDE.put("Oclusal 1", "Plano oclusal de Steiner, punto anterior: punto equidistante entre los bordes incisales superior e inferior (bisecte el espacio entre ambos incisivos en oclusión).");
        GUIDE.put("Oclusal 2", "Plano oclusal de Steiner, punto posterior: punto medio de la zona de intercuspidación/superposición de los primeros molares. Únalo con el punto anterior para construir el plano oclusal.");

        // Solow/Siersbæk-Nielsen cervical tangents.
        GUIDE.put("Cv2tg", "Cv2tg: punto de tangencia sobre el contorno dorsal de la apófisis odontoides de C2. Es el punto superior común usado por las tangentes OPT y CVT.");
        GUIDE.put("Cv2ip", "Cv2ip: punto más posteroinferior del cuerpo de C2. Junto con Cv2tg define la tangente OPT.");
        GUIDE.put("Cv4ip", "Cv4ip: punto más posteroinferior del cuerpo de C4. Junto con Cv2tg define la tangente CVT.");
        // Aliases retained only so older saved studies still show a useful guide.
        GUIDE.put("CVT sup.", "Referencia cervical histórica de la app. Use preferentemente Cv2tg: punto de tangencia dorsal de la odontoides de C2.");
        GUIDE.put("CVT inf.", "Referencia cervical histórica de la app. Use preferentemente Cv4ip: punto más posteroinferior del cuerpo de C4.");
        GUIDE.put("OPT sup.", "Referencia cervical histórica de la app. Use preferentemente Cv2tg: punto de tangencia dorsal de la odontoides de C2.");
        GUIDE.put("OPT inf.", "Referencia cervical histórica de la app. Use preferentemente Cv2ip: punto más posteroinferior del cuerpo de C2.");

        // Rocabado / hyoid triangle.
        GUIDE.put("Occipital", "C0 / referencia occipital de McGregor: punto del borde inferior del occipital usado como extremo posterior de la línea de McGregor; únalo con ENP.");
        GUIDE.put("C1 posterior", "C1 posterior: punto del arco posterior del atlas enfrentado al borde inferior del occipital para medir el espacio C0–C1.");
        GUIDE.put("Odontoides ápice", "Ápice de la odontoides: punto más superior del proceso odontoideo de C2.");
        GUIDE.put("C2 anteroinf.", "C2 anteroinferior: ángulo más anteroinferior del cuerpo del axis (C2); con el ápice odontoideo define la referencia odontoidea usada por el módulo Rocabado.");
        GUIDE.put("C3", "C3: ángulo más anteroinferior del cuerpo de la tercera vértebra cervical.");
        GUIDE.put("RGn", "RGn (retrognathion): punto más posteroinferior de la sínfisis mandibular.");
        GUIDE.put("H", "Hyoidale (H): punto más superior y anterior del cuerpo del hueso hioides.");
        GUIDE.put("AA", "AA: punto más anterior del cuerpo/arco anterior del atlas (C1) visible en la telerradiografía.");
        GUIDE.put("C2 post-sup.", "C2 posterosuperior: referencia posterosuperior de la odontoides/C2 utilizada como extremo superior de la tangente posterior C2–C7 para valorar profundidad cervical.");
        GUIDE.put("C7 post-inf.", "C7 posteroinferior: punto más posteroinferior del cuerpo de C7; constituye el extremo inferior de la tangente posterior C2–C7.");
        GUIDE.put("Profundidad cervical", "Profundidad cervical: punto de máxima concavidad posterior de la columna cervical, aproximadamente a nivel de C4; la app mide su distancia perpendicular a la tangente C2–C7.");

        // Powell soft tissue profile.
        GUIDE.put("G'", "Glabela de tejidos blandos (G'): punto más prominente de la frente en el perfil blando.");
        GUIDE.put("N'", "Nasion de tejidos blandos (N'): punto de mayor concavidad en la raíz nasal del perfil blando.");
        GUIDE.put("Pr", "Pronasale (Pr): punto más anterior y prominente de la punta de la nariz.");
        GUIDE.put("Pg'", "Pogonion de tejidos blandos (Pg'): punto más anterior del contorno blando del mentón.");
        GUIDE.put("Me'", "Menton de tejidos blandos (Me'): punto más inferior del contorno blando del mentón.");
        GUIDE.put("C", "Punto cervical (C): punto más profundo de la concavidad entre la región submandibular y el cuello.");

        // Adenoid / airway landmarks. Adopted convention: PNS/ENP as anterior anchor.
        GUIDE.put("AD1", "AD1: punto del tejido adenoideo/pared faríngea posterior que intersecta la línea ENP–Ba. Para PNS–AD1 seleccione el punto más cercano a ENP sobre esa misma línea.");
        GUIDE.put("AD2", "AD2: punto del tejido adenoideo/pared faríngea posterior intersectado por una línea que pasa por ENP y es perpendicular a S–Ba. Seleccione el punto más cercano a ENP sobre esa perpendicular.");
        GUIDE.put("Faringe sup ant.", "Faringe superior anterior de McNamara: punto en el contorno posterior del paladar blando desde el que se obtiene la distancia mínima hacia la pared faríngea posterior.");
        GUIDE.put("Faringe sup post.", "Faringe superior posterior de McNamara: punto de la pared faríngea posterior más cercano al punto anterior del paladar blando; la medida debe ser la distancia mínima.");
        GUIDE.put("Faringe inf ant.", "Faringe inferior anterior de McNamara: punto donde el contorno posterior de la lengua cruza el borde inferior de la mandíbula.");
        GUIDE.put("Faringe inf post.", "Faringe inferior posterior de McNamara: punto más cercano de la pared faríngea posterior al punto anterior inferior; mida la distancia mínima.");

        // Levandoski panoramic analysis.
        GUIDE.put("LM sup.", "Levandoski, línea 1: marque un punto superior sobre la línea media vertical maxilar que atraviesa el septum nasal. No use una desviación mandibular para definir esta línea.");
        GUIDE.put("LM inf.", "Levandoski, línea 1: marque un segundo punto, bien separado del primero, sobre la misma línea media vertical maxilar/septal para construir la línea 1.");
        GUIDE.put("LM mandibular", "Línea media mandibular: punto medio de la sínfisis mandibular; puede compararse visualmente con la línea media maxilar, pero no redefine la línea 1 de Levandoski.");
        GUIDE.put("Cd der.", "Condylion derecho (Cd): punto más superior de la cabeza condilar derecha en la panorámica.");
        GUIDE.put("Cd izq.", "Condylion izquierdo (Cd): punto más superior de la cabeza condilar izquierda en la panorámica.");
        GUIDE.put("Go der.", "Gonion derecho (Go): punto del ángulo mandibular derecho definido de forma equivalente al lado contralateral.");
        GUIDE.put("Go izq.", "Gonion izquierdo (Go): punto del ángulo mandibular izquierdo definido de forma equivalente al lado contralateral.");
        GUIDE.put("Kr der.", "Koronion derecho (Kr/Cor): punto más superior de la punta de la apófisis coronoides derecha.");
        GUIDE.put("Kr izq.", "Koronion izquierdo (Kr/Cor): punto más superior de la punta de la apófisis coronoides izquierda.");
        GUIDE.put("IC max der.", "Incisivo central maxilar derecho: centro del borde incisal del incisivo central derecho, usando el mismo criterio en ambos lados.");
        GUIDE.put("IC max izq.", "Incisivo central maxilar izquierdo: centro del borde incisal del incisivo central izquierdo, usando el mismo criterio en ambos lados.");
        GUIDE.put("IC mand der.", "Incisivo central mandibular derecho: centro del borde incisal del incisivo central derecho, usando el mismo criterio en ambos lados.");
        GUIDE.put("IC mand izq.", "Incisivo central mandibular izquierdo: centro del borde incisal del incisivo central izquierdo, usando el mismo criterio en ambos lados.");
        GUIDE.put("Cuerpo Md der.", "Cuerpo mandibular derecho: seleccione el mismo punto anatómico reproducible del borde corporal que usará en el lado izquierdo y a una altura comparable; esta es una comparación derecha/izquierda.");
        GUIDE.put("Cuerpo Md izq.", "Cuerpo mandibular izquierdo: seleccione el punto homólogo al marcado en el lado derecho y a una altura comparable; esta es una comparación derecha/izquierda.");
        GUIDE.put("M2 distal der.", "Segundo molar derecho: punto más distal de la corona del segundo molar usado para la comparación con la línea media.");
        GUIDE.put("M2 distal izq.", "Segundo molar izquierdo: punto más distal de la corona del segundo molar usado para la comparación con la línea media.");
        GUIDE.put("Rama ant der.", "Rama derecha, borde anterior: punto del borde anterior elegido al mismo nivel vertical que el punto posterior para medir el ancho de la rama.");
        GUIDE.put("Rama post der.", "Rama derecha, borde posterior: punto del borde posterior a la misma altura que el punto anterior.");
        GUIDE.put("Rama ant izq.", "Rama izquierda, borde anterior: punto homólogo al derecho y al mismo nivel vertical que el punto posterior.");
        GUIDE.put("Rama post izq.", "Rama izquierda, borde posterior: punto homólogo al derecho y a la misma altura que el punto anterior.");
    }

    private PointGuide() {}

    public static String description(String label) {
        String value = GUIDE.get(label);
        if (value != null) return value;
        return label + ": no hay una definición validada cargada para este rótulo. Revise la guía del análisis antes de marcarlo.";
    }
}
