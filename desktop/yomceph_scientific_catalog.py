"""Catálogo científico de YomCeph v0.12.

El catálogo separa tres cosas que no deben confundirse:
1) una medición geométrica que la app puede calcular;
2) un conjunto de referencia publicado (población/edad/sexo específicos);
3) la interpretación clínica, que nunca sustituye el diagnóstico profesional.

No se activa una medición nueva sólo porque exista el nombre de un análisis. Cuando
la geometría o la referencia no están suficientemente verificadas, queda marcada como
``validation`` o ``other_projection`` y la UI la muestra sin fabricar resultados.
"""

STATUS_ACTIVE = "active"
STATUS_VALIDATION = "validation"
STATUS_REFERENCE_ONLY = "reference_only"
STATUS_OTHER_PROJECTION = "other_projection"

EXTRA_POINTS = [
    ("M", "M · centro de la premaxila",
     "Marque el centro del mayor círculo que pueda inscribirse en la región anterior de la maxila y sea tangente a sus límites anterior, superior y palatino según la definición del método YEN/W."),
    ("G", "G · centro de la sínfisis mandibular",
     "Marque el centro del mayor círculo que pueda inscribirse en la sínfisis mandibular y sea tangente a sus límites internos anterior, posterior e inferior según la definición del método YEN/W."),
    ("Co", "Condylion (Co)",
     "Punto más posterosuperior del contorno del cóndilo mandibular. Necesario para longitudes efectivas de McNamara."),
    ("Ptm", "Pterigomaxilar (Ptm)",
     "Punto en el contorno de la fisura pterigomaxilar usado por McNamara/COGS y otros análisis."),
    ("H", "H · hioides",
     "Punto cefalométrico del cuerpo del hioides. La definición exacta depende del protocolo; para Rocabado se usa el borde superior/anterior del cuerpo hioideo."),
    ("C3ai", "C3 anteroinferior",
     "Ángulo anteroinferior del cuerpo de la tercera vértebra cervical. Se usa con RGn y H en el triángulo hioideo."),
    ("RGn", "Retrognathion (RGn)",
     "Punto más posteroinferior de la sínfisis mandibular utilizado en el triángulo hioideo de Rocabado."),
    ("Ba", "Basion (Ba)",
     "Punto medio del borde anterior del foramen magno. Requerido por varios análisis y por el G-triangle."),
    ("Bo", "Bolton (Bo)",
     "Punto Bolton de la base craneal posterior usado en el análisis sagital G-triangle. Su localización requiere protocolo específico."),
]

MEASUREMENTS = {
    "SNA": dict(analysis="steiner", label="SNA", unit="°", required=["S", "N", "A"], status=STATUS_ACTIVE),
    "SNB": dict(analysis="steiner", label="SNB", unit="°", required=["S", "N", "B"], status=STATUS_ACTIVE),
    "ANB": dict(analysis="steiner", label="ANB", unit="°", required=["S", "N", "A", "B"], status=STATUS_ACTIVE),
    "SND": dict(analysis="steiner", label="SND", unit="°", required=["S", "N", "D"], status=STATUS_ACTIVE),
    "SL": dict(analysis="steiner", label="SL", unit="mm", required=["S", "N", "Pg"], status=STATUS_ACTIVE),
    "SE": dict(analysis="steiner", label="SE", unit="mm", required=["S", "N", "CI"], status=STATUS_ACTIVE),
    "SN–PoOr": dict(analysis="steiner", label="SN–PoOr", unit="°", required=["S", "N", "Po", "Or"], status=STATUS_ACTIVE),
    "Frankfort–SPP": dict(analysis="steiner", label="Frankfort–SPP", unit="°", required=["Po", "Or", "ANS", "PNS"], status=STATUS_ACTIVE),
    "Ar–Go–Me": dict(analysis="steiner", label="Ar–Go–Me", unit="°", required=["Ar", "Go", "Me"], status=STATUS_ACTIVE),
    "SN–GoGn": dict(analysis="steiner", label="SN–GoGn", unit="°", required=["S", "N", "Go", "Gn"], status=STATUS_ACTIVE),
    "AB–GoGn": dict(analysis="steiner", label="AB–GoGn", unit="°", required=["A", "B", "Go", "Gn"], status=STATUS_ACTIVE),
    "IS–SN": dict(analysis="steiner", label="IS–SN", unit="°", required=["U1a", "U1i", "S", "N"], status=STATUS_ACTIVE),
    "IS–NA (°)": dict(analysis="steiner", label="IS–NA (°)", unit="°", required=["U1a", "U1i", "N", "A"], status=STATUS_ACTIVE),
    "IS–NA (mm)": dict(analysis="steiner", label="IS–NA (mm)", unit="mm", required=["U1i", "N", "A"], status=STATUS_ACTIVE),
    "II–NB (°)": dict(analysis="steiner", label="II–NB (°)", unit="°", required=["L1a", "L1i", "N", "B"], status=STATUS_ACTIVE),
    "II–NB (mm)": dict(analysis="steiner", label="II–NB (mm)", unit="mm", required=["L1i", "N", "B"], status=STATUS_ACTIVE),
    "Plano oclusal–SN": dict(analysis="steiner", label="Plano oclusal–SN", unit="°", required=["OcA", "OcP", "S", "N"], status=STATUS_ACTIVE),
    "Ángulo interincisal": dict(analysis="steiner", label="Ángulo interincisal", unit="°", required=["U1a", "U1i", "L1a", "L1i"], status=STATUS_ACTIVE),
    "Línea S · labio superior": dict(analysis="steiner", label="Línea S · labio superior", unit="mm", required=["Ssoft", "Pgsoft", "Ls"], status=STATUS_ACTIVE),
    "Línea S · labio inferior": dict(analysis="steiner", label="Línea S · labio inferior", unit="mm", required=["Ssoft", "Pgsoft", "Li"], status=STATUS_ACTIVE),
    "Pg–NB": dict(analysis="steiner", label="Pg–NB", unit="mm", required=["Pg", "N", "B"], status=STATUS_ACTIVE),
    "SN–OPT": dict(analysis="posture", label="SN–OPT", unit="°", required=["S", "N", "cv2ip", "cv2tg"], status=STATUS_ACTIVE),
    "SN–CVT": dict(analysis="posture", label="SN–CVT", unit="°", required=["S", "N", "cv2tg", "cv4ip"], status=STATUS_ACTIVE),
    "OPT–CVT": dict(analysis="posture", label="OPT–CVT", unit="°", required=["cv2ip", "cv2tg", "cv4ip"], status=STATUS_ACTIVE),
    "Tangente posterior C2–C7": dict(analysis="posture", label="Tangente posterior C2–C7", unit="°", required=["C2ps", "C2pi", "C7ps", "C7pi"], status=STATUS_ACTIVE),
    "MGP–OP": dict(analysis="rocabado", label="Ángulo craneocervical MGP–OP", unit="°", required=["PNS", "C0", "Ops", "Opi"], status=STATUS_ACTIVE),
    "MGP–CVT": dict(analysis="posture", label="MGP–CVT (descriptivo)", unit="°", required=["PNS", "C0", "cv2tg", "cv4ip"], status=STATUS_ACTIVE),
    "Profundidad cervical (mm)": dict(analysis="posture", label="Profundidad cervical (Penning)", unit="mm", required=["C2ps", "C2pi", "C7ps", "C7pi", "PC"], status=STATUS_ACTIVE),
    "Powell Nasofrontal": dict(analysis="powell", label="Powell · nasofrontal", unit="°", required=["Gsoft", "Nsoft", "Dn"], status=STATUS_ACTIVE),
    "Powell Nasofacial": dict(analysis="powell", label="Powell · nasofacial", unit="°", required=["Gsoft", "Pgsoft", "Nsoft", "Dn"], status=STATUS_ACTIVE),
    "Powell Nasomental": dict(analysis="powell", label="Powell · nasomental", unit="°", required=["Nsoft", "Dn", "Prn", "Pgsoft"], status=STATUS_ACTIVE),
    "Powell Mentocervical": dict(analysis="powell", label="Powell · mentocervical", unit="°", required=["Gsoft", "Pgsoft", "Mesoft", "Csoft"], status=STATUS_ACTIVE),
    "Wits AO–BO": dict(analysis="wits", label="Wits AO–BO", unit="mm", required=["A", "B", "OcA", "OcP"], status=STATUS_ACTIVE),
    "YEN": dict(analysis="yen_w", label="Ángulo YEN", unit="°", required=["S", "M", "G"], status=STATUS_ACTIVE),
    "W": dict(analysis="yen_w", label="Ángulo W", unit="°", required=["S", "M", "G"], status=STATUS_ACTIVE),
    "Jarabak · Saddle": dict(analysis="jarabak", label="Jarabak · ángulo silla N-S-Ar", unit="°", required=["N", "S", "Ar"], status=STATUS_ACTIVE),
    "Jarabak · Articular": dict(analysis="jarabak", label="Jarabak · ángulo articular S-Ar-Go", unit="°", required=["S", "Ar", "Go"], status=STATUS_ACTIVE),
    "Jarabak · Gonial": dict(analysis="jarabak", label="Jarabak · ángulo gonial Ar-Go-Me", unit="°", required=["Ar", "Go", "Me"], status=STATUS_ACTIVE),
    "Jarabak · Upper gonial": dict(analysis="jarabak", label="Jarabak · gonial superior Ar-Go-N", unit="°", required=["Ar", "Go", "N"], status=STATUS_ACTIVE),
    "Jarabak · Lower gonial": dict(analysis="jarabak", label="Jarabak · gonial inferior N-Go-Me", unit="°", required=["N", "Go", "Me"], status=STATUS_ACTIVE),
    "Jarabak · Sum": dict(analysis="jarabak", label="Jarabak · suma angular", unit="°", required=["N", "S", "Ar", "Go", "Me"], status=STATUS_ACTIVE),
    "Jarabak · S-N": dict(analysis="jarabak", label="Jarabak · base craneal anterior S-N", unit="mm", required=["S", "N"], status=STATUS_ACTIVE),
    "Jarabak · S-Ar": dict(analysis="jarabak", label="Jarabak · base craneal posterior S-Ar", unit="mm", required=["S", "Ar"], status=STATUS_ACTIVE),
    "Jarabak · Ar-Go": dict(analysis="jarabak", label="Jarabak · altura de rama Ar-Go", unit="mm", required=["Ar", "Go"], status=STATUS_ACTIVE),
    "Jarabak · Go-Me": dict(analysis="jarabak", label="Jarabak · cuerpo mandibular Go-Me", unit="mm", required=["Go", "Me"], status=STATUS_ACTIVE),
    "Jarabak · N-Me": dict(analysis="jarabak", label="Jarabak · altura facial anterior N-Me", unit="mm", required=["N", "Me"], status=STATUS_ACTIVE),
    "Jarabak · S-Go": dict(analysis="jarabak", label="Jarabak · altura facial posterior S-Go", unit="mm", required=["S", "Go"], status=STATUS_ACTIVE),
    "Jarabak ratio": dict(analysis="jarabak", label="Jarabak ratio S-Go/N-Me", unit="%", required=["S", "Go", "N", "Me"], status=STATUS_ACTIVE),
}

ANALYSES = {
    "steiner": {"name":"Steiner","status":STATUS_ACTIVE,"summary":"Esquelético, vertical, dental y tejidos blandos. Los valores crudos se conservan siempre; la clasificación automática puede desactivarse o usar una referencia clásica publicada identificada explícitamente.","missing_landmarks":[]},
    "posture": {"name":"Postura craneofacial / Solow–Tallgren / cervical","status":STATUS_ACTIVE,"summary":"SN–OPT, SN–CVT, OPT–CVT, tangentes cervicales y profundidad cervical. Las variables posturales se mantienen descriptivas salvo que el estudio elija una referencia publicada específica.","missing_landmarks":[]},
    "powell": {"name":"Powell · perfil de tejidos blandos","status":STATUS_ACTIVE,"summary":"Cuatro ángulos del triángulo estético: nasofrontal, nasofacial, nasomental y mentocervical.","missing_landmarks":[]},
    "wits": {"name":"Wits","status":STATUS_ACTIVE,"summary":"Proyección perpendicular de A y B al plano oclusal funcional y distancia AO–BO.","missing_landmarks":[]},
    "jarabak": {"name":"Björk–Jarabak","status":STATUS_ACTIVE,"summary":"Ángulos silla/articular/gonial, dimensiones lineales y proporción facial de Jarabak.","missing_landmarks":[]},
    "yen_w": {"name":"YEN y W","status":STATUS_ACTIVE,"summary":"Indicadores sagitales S-M-G. Requieren marcar los puntos M y G siguiendo su definición publicada.","missing_landmarks":["M","G"]},
    "rocabado": {"name":"Rocabado","status":STATUS_VALIDATION,"summary":"El ángulo craneocervical MGP–OP 96–106° ya está implementado. C0–C1, C1–C2 y triángulo hioideo requieren puntos adicionales y validación geométrica antes de activarse.","missing_landmarks":["H","C3ai","RGn","C1 posterior"]},
    "airway": {"name":"Vías aéreas · McNamara","status":STATUS_VALIDATION,"summary":"Anchuras faríngeas superior e inferior en lateral de cráneo. Son medidas 2D de cribado/anatomía, no diagnóstico de obstrucción ni apnea.","missing_landmarks":["puntos faríngeos específicos superior/inferior"]},
    "mcnamara": {"name":"McNamara","status":STATUS_VALIDATION,"summary":"A-N perpendicular, Pog-N perpendicular, Co-A, Co-Gn, diferencia maxilomandibular, altura facial, incisivos y vía aérea. Varias normas dependen de edad/sexo.","missing_landmarks":["Co","Ptm","puntos faríngeos"]},
    "downs": {"name":"Downs","status":STATUS_VALIDATION,"summary":"Ángulo facial, convexidad, AB-plane, plano mandibular, eje Y y variables dentales. Se está validando orientación/signo antes de activarlo.","missing_landmarks":[]},
    "tweed": {"name":"Tweed","status":STATUS_VALIDATION,"summary":"Triángulo FMA–FMIA–IMPA. La selección está documentada; falta cerrar pruebas de orientación angular antes de activarla.","missing_landmarks":[]},
    "ricketts": {"name":"Ricketts","status":STATUS_VALIDATION,"summary":"Incluye puntos construidos y normas que cambian con edad. Se integrará por bloques para evitar aplicar referencias adultas a niños.","missing_landmarks":["Xi","Pm","Pt","Dc","Cc"]},
    "cogs": {"name":"COGS · Burstone","status":STATUS_VALIDATION,"summary":"Cephalometrics for Orthognathic Surgery. Requiere plano horizontal de COGS, Ptm, molares y referencias diferenciadas por sexo/población.","missing_landmarks":["Ptm","molar superior","molar inferior","plano HP construido"]},
    "sassouni": {"name":"Sassouni · análisis de arcos","status":STATUS_VALIDATION,"summary":"Análisis estructural basado en múltiples planos y arcos. La literatura confirma variación de normas; falta formalizar el constructor de centro/arcos.","missing_landmarks":["centro de convergencia de planos / construcciones de arco"]},
    "bimler": {"name":"Bimler","status":STATUS_VALIDATION,"summary":"Análisis histórico con puntos y construcciones propias. Las fuentes indexadas localizadas no bastan aún para codificar una tabla completa sin el manual/original metodológico.","missing_landmarks":["puntos y construcciones específicos de Bimler por verificar"]},
    "alexander": {"name":"Alexander Discipline","status":STATUS_REFERENCE_ONLY,"summary":"La literatura indexada describe principalmente una disciplina/técnica de tratamiento; no se ha confirmado un único análisis cefalométrico canónico equivalente a Steiner. No se inventará uno.","missing_landmarks":[]},
    "g_triangle": {"name":"Sagittal G-triangle","status":STATUS_VALIDATION,"summary":"Método de 2022 con AXK/BXK construido a partir de Ba, Bo, Po, Or y G. Requiere implementar y probar la construcción Bo-X-K antes de activarlo.","missing_landmarks":["Ba","Bo","G","X/K construidos"]},
    "ritucci": {"name":"Ritucci–Burstone · asimetría","status":STATUS_OTHER_PROJECTION,"summary":"El método publicado usa radiografía submentovertex (SMV), no la lateral de cráneo. No puede ofrecerse honestamente dentro del flujo de una sola lateral.","missing_landmarks":["23 pares de landmarks en proyección submentovertex"]},
}

REFERENCES = {
    "steiner":["Steiner CC. Cephalometrics for you and me. Am J Orthod. 1953.","Cephalometric Evaluation Based on Steiner's Analysis on Adults of Bihar. PMCID: PMC8686945."],
    "wits":["Jacobson A. The Wits appraisal of jaw disharmony. Am J Orthod. 1975;67(2):125-138. PMID:1054214."],
    "yen_w":["Neela PK, Mascarenhas R, Husain A. A new sagittal dysplasia indicator: the YEN angle. World J Orthod. 2009;10(2):147-151. PMID:19582259.","Bhad WA, Nayak S, Doshi UH. A new approach of assessing sagittal dysplasia: the W angle. Eur J Orthod. 2013;35(1):66-70. PMID:21303811."],
    "g_triangle":["Li B, et al. Sagittal G-Triangle Analysis. J Craniofac Surg. 2022;33(2):521-525. PMID:34669681; PMCID:PMC8865203."],
    "jarabak":["Evaluation of skeletal variations and establishment of cephalometric norms using Bjork Jarabak’s analysis. PMCID:PMC6191777."],
    "rocabado":["Rocabado-Penning skull-cervical posture in orthodontic patients. PMCID:PMC11495177."],
    "cogs":["Burstone CJ, James RB, Legan H, Murphy GA, Norton LA. Cephalometrics for orthognathic surgery. J Oral Surg. 1978;36:269-277."],
    "ritucci":["Cephalometric norms for craniofacial asymmetry using submental-vertical radiographs. PMID:8074089."],
}

def analysis_measurements(analysis_id, active_only=False):
    out=[]
    for key,spec in MEASUREMENTS.items():
        if spec.get("analysis")!=analysis_id: continue
        if active_only and spec.get("status")!=STATUS_ACTIVE: continue
        out.append(key)
    return out

def required_landmarks(measure_keys):
    seen=set();out=[]
    for key in measure_keys:
        for landmark in MEASUREMENTS.get(key,{}).get("required",[]):
            if landmark not in seen:
                seen.add(landmark);out.append(landmark)
    return out
