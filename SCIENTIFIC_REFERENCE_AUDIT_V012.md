# YomCeph v0.12.6 — Auditoría científica de análisis, landmarks y referencias

**Fecha de revisión:** 11 de septiembre de 2026  
**Alcance:** telerradiografía lateral de cráneo, salvo que se indique expresamente otra proyección.

YomCeph separa **geometría**, **referencia poblacional** e **interpretación**. Una medición puede estar geométricamente bien implementada sin que exista una norma universal para todas las edades, sexos o poblaciones. La etiqueta **Disponible** significa que existe un bloque reproducible y probado; no implica que todos los componentes históricos del análisis estén automatizados ni que YomCeph realice un diagnóstico clínico.

## Principios de implementación

- La distribución pública es neutral: no incluye universidad, clínica, país, muestra ni investigación preconfigurados.
- El valor crudo se conserva independientemente de la referencia seleccionada.
- Las normas poblacionales no intervienen en la construcción geométrica de un ángulo o una distancia.
- Las mediciones lineales en milímetros requieren calibración.
- Un bloque nuevo sólo se activa cuando sus landmarks, geometría, unidad y convención de signo/sector pueden reproducirse.
- Las referencias dependientes de edad/sexo/población no se convierten en una “normalidad” universal.
- Una lateral 2D no se usa para diagnosticar apnea u obstrucción por sí sola.
- Ritucci–Burstone permanece como **Otra proyección** porque el método de asimetría publicado usa submentovertex (SMV).
- Alexander permanece como **Referencia** porque la literatura localizada describe principalmente la Alexander Discipline y no un único análisis cefalométrico canónico equivalente a Steiner.

## Geometría antes que norma

Las versiones heredadas contenían rutas que podían elegir un ángulo o su suplemento por proximidad a un valor esperado. La entrada pública actual recalcula las mediciones activas con reglas geométricas explícitas. Entre otras:

- SN–PoOr, SN–GoGn y AB–GoGn: sector agudo.
- IS–SN: sector obtuso del eje incisivo respecto de SN.
- SN–OPT y SN–CVT: sector obtuso/inferiormente abierto.
- MGP–OP: sector obtuso McGregor/plano odontoideo.
- Powell nasomental: sector obtuso entre tangente dorsonasal y Prn–Pg′.
- Powell mentocervical: vectores anatómicamente ordenados G′→Pg′ y Me′→C.

Las pruebas incluyen reflexión izquierda/derecha para evitar que el resultado cambie sólo por orientación de la imagen.

## Steiner — disponible

Incluye el bloque esquelético, vertical, dentoalveolar y de tejidos blandos ya auditado. La opción **Sin clasificación automática** conserva el valor crudo sin inyectar una norma heredada. Una referencia clásica sólo se usa cuando el usuario la selecciona explícitamente.

**Fuentes:** Steiner CC. *Am J Orthod*. 1953; PMCID PMC8686945.

## Wits — disponible

A y B se proyectan perpendicularmente sobre el plano oclusal funcional para obtener AO y BO. La dirección posterior→anterior del plano fija el signo. La referencia original varía según sexo y convención.

**Fuente:** Jacobson A. *Am J Orthod*. 1975;67(2):125–138. PMID 1054214.

## YEN y W — disponibles

YEN usa S–M–G con vértice M; W usa M–G y la perpendicular desde M a S–G. M y G se describen mediante las construcciones circulares publicadas, no como simples “puntos medios”.

**Fuentes:** PMID 19582259; PMID 21303811.

## Björk–Jarabak — disponible

Incluye ángulos silla, articular y gonial, suma angular, S–N, S–Ar, Ar–Go, Go–Me, S–Go, N–Me y ratio S–Go/N–Me ×100. Las longitudes requieren calibración y sus referencias cambian según población/edad/sexo.

**Fuente:** PMCID PMC6191777.

## Postura craneocervical / Solow–Tallgren — disponible como geometría descriptiva

Incluye SN–OPT, SN–CVT, OPT–CVT, tangentes cervicales, MGP–CVT y profundidad cervical. No se asigna una única norma universal.

**Fuentes:** Solow B, Tallgren A. PMID 937521; revisión PMCID PMC4009738.

## Powell — disponible

Dn y Prn son landmarks distintos. Se calculan los ángulos nasofrontal, nasofacial, nasomental y mentocervical. Los rangos estéticos, cuando se muestran, son referencias y no diagnóstico.

## Tweed — disponible

Se calculan FMA, FMIA e IMPA a partir de Frankfort, plano mandibular y eje del incisivo inferior. El sector se define por la geometría, no por proximidad a una norma.

**Fuente primaria:** Tweed CH, trabajos sobre Frankfort-mandibular incisor angle y triángulo diagnóstico de Tweed.

## McNamara — núcleo reproducible disponible

Se calculan:

- A a N-perpendicular.
- Pg a N-perpendicular.
- Co–A.
- Co–Gn.
- Diferencia maxilomandibular Co–Gn − Co–A.
- ANS–Me.
- Plano mandibular respecto de Frankfort.

Las variables lineales requieren calibración. No se aplican automáticamente normas pediátricas/adultas o por sexo.

### Corrección Pt vs Ptm

En v0.12.5 existió una salida histórica denominada `BaN–PtmGn`. La auditoría bibliográfica mostró que el **eje facial de Ricketts** utiliza **Pt**, no Ptm. v0.12.6 retira esa medición del catálogo activo y la reemplaza por el eje facial correcto dentro del bloque Ricketts. Pt y Ptm quedan definidos como landmarks distintos.

**Fuentes:** McNamara JA Jr. *A method of cephalometric evaluation*. Am J Orthod. 1984; reproducción metodológica PMCID PMC8018756.

## Vía aérea 2D — disponible como morfometría descriptiva

Se calculan las anchuras faríngeas superior e inferior mediante los puntos anteriores/posteriores correspondientes. No se infiere apnea, obstrucción ni patología a partir de una lateral aislada.

## Rocabado — bloque reproducible disponible

Incluye MGP–OP y el bloque lineal C0–C1, C1–C2, C3–RGn, C3–H, H–RGn y distancia perpendicular de H a C3–RGn. Las distancias requieren calibración.

**Fuentes de revisión:** PMCID PMC7710100, PMC4942290, PMC3555465, PMC11495177 y literatura de espacios cervicales/hioides.

## Downs — disponible y completado en v0.12.6

Además del ángulo facial, plano mandibular, eje Y, plano oclusal y variables dentales, v0.12.6 incorpora:

- convexidad N–A/A–Pg: magnitud geométrica con signo según la posición de A respecto de N–Pg;
- plano A–B/N–Pg: magnitud aguda con signo anatómico explícito;
- ángulo interincisal.

La convención de signo se basa en el eje anatómico posterior→anterior de Frankfort y está desacoplada de cualquier valor normal.

**Fuente primaria:** Downs WB. *Variations in facial relationships: their significance in treatment and prognosis*. Am J Orthod. 1948; reproducciones metodológicas en literatura indexada, entre ella PMCID PMC6266314.

## Ricketts — núcleo reproducible disponible en v0.12.6

### Landmarks nuevos

- **Pt:** punto pterigoideo de Ricketts, definido en relación con el borde inferior del foramen redondo y pared posterior de la fisura pterigomaxilar.
- **Pm:** protuberance menti, transición de concavidad a convexidad del contorno anterior de la sínfisis.
- **DC:** referencia del centro/cuello condilar usada con Xi.
- **R1, R2, R3, R4:** límites para construir Xi.
- **Xi:** se construye como centro del rectángulo de la rama; no se exige marcarlo manualmente.

### Variables activas

- eje facial Ba–N/Pt–Gn;
- profundidad facial FH/N–Pg;
- plano mandibular FH/Go–Me;
- altura facial inferior ANS–Xi–Pm;
- arco mandibular DC–Xi/Xi–Pm;
- profundidad maxilar FH/N–A;
- convexidad A a N–Pg;
- longitud del corpus Xi–Pm;
- L1 a A–Pg en mm y °;
- U6 a PTV.

### VERT

El índice VERT combina componentes de Ricketts con referencias que cambian con el crecimiento. YomCeph v0.12.6 conserva los componentes crudos y **no produce una clasificación VERT automática sin una referencia etaria explícita**.

**Fuentes:** reproducciones de componentes/landmarks en PMCID PMC7486496 y PMC3971129; referencias relacionadas con VERT y edad en PMCID PMC10625683.

## COGS / Burstone — bloque de tejidos duros disponible en v0.12.6

El plano horizontal (HP) se construye a **7° respecto de SN** y se orienta de forma coherente con Frankfort. Se incorporaron U6 y L6 para las variables dentales/oclusales.

Variables implementadas:

- Ar–Ptm // HP, Ptm–N // HP;
- N–A–Pg;
- N–A // HP, N–B // HP, N–Pg // HP;
- N–ANS ⟂ HP, ANS–Gn ⟂ HP, PNS–N ⟂ HP;
- MP–HP;
- U1/U6 al piso nasal;
- L1/L6 al plano mandibular;
- PNS–ANS // HP;
- Ar–Go, Go–Pg, B–Pg // MP, Ar–Go–Gn;
- OP–HP, A–B // OP;
- U1–NF y L1–MP angulares.

Las tablas originales son específicas de sexo/población; YomCeph no las generaliza automáticamente.

**Fuente primaria:** Burstone CJ, James RB, Legan H, Murphy GA, Norton LA. *Cephalometrics for orthognathic surgery*. J Oral Surg. 1978;36:269–277. PMID 273073. Reproducciones metodológicas: PMCID PMC4252385, PMC3244091 y PMC3723291.

## Sassouni — núcleo estructural disponible en v0.12.6

Se añadieron landmarks para la dirección supraorbitaria/basal y el plano mandibular. Se implementan las divergencias entre:

- plano basal;
- plano palatino ANS–PNS;
- plano oclusal;
- plano mandibular.

El método histórico también usa un punto de convergencia **O** y arcos. Las fuentes describen una región/zona de convergencia y manuales posteriores proponen procedimientos gráficos, pero no se identificó una única construcción computacional suficientemente canónica para automatizar O sin introducir una decisión arbitraria. Por eso **O y los arcos siguen fuera del bloque activo**.

**Fuentes:** Sassouni V. *A roentgenographic cephalometric analysis of cephalo-facio-dental relationships*. Am J Orthod. 1955;41:735–764; *Sassouni Plus Analysis*, Ohlendorf Company, 1987.

## Bimler — núcleo verificable disponible en v0.12.6

La revisión del artículo de Bimler y del libro técnico permitió implementar un subconjunto con construcción clara en el sistema de Frankfort:

- F1: perfil superior N–A;
- F2: perfil inferior A–B;
- F3: inclinación mandibular Me–GoA;
- F4: inclinación maxilar ANS–PNS;
- F5: inclinación del clivus Cls–Cli;
- F7: inclinación S–N;
- ángulo de perfil F1+F2;
- ángulo basal superior F4+F5;
- ángulo basal inferior |F3|+|F4|;
- ángulo basal total;
- U1/FH, L1/FH e interincisal.

F6, F8–F10 y el correlómetro **no se automatizan** hasta disponer de una construcción completa inequívoca en las fuentes revisadas.

**Fuentes:** Bimler HP. *Bimler therapy. Part 1. Bimler cephalometric analysis*. J Clin Orthod. 1985;19(7):501–523. PMID 3861619. Bastien GB. *The Bimler Cephalometric Analysis*. Ortho Organizers; 1985.

## Sagittal G-triangle — disponible en v0.12.6

Se reproduce la construcción publicada:

1. unir Ba–G y Po–Or; su intersección es I;
2. usar la semirrecta Bo→I;
3. desde G construir la recta que forma 60° con Bo–I; su intersección determina X;
4. construir el triángulo equilátero invertido Bo–X–K;
5. calcular AXK y BXK con signo según la posición anterior/posterior respecto de X–K.

Para evitar colisión con el punto **G** de YEN/W, YomCeph denomina internamente **Gtri** a la glabela de tejido blando de este método.

Los rangos del artículo original proceden de adultos jóvenes del sur de China y no se aplican como norma universal a niños u otras poblaciones.

**Fuente:** Li B, Zhang Z, Lin X, Dong Y. *Sagittal Cephalometric Evaluation Without Point Nasion: Sagittal G-Triangle Analysis*. J Craniofac Surg. 2022;33(2):521–525. PMID 34669681; PMCID PMC8865203.

## Alexander — referencia, no análisis activado

La literatura localizada describe principalmente la Alexander Discipline como filosofía/técnica terapéutica. No se identificó un único análisis cefalométrico canónico comparable a Steiner que pueda codificarse sin inventar una definición.

## Ritucci–Burstone — otra proyección

El método publicado de asimetría usa radiografía **submentovertex (SMV)** y pares de landmarks bilaterales. No se ofrecerá dentro del flujo de una lateral única.

**Fuentes:** PMID 8074089; PMID 6584032.

## Investigación y elegibilidad

En investigación, el protocolo se activa sin abrir automáticamente la ficha del sujeto. Primero se abre la radiografía y se intenta el trazado. Al finalizar YomCeph evalúa:

- edad respecto del rango del protocolo;
- país/procedencia cuando se definió;
- presencia de todos los landmarks requeridos;
- calibración si existen variables lineales;
- causas radiográficas documentadas por el investigador.

Un caso excluido se conserva para trazabilidad y no cuenta como incluido.

## Estadística y exportación

Para los casos incluidos se calculan n válido, media, DE, mínimo y máximo. La prevalencia sólo se reporta cuando existe una regla categórica explícita y exporta su denominador. Excel incluye Datos, Descriptivos, Frecuencias, Prevalencias, Diccionario, Protocolo e Historial protocolo. SPSS recibe CSV UTF-8 y sintaxis `.sps`; no se crea un `.sav` falso.

## Referencias principales verificadas

1. Steiner CC. *Cephalometrics for you and me*. Am J Orthod. 1953.
2. Jacobson A. Wits appraisal. PMID 1054214.
3. Neela PK et al. YEN angle. PMID 19582259.
4. Bhad WA et al. W angle. PMID 21303811.
5. Björk–Jarabak. PMCID PMC6191777.
6. Solow B, Tallgren A. PMID 937521; revisión PMCID PMC4009738.
7. McNamara JA Jr. *A method of cephalometric evaluation*. Am J Orthod. 1984; PMCID PMC8018756.
8. Downs WB. *Variations in facial relationships*. Am J Orthod. 1948.
9. Ricketts: PMCID PMC7486496, PMC3971129, PMC10625683.
10. Burstone/COGS: PMID 273073; PMCID PMC4252385, PMC3244091, PMC3723291.
11. Sassouni V. *Am J Orthod*. 1955;41:735–764; *Sassouni Plus Analysis*, 1987.
12. Bimler HP. J Clin Orthod. 1985;19(7):501–523. PMID 3861619; Bastien GB, 1985.
13. Sagittal G-triangle: PMID 34669681; PMCID PMC8865203.
14. Ritucci–Burstone SMV: PMID 8074089; PMID 6584032.

**Estado v0.12.6:** disponibles los bloques reproducibles de Steiner, postura, Powell, Wits, Björk–Jarabak, YEN/W, Tweed, McNamara, vía aérea 2D descriptiva, Rocabado, Downs, Ricketts, COGS/Burstone, Sassouni estructural, Bimler y Sagittal G-triangle. Alexander permanece como referencia y Ritucci–Burstone como método de otra proyección.
