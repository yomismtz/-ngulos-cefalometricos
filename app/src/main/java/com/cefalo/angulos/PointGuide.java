package com.cefalo.angulos;

import java.util.HashMap;
import java.util.Map;

public final class PointGuide {
    private static final Map<String, String> GUIDE = new HashMap<>();

    static {
        // Cefalometría ósea y dental
        GUIDE.put("S", "Sella (S): centro geométrico de la silla turca.");
        GUIDE.put("N", "Nasion (N): punto más anterior de la sutura frontonasal en el plano medio.");
        GUIDE.put("A", "Punto A o subespinal: punto más profundo de la concavidad anterior del maxilar entre la espina nasal anterior y el proceso alveolar.");
        GUIDE.put("B", "Punto B o supramentale: punto más profundo de la concavidad anterior de la sínfisis mandibular, entre infradentale y pogonion.");
        GUIDE.put("D", "Punto D: centro geométrico de la sínfisis mandibular; es un punto construido, no un accidente anatómico superficial.");
        GUIDE.put("Pg", "Pogonion óseo (Pg): punto más anterior del contorno óseo de la sínfisis mandibular. Para SL el software proyecta Pg perpendicularmente sobre SN; no debe marcarse un punto L adicional.");
        GUIDE.put("Cóndilo posterior", "Punto condilar posterior para SE: punto más posterior del contorno de la cabeza condilar visible. El software proyecta este punto perpendicularmente sobre SN para construir E; no debe marcarse E manualmente.");
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
        GUIDE.put("Oclusal 1", "Plano oclusal, punto anterior: ubique el punto medio de la sobremordida en la región incisiva cuando sea visible; use el mismo criterio de construcción del plano oclusal seleccionado.");
        GUIDE.put("Oclusal 2", "Plano oclusal, punto posterior: ubique el punto medio de la intercuspidación de los primeros molares permanentes o la referencia posterior definida por el protocolo. Debe formar con Oclusal 1 un único plano reproducible.");

        // Postura cráneo-cervical
        GUIDE.put("Occipital", "Punto occipital para el plano de McGregor: punto más inferior de la escama/base occipital visible. Únalo con ENP/PNS para formar el plano de McGregor.");
        GUIDE.put("Odontoides ápice", "Ápice de la odontoides: punto más superior del proceso odontoideo de C2.");
        GUIDE.put("C2 anteroinf.", "C2 anteroinferior: ángulo anteroinferior del cuerpo del axis (C2). Junto con el ápice de la odontoides puede definir el plano odontoideo usado en la evaluación cráneo-cervical de Rocabado.");
        GUIDE.put("C1 sup. posterior", "C1 superior/posterior: punto más superior y posterior del arco posterior del atlas. Se utiliza para medir perpendicularmente el espacio C0-C1 respecto al plano de McGregor.");
        GUIDE.put("C1 inf. posterior", "C1 inferior/posterior: punto más inferior y posterior del arco posterior del atlas. Es el extremo superior de la medición C1-C2.");
        GUIDE.put("C2 espinosa sup. posterior", "C2 apófisis espinosa superior/posterior: punto más superior y posterior de la apófisis espinosa del axis. Es el extremo inferior de la medición C1-C2.");
        GUIDE.put("C1 posterior", "C1 posterior (etiqueta heredada): si la medición requiere C0-C1 use el punto más superior y posterior del arco posterior del atlas. Las versiones nuevas del trazado separan C1 sup. posterior y C1 inf. posterior para evitar ambigüedad.");
        GUIDE.put("C3", "C3: ángulo más anteroinferior del cuerpo de la tercera vértebra cervical. Se utiliza, entre otras medidas, en el triángulo hioideo C3-RGn-H.");
        GUIDE.put("RGn", "RGn o retrognathion: punto más posteroinferior de la sínfisis mandibular utilizado en el triángulo hioideo.");
        GUIDE.put("H", "H o hyoidale: punto más superior y anterior del cuerpo del hueso hioides.");
        GUIDE.put("AA", "AA: punto más anterior del arco anterior del atlas (C1).");

        GUIDE.put("CV2tg", "CV2tg: punto de tangencia en el extremo superoposterior del proceso odontoideo de C2. Es el punto superior común de las líneas OPT y CVT en la nomenclatura de Solow/Tallgren.");
        GUIDE.put("CV2ip", "CV2ip: punto más inferior y posterior del cuerpo de C2. Junto con CV2tg forma la línea OPT.");
        GUIDE.put("CV4ip", "CV4ip: punto más inferior y posterior del cuerpo de C4. Junto con CV2tg forma la línea CVT; también puede servir como punto superior de la línea EVT.");
        GUIDE.put("CV6ip", "CV6ip: punto más inferior y posterior del cuerpo de C6. Junto con CV4ip forma la línea EVT para describir la curvatura cervical inferior.");
        GUIDE.put("CVT sup.", "CVT superior (etiqueta heredada): corresponde a CV2tg, punto de tangencia superoposterior de la odontoides de C2.");
        GUIDE.put("CVT inf.", "CVT inferior (etiqueta heredada): corresponde a CV4ip, punto más inferoposterior del cuerpo de C4.");
        GUIDE.put("OPT sup.", "OPT superior (etiqueta heredada): corresponde a CV2tg, punto de tangencia superoposterior de la odontoides de C2.");
        GUIDE.put("OPT inf.", "OPT inferior (etiqueta heredada): corresponde a CV2ip, punto más inferoposterior del cuerpo de C2.");

        GUIDE.put("C2 post-sup.", "C2 posterosuperior para Penning: punto del margen posterosuperior del proceso odontoideo de C2 desde el que se traza la tangente posterior hacia C7.");
        GUIDE.put("C7 post-inf.", "C7 posteroinferior para Penning: punto más posterior e inferior del cuerpo de C7; es el extremo inferior de la tangente usada para valorar la profundidad cervical.");
        GUIDE.put("Profundidad cervical", "Punto de profundidad cervical en C4: ubique el contorno posterior de C4 al nivel donde se trazará una perpendicular a la tangente C2-C7. La longitud firmada de esa perpendicular se usa para clasificar la curva de Penning: negativa = cifótica/invertida; 0 a <8 mm = rectificada; 8-12 mm = intervalo fisiológico; >12 mm = lordosis aumentada.");

        // Compatibilidad con un trazado antiguo que no debe volver a presentarse como medida validada
        GUIDE.put("C4-1", "C4-1 (etiqueta heredada): no utilice este punto para una medición automática denominada McGregor-C4 sin una fuente que defina su construcción. Las versiones nuevas usan CV4ip cuando corresponde.");
        GUIDE.put("C4-2", "C4-2 (etiqueta heredada): no utilice este punto para una medición automática denominada McGregor-C4 sin una fuente que defina su construcción. Las versiones nuevas usan landmarks cervicales explícitos.");

        // Perfil blando
        GUIDE.put("G'", "Glabela de tejidos blandos (G'): punto más prominente de la frente en el perfil blando.");
        GUIDE.put("N'", "Nasion de tejidos blandos (N'): punto de máxima concavidad en la raíz nasal del perfil blando.");
        GUIDE.put("Pr", "Pronasale (Pr): punto más anterior de la punta de la nariz.");
        GUIDE.put("Pg'", "Pogonion de tejidos blandos (Pg'): punto más anterior del mentón blando.");
        GUIDE.put("Me'", "Menton de tejidos blandos (Me'): punto más inferior del contorno del mentón blando.");
        GUIDE.put("C", "Punto cervical (C): punto más profundo de la concavidad entre la región submandibular y el cuello en el perfil blando.");

        // Vía aérea superior y adenoides
        GUIDE.put("Ba", "Basion (Ba): punto medio del borde anterior del foramen magno.");
        GUIDE.put("AD1", "AD1: punto más prominente del tejido adenoideo o de la pared faríngea posterior sobre la línea que une ENP/PNS con Basion. Se mide ENP-AD1 siguiendo esa misma dirección.");
        GUIDE.put("AD2", "AD2: punto más prominente del tejido adenoideo o de la pared faríngea posterior sobre la línea que parte de ENP/PNS y es perpendicular a S-Ba.");
        GUIDE.put("tu", "tu: punto más posterosuperior de la tuberosidad maxilar; en la nomenclatura de Solow se describe también como el punto más profundo del contorno anterior de la fosa/fisura pterigopalatina. Utilice una imagen donde esta referencia sea identificable.");
        GUIDE.put("AD3", "ad3: punto del tejido adenoideo o pared faríngea dorsal más cercano a tu en el protocolo de Solow. La medición tu-ad3 es la distancia mínima entre ambos puntos.");
        GUIDE.put("Uptp", "Uptp (etiqueta heredada): no se considera una nomenclatura universal reproducible para AD3. Las versiones nuevas de YomCeph utilizan tu y ad3 con definición anatómica explícita.");
        GUIDE.put("Adenoides", "Adenoides (etiqueta heredada): utilice AD1, AD2 o AD3 según la construcción concreta. No marque un punto genérico de 'adenoides' sin especificar el plano o la distancia que se va a medir.");
        GUIDE.put("P", "P o extremo del paladar blando: punto más distal/inferior de la úvula o extremo libre del paladar blando utilizado para medir la longitud PNS-P. Mantenga el mismo criterio anatómico en estudios comparativos.");
        GUIDE.put("Faringe sup ant.", "Faringe superior anterior de McNamara: punto del contorno posterior del paladar blando desde el cual se obtiene la menor distancia hacia la pared faríngea posterior.");
        GUIDE.put("Faringe sup post.", "Faringe superior posterior de McNamara: punto más cercano de la pared faríngea posterior al punto anterior de la vía aérea superior.");
        GUIDE.put("Faringe inf ant.", "Faringe inferior anterior de McNamara: punto donde el contorno posterior de la lengua cruza el borde inferior de la mandíbula; desde aquí se obtiene la menor distancia a la pared faríngea posterior.");
        GUIDE.put("Faringe inf post.", "Faringe inferior posterior de McNamara: punto más cercano de la pared faríngea posterior a la altura del punto anterior inferior.");
        GUIDE.put("PAS ant.", "PAS anterior: punto de la base/posterior de la lengua sobre la dirección usada para medir el espacio aéreo posterior hacia la pared faríngea. La construcción exacta debe permanecer vinculada al protocolo elegido.");
        GUIDE.put("PAS post.", "PAS posterior: punto correspondiente de la pared faríngea posterior sobre la misma dirección que PAS anterior.");

        // Panorámica / simetría
        GUIDE.put("LM sup.", "Línea media maxilar superior: punto superior sobre una línea media vertical del maxilar que siga el tabique nasal visible en la panorámica.");
        GUIDE.put("LM inf.", "Línea media maxilar inferior: segundo punto sobre la misma línea media vertical maxilar para completar una recta reproducible.");
        GUIDE.put("LM mandibular", "Línea media mandibular: punto medio mandibular usado para comparar la coincidencia con la línea media maxilar; ubíquelo en la región sinfisaria/interincisiva según el trazado elegido.");
        GUIDE.put("Cd der.", "Condylion derecho (Cd): punto más superior de la cabeza condilar derecha.");
        GUIDE.put("Cd izq.", "Condylion izquierdo (Cd): punto más superior de la cabeza condilar izquierda.");
        GUIDE.put("Go der.", "Gonion derecho (Go): punto del ángulo mandibular derecho definido con el mismo criterio que en el lado izquierdo.");
        GUIDE.put("Go izq.", "Gonion izquierdo (Go): punto del ángulo mandibular izquierdo definido con el mismo criterio que en el lado derecho.");
        GUIDE.put("Kr der.", "Koronion/Coronoid derecho (Kr/Cor): punto más superior de la apófisis coronoides derecha.");
        GUIDE.put("Kr izq.", "Koronion/Coronoid izquierdo (Kr/Cor): punto más superior de la apófisis coronoides izquierda.");
        GUIDE.put("IC max der.", "Incisivo central maxilar derecho: punto de contacto/incisal usado por el trazado panorámico para comparar la distancia desde el cóndilo derecho con el lado contrario.");
        GUIDE.put("IC max izq.", "Incisivo central maxilar izquierdo: punto equivalente del lado izquierdo, usando exactamente el mismo criterio anatómico que a la derecha.");
        GUIDE.put("IC mand der.", "Incisivo central mandibular derecho: punto de contacto/incisal usado para la comparación desde el cóndilo derecho.");
        GUIDE.put("IC mand izq.", "Incisivo central mandibular izquierdo: punto equivalente del lado izquierdo, usando exactamente el mismo criterio anatómico que a la derecha.");
        GUIDE.put("Cuerpo Md der.", "Cuerpo mandibular derecho: punto de referencia elegido sobre el cuerpo mandibular derecho para comparar su distancia perpendicular a la línea media; use el mismo nivel anatómico a ambos lados.");
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
        return label + ": marque este punto anatómico únicamente si la medición seleccionada define de forma explícita su construcción.";
    }
}
