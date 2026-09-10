# Auditoría clínica de YomCeph · 2026-09-10

Esta revisión reorganiza YomCeph por **tema de evaluación** y no por apellido de autor. Los nombres históricos se conservan únicamente en la referencia de una medición cuando esa medición corresponde a un método publicado.

## 1. Análisis cefalométrico

### Medidas angulares adoptadas

- SNA: 82° ± 2°.
- SNB: 80° ± 2°.
- ANB: 2° ± 2°, conservando el signo de SNA-SNB.
- SND: 76° ± 2°.
- SN-GoGn: 32° ± 4°.
- NS-SGn (eje Y): 65° ± 3°.
- Plano oclusal-SN: 14° ± 3°.
- Incisivo superior-SN: 103° ± 4°.
- Incisivo superior-NA: 22° ± 6°.
- Incisivo inferior-NB: 25° ± 4°.
- Interincisal: 131° ± 4°.
- Ángulo goníaco Ar-Go-Me: 130° ± 7° / intervalo 123°-137° como medición complementaria de referencia Björk-Jarabak.

### Medidas lineales

- SL: 51 ± 4 mm. L se construye proyectando Pg perpendicularmente sobre SN; el usuario solo debe marcar S, N y Pg.
- SE: 22 ± 3 mm. E se construye proyectando el punto más posterior del contorno condilar perpendicularmente sobre SN; el usuario no debe marcar E.
- Incisivo superior a NA: 4 mm como valor clásico; distancia perpendicular del borde incisal a NA.
- Incisivo inferior a NB: 4 mm como valor clásico; distancia perpendicular del borde incisal a NB.

Se eliminaron del bloque principal varias medidas que estaban mezcladas como si pertenecieran a una sola versión de Steiner y no tenían una fuente suficientemente clara en el catálogo actual.

Fuentes: Ibarra et al., *Applied System Innovation* 2022, https://www.mdpi.com/2673-6470/2/2/8 ; literatura cefalométrica complementaria indicada en el repositorio independiente `Analisis-Cefalometrico`.

## 2. Postura cráneo-cervical

### Landmarks cervicales definidos

- C0: base/escama occipital usada para McGregor.
- C1 superior/posterior: punto más superior y posterior del arco posterior del atlas.
- C1 inferior/posterior: punto más inferior y posterior del arco posterior del atlas.
- C2 anteroinferior: ángulo anteroinferior del cuerpo del axis.
- C2 espinosa superior/posterior: punto más superior y posterior de la apófisis espinosa de C2.
- CV2tg: punto de tangencia superoposterior de la odontoides.
- CV2ip: punto más inferoposterior del cuerpo de C2.
- C3: ángulo anteroinferior del cuerpo de C3.
- CV4ip: punto más inferoposterior del cuerpo de C4.
- CV6ip: punto más inferoposterior del cuerpo de C6.
- C7 posteroinferior: extremo inferior de la tangente de Penning.

### Medidas adoptadas

- Ángulo cráneo-odontoideo: McGregor / plano odontoideo, 101° ± 5°; intervalo funcional 96°-106°.
- C0-C1: 4-9 mm. Debe medirse respecto al plano de McGregor y al punto superior/posterior del atlas. La implementación previa como simple distancia Occipital-C1 era geométricamente incompleta y fue corregida en el catálogo.
- C1-C2: 4-9 mm entre el punto inferior/posterior del arco posterior del atlas y el punto superior/posterior de la apófisis espinosa de C2.
- Profundidad cervical de Penning: tangente desde región posterosuperior de la odontoides/C2 hasta C7 posteroinferior, perpendicular a nivel de C4. Referencia 10 ± 2 mm. Clasificación usada: valor negativo = cifótica/invertida; 0 a <8 mm = rectificada; 8-12 mm = intervalo fisiológico; >12 mm = lordosis aumentada.
- Triángulo hioideo: C3-RGn-H y altura perpendicular H-H'. Se informa posición y magnitud; no se convierte en diagnóstico respiratorio.
- OPT: CV2tg-CV2ip.
- CVT: CV2tg-CV4ip.
- EVT: CV4ip-CV6ip.
- CVT/EVT: se añade como descripción de la angulación cervical; no se asigna por ahora un umbral universal de normalidad.

Se retira `McGregor-C4 100°-110°`, porque no se localizó una construcción bibliográfica suficientemente consistente para esa medición exacta.

Fuentes principales: Rocabado/Penning revisados en https://pmc.ncbi.nlm.nih.gov/articles/PMC11495177/ ; Aldana et al. https://www.scielo.cl/scielo.php?pid=S0718-381X2011000200002&script=sci_arttext ; revisión de postura cervical https://pmc.ncbi.nlm.nih.gov/articles/PMC4009738/ .

## 3. Perfil facial

Se mantiene como módulo de **Perfil facial**, no “Análisis de Powell”. Las mediciones actuales son nasofrontal, nasofacial, nasomental y mentocervical. Los rangos deben mostrarse como referencias estéticas de población/método y no como normalidad clínica universal. El intervalo mentocervical varía entre publicaciones, por lo que el informe debe declarar la referencia adoptada.

## 4. Triángulo dentofacial

Se mantiene FMA, FMIA e IMPA, pero el módulo se denomina **Triángulo dentofacial**. Referencias centrales adoptadas:

- FMA: 25° ± 5°.
- FMIA: ideal 65°; intervalo central 65° ± 5°.
- IMPA: 90° ± 5°.
- Control geométrico: FMA + FMIA + IMPA ≈ 180°.

No debe generar automáticamente un pronóstico clínico de tratamiento a partir de esos tres valores.

## 5. Simetría panorámica

El módulo deja de llamarse “Levandoski” en la interfaz. Se conservan comparaciones derecha/izquierda, recordando que una panorámica tiene distorsión y magnificación no uniformes.

Candidato prioritario para una siguiente versión del motor:

- Cor-Go / Cd-Go por lado. La literatura sobre hiperplasia coronoidea utiliza esta razón y propone que valores >1.1 justifican investigación adicional; no debe usarse como diagnóstico único. Las longitudes crudas dependen del tamaño y de la distorsión, mientras que la razón es más robusta para comparación.

Fuentes: https://pmc.ncbi.nlm.nih.gov/articles/PMC9157585/ ; https://pubmed.ncbi.nlm.nih.gov/10577758/ ; https://pubmed.ncbi.nlm.nih.gov/21495328/ .

## 6. Vía aérea superior

### Adenoides

- AD1: punto adenoideo/pared posterior sobre PNS-Ba.
- AD2: punto adenoideo/pared posterior sobre una perpendicular a S-Ba trazada desde PNS.
- AD3: sí existe como construcción reproducible, pero `Uptp` no se conserva como nomenclatura universal. En el protocolo de Solow se utiliza `tu`, punto posterosuperior de la tuberosidad maxilar/profundidad del contorno anterior de la región pterigopalatina, y `ad3`, punto de tejido adenoideo/pared faríngea dorsal más cercano a `tu`; se informa la distancia tu-ad3.

Los valores de una tabla docente previa para edades 6/16 no se usan como clasificación automática mientras no se trace su fuente primaria y población.

### Medidas adicionales verificadas

- MP-H: perpendicular del plano mandibular al hioides, referencia 15.4 ± 3 mm.
- PNS-P: longitud del paladar blando, referencia 37 ± 3 mm.
- Las medidas faríngeas se mantienen como evaluación 2D; no deben afirmar ni descartar apnea, obstrucción o hipertrofia por sí solas.

Fuentes: https://scielo.isciii.es/scielo.php?script=sci_arttext&pid=S1138-123X2002000500006 ; https://pubmed.ncbi.nlm.nih.gov/11359132/ ; revisión de Solow/ad3 y literatura de vía aérea citada en el historial de la auditoría.

## Reglas de interpretación para toda la app

1. Cada resultado debe declarar su referencia y no presentar una norma poblacional como verdad universal.
2. Una sola medida no debe generar diagnóstico.
3. Si faltan puntos, se calculan solo las medidas geométricamente posibles.
4. Los puntos construidos por proyección se calculan por software y no se piden como landmarks manuales.
5. Las medidas lineales requieren calibración válida.
6. Cuando la evidencia define una medida pero no un umbral reproducible, la app debe mostrarla como descriptiva.
7. Los módulos se nombran por el tema evaluado; los autores se citan en la fuente de cada medición.
