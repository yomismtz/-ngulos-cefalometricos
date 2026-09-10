# YomCeph — Guía reproducible de colocación de puntos

Actualización: 2026-09-10.

Esta guía documenta las convenciones que usa la app. Los dibujos integrados son **esquemas orientativos, no a escala**, y nunca intervienen en los cálculos. La ubicación final debe hacerse sobre la anatomía radiográfica visible.

## Flujo de trabajo

1. Elegir análisis.
2. Seleccionar radiografía.
3. Asignar nombre/número del estudio y datos diferenciadores del paciente.
4. Calibrar solo cuando el módulo necesite distancias lineales y exista una referencia válida.
5. Seleccionar explícitamente cada punto y colocarlo con un toque. La selección no avanza sola.
6. Un dedo arrastra la radiografía; pellizco amplía/reduce. Para corregir un punto ya colocado, mantener presionado el punto y arrastrarlo con la lupa.
7. El informe puede ser parcial: solo aparecen las medidas para las que estén presentes todos los puntos necesarios.

## Steiner / Tweed

Los puntos S, N, A, B, Po, Or, ENA/PNS, Ar, Go, Me y Gn siguen las definiciones cefalométricas convencionales. Para el plano oclusal de Steiner, YomCeph adopta un punto anterior equidistante entre los bordes incisales superior/inferior y un punto posterior en la intercuspidación/superposición de los primeros molares.

Referencia sobre plano oclusal de Steiner:
- https://www.scielo.cl/scielo.php?pid=S0719-01072015000300010&script=sci_arttext

## Postura cervical / Solow

YomCeph usa puntos compartidos para no marcar dos veces el mismo sitio:
- **Cv2tg**: punto de tangencia sobre el contorno dorsal de la odontoides de C2.
- **Cv2ip**: punto más posteroinferior del cuerpo de C2.
- **Cv4ip**: punto más posteroinferior del cuerpo de C4.
- **OPT** = Cv2tg–Cv2ip.
- **CVT** = Cv2tg–Cv4ip.

Referencias:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC5676314/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC4792970/

La antigua medición “McGregor–C4” se retiró porque la implementación existente dependía de dos puntos C4-1/C4-2 sin definición anatómica reproducible ni respaldo suficiente para el rango usado.

## Rocabado / triángulo hioideo

- H: punto más superior y anterior del cuerpo del hioides.
- C3: punto anteroinferior del cuerpo de C3.
- RGn: punto posteroinferior de la sínfisis.
- C0/Occipital + ENP: línea de McGregor.
- La profundidad cervical se obtiene respecto de la tangente posterior C2–C7, con la concavidad medida cerca de C4.

## Vía aérea

Convención adoptada por la app:
- **AD1**: punto del tejido adenoideo/pared posterior sobre la línea ENP(PNS)–Ba; PNS–AD1 es la distancia desde ENP al punto más cercano de tejido adenoideo sobre esa línea.
- **AD2**: punto sobre la línea que pasa por ENP y es perpendicular a S–Ba; PNS–AD2 es la distancia desde ENP al tejido adenoideo más cercano sobre esa perpendicular.
- **McNamara superior**: distancia mínima desde el contorno posterior del paladar blando a la pared faríngea posterior.
- **McNamara inferior**: distancia mínima desde el punto donde el contorno posterior de la lengua cruza el borde inferior mandibular a la pared faríngea posterior.

Referencias:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC9128391/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC5035718/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC3520347/

**AD3 Uptp–Adenoides se retiró.** No se mantuvo una medida cuya construcción y valores dependían de una “tabla aportada” que no forma parte de la app y cuya geometría no pudo verificarse de manera reproducible con las fuentes revisadas.

## Levandoski

La línea 1 es la línea media vertical maxilar que pasa por el septum nasal. Las líneas horizontales clásicas son perpendiculares a esa línea y pasan/tangencian el borde inferior de la sínfisis, la punta condilar y la punta coronoidea. Cd, Go y Kr/Cor se marcan de forma homóloga en ambos lados.

Referencias:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC5052233/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC9157585/

## Powell

Los puntos de tejidos blandos G', N', Pr, Pg', Me' y C se conservan como referencias del perfil. El esquema de la app es solo un localizador aproximado y no sustituye la identificación del contorno blando real.
