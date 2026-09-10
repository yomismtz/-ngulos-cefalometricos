# Auditoría de referencias cefalométricas de YomCeph

Última revisión: 2026-09-10.

YomCeph es una herramienta educativa. Los valores de referencia dependen del análisis, edad, sexo, población, técnica radiográfica y protocolo. Ninguna medición aislada equivale a un diagnóstico.

## Steiner

Referencias centrales conservadas en la app:

- SNA: 82° ± 2°.
- SNB: 80° ± 2°.
- ANB: 2° ± 2°. La app conserva el signo mediante SNA − SNB.
- SN-GoGn: 32° ± 5°.
- Plano oclusal-SN: 14° ± 2°.
- Incisivo superior-NA: 22° ± 2°.
- Incisivo inferior-NB: 25° ± 2°.
- Ángulo interincisal: aproximadamente 130–131° según la referencia utilizada.
- SND: aproximadamente 76°.

Fuentes de contraste:
- Steiner CC. *The use of cephalometrics as an aid to planning and assessing orthodontic treatment*. Am J Orthod. 1960.
- Tabla contemporánea de parámetros de Steiner: https://pmc.ncbi.nlm.nih.gov/articles/PMC12412276/

## Tweed

Referencias centrales:
- FMA: 25°; la app usa 20–30° como intervalo central 25° ± 5° y muestra además el rango histórico publicado 16–35°.
- FMIA: valor de referencia 65°; rango histórico publicado 60–75° (algunas tablas contemporáneas lo expresan como 65° ± 5°).
- IMPA: 90° ± 5°.

Reglas históricas de relación:
- FMA 21–29°: objetivo FMIA cercano a 68°.
- FMA ≥30°: objetivo FMIA cercano a 65°.
- FMA ≤20°: IMPA no debería exceder aproximadamente 92° según la formulación histórica.

Fuentes:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC8402232/
- Tweed Foundation historical material: https://tweedortho.com/wp-content/uploads/2024/12/frankfort-mandibular-incisor-angle.pdf

## Triángulo hioideo de Bibby/Preston

Valores históricos de la muestra original:
- C3-RGn: 67.2 ± 6.6 mm.
- C3-H: 31.76 ± 2.9 mm.
- H-RGn: 36.83 ± 5.83 mm.
- H-H′: 4.80 ± 4.64 mm.
- AA-PNS/ENP: 32.91 ± 3.66 mm.

Fuente primaria:
- Bibby RE, Preston CB. *The hyoid triangle*. Am J Orthod. 1981;80(1):92-97. PMID 6942659. DOI: 10.1016/0002-9416(81)90199-8.

## Rocabado / Penning

Referencias usadas:
- Ángulo craneocervical: 96–106°.
- C0-C1: 4–9 mm.
- Profundidad cervical:
  - <2 mm: cifótica/invertida.
  - 2 a <8 mm: rectificada.
  - 8–12 mm: intervalo de referencia.
  - >12 mm: lordosis aumentada.

Fuente de contraste:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC11495177/

Las medidas SN-CVT, SN-OPT y McGregor-C4 se mantienen como referencias de protocolo/docencia y no se presentan como umbrales diagnósticos universales.

## Powell

Rangos usados:
- Nasofrontal: 115–130°.
- Nasofacial: 30–40°.
- Nasomental: 120–132°.
- Mentocervical: 80–95°.

Fuentes de contraste:
- Universidad Nacional Autónoma de México: https://tesiunamdocumentos.dgb.unam.mx/ptd2019/enero/0784598/0784598.pdf
- Revisión clínica del triángulo de Powell: https://www.rhinoplastyarchive.com/articles/rhinoplasty-fundamentals/rhinoplasty-long-term-effects

Estos rangos describen proporciones estéticas históricas y no son estándares universales para todas las poblaciones.

## McNamara / vía aérea

Referencia original:
- McNamara JA Jr. *A method of cephalometric evaluation*. Am J Orthod. 1984;86(6):449-469. PMID 6594933. DOI: 10.1016/S0002-9416(84)90352-X.

Valores adultos mostrados:
- Faringe superior: mujeres 17.4 ± 3.4 mm; hombres 17.4 ± 4.3 mm.
- Faringe inferior: mujeres 11.3 ± 3.3 mm; hombres 13.5 ± 4.3 mm.

La telerradiografía lateral es una representación 2D obtenida en vigilia y no diagnostica apnea del sueño ni obstrucción respiratoria por sí sola.

AD1 y AD2 permanecen como medidas geométricas sin umbral diagnóstico automático. Se retiró AD3 Uptp–Adenoides porque la construcción previa dependía de una tabla no incluida en la app y no pudo verificarse de forma reproducible con las fuentes revisadas. Las convenciones de colocación se documentan en LANDMARK_PLACEMENT_GUIDE.md.

## Control de consistencia

El build de YomCeph ejecuta pruebas unitarias para:
- conservar ANB con signo;
- mantener iguales las referencias SN-Frankfort entre módulos;
- proteger los valores centrales de Steiner y Tweed;
- proteger los límites de profundidad cervical;
- comprobar que la referencia H-H′ publicada siga visible.


## Revisión de puntos y flujo 2026-09-10

- OPT se construye con Cv2tg–Cv2ip y CVT con Cv2tg–Cv4ip, compartiendo Cv2tg para evitar duplicación del mismo punto anatómico.
- Se retiró la medición McGregor–C4 que dependía de C4-1/C4-2 sin definición reproducible.
- El análisis parcial ahora omite únicamente las medidas cuyos puntos estén incompletos.
- Se separan las exportaciones de radiografía con puntos y radiografía con trazado.
- La guía visual integrada es un esquema original, no a escala y no interviene en los cálculos.
