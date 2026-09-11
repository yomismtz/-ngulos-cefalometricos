# YomCeph v0.12.0 — Auditoría científica de análisis, landmarks y referencias

**Fecha de revisión:** 11 de septiembre de 2026  
**Alcance:** telerradiografía lateral de cráneo, salvo que se indique otra proyección.

YomCeph distingue entre **geometría de una medición**, **conjunto de referencia publicado** e **interpretación clínica**. Un valor puede calcularse correctamente sin que exista una norma universal aplicable a toda edad, sexo o población.

## Principios de implementación

- La distribución pública es neutral: no incluye universidad, escuela, clínica, país, muestra ni investigación preconfigurados.
- Los valores crudos se conservan independientemente de la referencia seleccionada.
- Cuando se utiliza una referencia publicada, queda identificada como tal y separada de cualquier protocolo propio del usuario.
- Una medición nueva sólo se activa cuando sus landmarks y geometría pueden definirse de forma reproducible.
- Un análisis incompleto permanece visible como **En validación**; YomCeph no fabrica resultados.
- Ritucci–Burstone se marca **Otra proyección**, porque el método publicado para asimetría utiliza submentovertex (SMV), no lateral.
- “Prevalencia” sólo se calcula para categorías con una regla explícita del protocolo; las variables continuas se resumen con n, media, DE, mínimo y máximo.

## Steiner

Landmarks principales: S, N, A, B, D, Pg, Po, Or, ANS, PNS, Ar, Go, Me, Gn, CI, ejes incisivos, plano oclusal y tejidos blandos para línea S.

Una tabla contemporánea que reproduce valores tradicionales reporta aproximadamente SNA 82°, SNB 80°, ANB 2°, SN-GoGn 32°, plano oclusal-SN 14°, U1-NA 22°/4 mm, L1-NB 25°/4 mm y línea S 0 mm. En la versión pública, el usuario puede trabajar sin clasificación automática o seleccionar una referencia clásica publicada. No se incluye una referencia institucional propia como opción preconfigurada.

Pendiente matemático: varias fórmulas históricas de YomCeph usan `closest_supplement()`. Se conserva por compatibilidad con datos creados en versiones anteriores, pero no se generaliza a nuevos módulos hasta sustituirlo por una orientación geométrica inequívoca.

**Fuentes:** Steiner CC. *Am J Orthod*. 1953; PMCID: PMC8686945.

## Wits appraisal — activo

Landmarks: A, B y plano oclusal funcional. A y B se proyectan perpendicularmente para obtener AO y BO y se mide su separación sobre el plano. La referencia original de Jacobson depende del sexo y de la convención de signo, por lo que YomCeph conserva el valor crudo y documenta la convención.

**Fuente:** Jacobson A. *Am J Orthod*. 1975;67(2):125-138. PMID: 1054214.

## YEN y W — activos

Landmarks: S, M y G. YEN es el ángulo S-M-G. Referencia original: 117–123° Clase I, <117° Clase II, >123° Clase III. El ángulo W utiliza M-G y la perpendicular desde M a S-G; referencia original 51–56° Clase I, <51° Clase II, >56° Clase III.

**Fuentes:** Neela PK et al. PMID: 19582259; Bhad WA et al. PMID: 21303811.

## Björk–Jarabak — activo

Landmarks: N, S, Ar, Go y Me. Incluye ángulos silla, articular y gonial, suma angular, S-N, S-Ar, Ar-Go, Go-Me, S-Go, N-Me y ratio S-Go/N-Me ×100. Las longitudes absolutas requieren calibración y las referencias varían por población, edad y sexo.

Referencias históricas reproducidas: silla 123±6°, articular 143±5°, gonial 130±6°, suma 396±5°, S-Ar 32±3 mm, S-N 71±3 mm, Ar-Go 44±5 mm, Go-Me 71±5 mm, S-Go 77.5±7.5 mm, N-Me 112.5±7.5 mm y ratio 63.5±1.5%.

**Fuente:** PMCID: PMC6191777.

## Postura craneofacial / Solow–Tallgren — activa como variables descriptivas

Landmarks actuales: S, N, cv2ip, cv2tg, cv4ip, pares posteriores C2–C7, PC, PNS, C0, Ops y Opi. Se calculan SN-OPT, SN-CVT, OPT-CVT, tangente posterior C2-C7, MGP-CVT y profundidad cervical. No se asigna una única “normal universal” a los ángulos posturales: la literatura muestra dependencia de técnica, edad, postura y población.

## Rocabado — parcialmente activo

El ángulo craneocervical McGregor/plano odontoideo permanece disponible. Para el módulo completo se requieren H, RGn, C3 anteroinferior y referencias C0/C1/C2 adicionales para el triángulo hioideo y espacios suboccipitales. Esas extensiones permanecen en validación hasta cerrar la geometría exacta.

**Fuentes de revisión:** PMCID: PMC4942290; PMC3555465; PMC11495177.

## Powell — activo y corregido

Landmarks: G', N', Dn, Prn, Pg', Me' y punto cervical C. Desde v0.9 YomCeph separa Dn de Prn: la dirección del dorso nasal usa N'–Dn y Prn sigue siendo la punta nasal. Rangos de referencia actuales: nasofrontal 115–130°, nasofacial 30–40°, nasomental 120–132° y mentocervical 80–95°. Se presentan como referencias estéticas, no diagnóstico de patología.

## McNamara y vías aéreas — en validación

Se han identificado Co y Ptm como landmarks prioritarios, además de puntos faríngeos superiores/inferiores. El catálogo contempla A a N-perpendicular, Pog a N-perpendicular, Co-A, Co-Gn, diferencia maxilomandibular, altura facial y variables 2D de vía aérea. No se aplicará una norma universal porque las referencias dependen de edad, sexo y población. Una lateral 2D no se utilizará para diagnosticar apnea u obstrucción por sí sola.

## Downs y Tweed — en validación

Downs requiere validar orientación/signo del ángulo facial, convexidad, AB-plane, plano mandibular, eje Y y variables dentales. Tweed requiere cerrar la orientación de FMA, FMIA e IMPA antes de activar clasificación automática.

## Ricketts — en validación por edad

Landmarks prioritarios: Pt, DC, CC, CF, Xi y Pm, además de los ya existentes. Varias referencias de Ricketts cambian con crecimiento, por lo que YomCeph no aplicará una norma adulta fija a niños y adolescentes.

## COGS / Burstone — en validación

Landmarks/construcciones: Ar, Ptm, N, A, B, Pg, ANS, PNS, Gn, Go, ejes incisivos, primeros molares y plano horizontal HP construido según COGS. Las tablas de referencia originales dependen del sexo y no deben extrapolarse automáticamente a otras poblaciones.

**Fuente primaria:** Burstone CJ et al. *J Oral Surg*. 1978;36:269-277. Referencias reproducidas en PMCID: PMC4252385 y PMC3723291.

## Sassouni y Bimler — en validación documental

Sassouni requiere formalizar el centro de convergencia y las construcciones de arcos exactas; no se codificarán aproximaciones. Para Bimler, las publicaciones indexadas localizadas no aportan en sus resúmenes una especificación suficiente de todo el método; el módulo permanece en validación hasta revisar la metodología completa/original.

## Alexander

La literatura indexada localizada describe principalmente la Alexander Discipline como filosofía/técnica terapéutica. No se confirmó un único análisis cefalométrico canónico equivalente a Steiner, por lo que YomCeph no inventará uno bajo ese nombre.

## Sagittal G-triangle — en validación

Requiere Ba, Bo, Po, Or, G y construcciones X/K antes de medir AXK/BXK. La construcción geométrica y las referencias poblacionales/por sexo deben implementarse y probarse antes de activar el módulo.

**Fuente:** PMID: 34669681; PMCID: PMC8865203.

## Ritucci–Burstone — otra proyección

El sistema publicado para asimetría usa radiografía **submental-vertical (SMV)** y evalúa pares de landmarks. No se ofrecerá falsamente dentro del flujo “misma lateral de cráneo”.

**Fuentes:** PMID: 8074089; PMID: 6584032.

## Landmarks nuevos prioritarios

M, G, Co, Ptm, H, C3 anteroinferior, RGn, Ba y Bo ya están incorporados al catálogo de expansión. En fases posteriores se añadirán los puntos faríngeos específicos, puntos de Ricketts (Pt/DC/CC/CF/Xi/Pm), molares COGS y referencias de C1 cuando sus definiciones queden cerradas.

## Estadística y exportación

Para casos **incluidos** YomCeph puede calcular n válido, media, desviación estándar, mínimo, máximo y frecuencias. Sólo reporta prevalencia (%) cuando existe una categoría explícita y reproducible. La exportación para IBM SPSS se hace mediante CSV UTF-8 + archivo `.sps` de importación reproducible; no se crea un `.sav` falso.

## Referencias principales verificadas

1. Steiner CC. Cephalometrics for you and me. *Am J Orthod*. 1953.
2. PMCID: PMC8686945 — tabla contemporánea basada en Steiner.
3. Jacobson A. The Wits appraisal of jaw disharmony. PMID: 1054214.
4. Neela PK, Mascarenhas R, Husain A. YEN angle. PMID: 19582259.
5. Bhad WA, Nayak S, Doshi UH. W angle. PMID: 21303811.
6. Björk–Jarabak norms. PMCID: PMC6191777.
7. McNamara population comparison. PMCID: PMC8018756.
8. Rocabado/hyoid literature: PMC4942290; PMC3555465; PMC11495177.
9. Burstone/COGS: PMCID: PMC4252385; PMC3723291.
10. Ricketts growth/landmarks: PMCID: PMC3971129.
11. Sassouni validation: PMID: 2638077; arc analysis PMID: 4081484.
12. Sagittal G-triangle: PMID: 34669681; PMCID: PMC8865203.
13. Ritucci/Burstone SMV asymmetry: PMID: 8074089; 6584032.

**Estado:** suficiente para activar de forma trazable Steiner, Postura como variables seleccionables, Powell, Wits, Björk–Jarabak y YEN/W. Los demás módulos permanecen visibles, pero no producen resultados hasta completar su validación geométrica y bibliográfica.
