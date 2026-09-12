"""Extensiones científicas reproducibles para YomCeph Desktop v0.12.5.

Este módulo activa únicamente mediciones cuya construcción geométrica puede
expresarse de forma explícita con landmarks definidos. Las referencias
poblacionales no forman parte de la geometría y no se usan para elegir sectores
angulares. Ricketts completo, COGS completo, Sassouni, Bimler, Alexander y
Ritucci permanecen fuera de este bloque hasta disponer de una implementación
canónica y verificable para la proyección correspondiente.
"""

from __future__ import annotations

import math

import yomceph_scientific_catalog as catalog
from yomceph_v120_geometry import (
    acute_line_angle,
    directed_line_angle,
    distance,
    obtuse_line_angle,
    project_point_to_line,
)


NEW_POINTS = [
    ("C1sp", "C1 · arco posterior superior",
     "Marque el punto superior/posterior del arco posterior del atlas visible en la telerradiografía. Se usa para el espacio C0–C1."),
    ("C1ip", "C1 · arco posterior inferior",
     "Marque el punto inferior/posterior del arco posterior del atlas. Se usa con C2sp para el espacio C1–C2."),
    ("C2sp", "C2 · espinosa superior posterior",
     "Marque el punto superior/posterior de la apófisis espinosa de C2 usado para el espacio C1–C2."),
    ("UPhA", "Faringe superior · punto anterior",
     "Marque el punto del contorno posterior del paladar blando que produzca la menor distancia hacia la pared faríngea posterior."),
    ("UPhP", "Faringe superior · pared posterior",
     "Marque el punto correspondiente de la pared faríngea posterior para la menor distancia de la faringe superior."),
    ("LPhA", "Faringe inferior · punto anterior",
     "Marque la zona de intersección del borde posterior de la lengua con el borde inferior mandibular usada por McNamara para la anchura faríngea inferior."),
    ("LPhP", "Faringe inferior · pared posterior",
     "Marque el punto más próximo de la pared faríngea posterior para la anchura faríngea inferior."),
]


EXTENDED_MEASUREMENTS = {
    # Tweed: sectores definidos por la orientación anatómica de cada eje.
    "Tweed · FMA": dict(analysis="tweed", label="Tweed · FMA", unit="°", required=["Po", "Or", "Go", "Me"], status=catalog.STATUS_ACTIVE),
    "Tweed · FMIA": dict(analysis="tweed", label="Tweed · FMIA", unit="°", required=["Po", "Or", "L1a", "L1i"], status=catalog.STATUS_ACTIVE),
    "Tweed · IMPA": dict(analysis="tweed", label="Tweed · IMPA", unit="°", required=["Go", "Me", "L1a", "L1i"], status=catalog.STATUS_ACTIVE),

    # McNamara: núcleo esquelético y dentofacial reproducible. Las distancias
    # lineales requieren calibración; la app devuelve valor crudo sin norma
    # automática dependiente de edad/sexo.
    "McNamara · A–N⊥": dict(analysis="mcnamara", label="McNamara · A a N-perpendicular", unit="mm", required=["Po", "Or", "N", "A"], status=catalog.STATUS_ACTIVE),
    "McNamara · Pg–N⊥": dict(analysis="mcnamara", label="McNamara · Pogonion a N-perpendicular", unit="mm", required=["Po", "Or", "N", "Pg"], status=catalog.STATUS_ACTIVE),
    "McNamara · Co–A": dict(analysis="mcnamara", label="McNamara · longitud mediofacial Co–A", unit="mm", required=["Co", "A"], status=catalog.STATUS_ACTIVE),
    "McNamara · Co–Gn": dict(analysis="mcnamara", label="McNamara · longitud mandibular Co–Gn", unit="mm", required=["Co", "Gn"], status=catalog.STATUS_ACTIVE),
    "McNamara · diferencia maxilomandibular": dict(analysis="mcnamara", label="McNamara · Co–Gn − Co–A", unit="mm", required=["Co", "Gn", "A"], status=catalog.STATUS_ACTIVE),
    "McNamara · ANS–Me": dict(analysis="mcnamara", label="McNamara · altura facial inferior ANS–Me", unit="mm", required=["ANS", "Me"], status=catalog.STATUS_ACTIVE),
    "McNamara · FH–GoMe": dict(analysis="mcnamara", label="McNamara · plano mandibular FH/Go–Me", unit="°", required=["Po", "Or", "Go", "Me"], status=catalog.STATUS_ACTIVE),
    "McNamara · eje facial BaN–PtmGn": dict(analysis="mcnamara", label="McNamara · eje facial Ba–N / Ptm–Gn", unit="°", required=["Ba", "N", "Ptm", "Gn"], status=catalog.STATUS_ACTIVE),

    # Vía aérea: morfometría 2D descriptiva. No se asigna diagnóstico de
    # obstrucción/apnea ni una norma universal.
    "Vía aérea · faringe superior": dict(analysis="airway", label="Vía aérea · faringe superior", unit="mm", required=["UPhA", "UPhP"], status=catalog.STATUS_ACTIVE),
    "Vía aérea · faringe inferior": dict(analysis="airway", label="Vía aérea · faringe inferior", unit="mm", required=["LPhA", "LPhP"], status=catalog.STATUS_ACTIVE),

    # Rocabado / hioides: construcciones lineales explícitas.
    "Rocabado · C0–C1": dict(analysis="rocabado", label="Rocabado · espacio C0–C1", unit="mm", required=["PNS", "C0", "C1sp"], status=catalog.STATUS_ACTIVE),
    "Rocabado · C1–C2": dict(analysis="rocabado", label="Rocabado · espacio C1–C2", unit="mm", required=["C1ip", "C2sp"], status=catalog.STATUS_ACTIVE),
    "Rocabado · C3–RGn": dict(analysis="rocabado", label="Rocabado · C3–RGn", unit="mm", required=["C3ai", "RGn"], status=catalog.STATUS_ACTIVE),
    "Rocabado · C3–H": dict(analysis="rocabado", label="Rocabado · C3–H", unit="mm", required=["C3ai", "H"], status=catalog.STATUS_ACTIVE),
    "Rocabado · H–RGn": dict(analysis="rocabado", label="Rocabado · H–RGn", unit="mm", required=["H", "RGn"], status=catalog.STATUS_ACTIVE),
    "Rocabado · H a C3–RGn": dict(analysis="rocabado", label="Rocabado · distancia de H a C3–RGn", unit="mm", required=["C3ai", "RGn", "H"], status=catalog.STATUS_ACTIVE),

    # Downs: bloque cuyos sectores son geométricamente inequívocos. Los ángulos
    # de convexidad y AB-plane con signo se mantienen pendientes para no inventar
    # una convención de signo silenciosa.
    "Downs · ángulo facial": dict(analysis="downs", label="Downs · ángulo facial FH/N–Pg", unit="°", required=["Po", "Or", "N", "Pg"], status=catalog.STATUS_ACTIVE),
    "Downs · plano mandibular": dict(analysis="downs", label="Downs · plano mandibular Go–Gn/FH", unit="°", required=["Go", "Gn", "Po", "Or"], status=catalog.STATUS_ACTIVE),
    "Downs · eje Y": dict(analysis="downs", label="Downs · eje Y S–Gn/FH", unit="°", required=["S", "Gn", "Po", "Or"], status=catalog.STATUS_ACTIVE),
    "Downs · plano oclusal": dict(analysis="downs", label="Downs · plano oclusal/FH", unit="°", required=["OcP", "OcA", "Po", "Or"], status=catalog.STATUS_ACTIVE),
    "Downs · L1–OP": dict(analysis="downs", label="Downs · incisivo inferior/plano oclusal", unit="°", required=["L1a", "L1i", "OcP", "OcA"], status=catalog.STATUS_ACTIVE),
    "Downs · L1–MP": dict(analysis="downs", label="Downs · incisivo inferior/plano mandibular", unit="°", required=["L1a", "L1i", "Go", "Gn"], status=catalog.STATUS_ACTIVE),
    "Downs · U1 a A–Pg": dict(analysis="downs", label="Downs · incisivo superior a A–Pg", unit="mm", required=["U1i", "A", "Pg"], status=catalog.STATUS_ACTIVE),
}


REFERENCES = {
    "mcnamara": [
        "McNamara JA Jr. A method of cephalometric evaluation. Am J Orthod. 1984.",
        "McNamara analysis cephalometric parameters in White-Brazilians, Japanese and Japanese-Brazilians. PMCID: PMC8018756.",
    ],
    "downs": [
        "Downs WB. Variations in facial relationships: their significance in treatment and prognosis. Am J Orthod. 1948.",
        "Definitions of Downs variables reproduced in PMCID: PMC12949154.",
    ],
    "tweed": [
        "Tweed CH. The Frankfort-mandibular incisor angle in orthodontic diagnosis, treatment planning and prognosis. Angle Orthod.",
    ],
    "airway": [
        "McNamara upper/lower pharyngeal airway constructions; lateral cephalometric studies summarized in PMCID: PMC6562225.",
    ],
    "rocabado": [
        "Rocabado/Penning cranio-cervical and hyoid evaluation; methodological summaries include PMCID: PMC9229202 and PMC11495177.",
    ],
}


def install_catalog_extensions():
    """Mutates the shared catalog once; safe to call repeatedly."""
    seen = {item[0] for item in catalog.EXTRA_POINTS}
    for item in NEW_POINTS:
        if item[0] not in seen:
            catalog.EXTRA_POINTS.append(item)
            seen.add(item[0])
    catalog.MEASUREMENTS.update(EXTENDED_MEASUREMENTS)

    catalog.ANALYSES["tweed"].update(
        status=catalog.STATUS_ACTIVE,
        summary="Triángulo de Tweed FMA–FMIA–IMPA con sectores geométricos explícitos. Los valores crudos no dependen de una norma para calcularse.",
        missing_landmarks=[],
    )
    catalog.ANALYSES["mcnamara"].update(
        status=catalog.STATUS_ACTIVE,
        summary="Núcleo reproducible de McNamara: A/Pg a N-perpendicular, Co–A, Co–Gn, diferencia maxilomandibular, ANS–Me, plano mandibular y eje facial. Las referencias por edad/sexo no se aplican automáticamente.",
        missing_landmarks=["Co", "Ptm", "Ba"],
    )
    catalog.ANALYSES["airway"].update(
        status=catalog.STATUS_ACTIVE,
        summary="Anchuras faríngeas superior e inferior de McNamara como morfometría lateral 2D descriptiva. No diagnostica obstrucción ni apnea.",
        missing_landmarks=["UPhA", "UPhP", "LPhA", "LPhP"],
    )
    catalog.ANALYSES["rocabado"].update(
        status=catalog.STATUS_ACTIVE,
        summary="Ángulo MGP–OP y bloque lineal C0–C1, C1–C2 y triángulo hioideo con geometría explícita. Las referencias históricas se mantienen separadas del valor crudo.",
        missing_landmarks=["C1sp", "C1ip", "C2sp", "H", "C3ai", "RGn"],
    )
    catalog.ANALYSES["downs"].update(
        status=catalog.STATUS_ACTIVE,
        summary="Bloque reproducible de Downs: ángulo facial, plano mandibular, eje Y, plano oclusal y variables dentales. Convexidad y AB-plane con signo permanecen en validación hasta fijar la convención de signo explícita.",
        missing_landmarks=[],
    )

    for key, values in REFERENCES.items():
        current = list(catalog.REFERENCES.get(key, []))
        for value in values:
            if value not in current:
                current.append(value)
        catalog.REFERENCES[key] = current


install_catalog_extensions()


def _signed_along_line(point, origin, line_a, line_b, mm_per_pixel):
    """Signed projection along line_a→line_b; reflection invariant."""
    if not mm_per_pixel or mm_per_pixel <= 0:
        return None
    dx = line_b[0] - line_a[0]
    dy = line_b[1] - line_a[1]
    den = math.hypot(dx, dy)
    if den <= 1e-12:
        return None
    ux, uy = dx / den, dy / den
    return ((point[0] - origin[0]) * ux + (point[1] - origin[1]) * uy) * mm_per_pixel


def _perpendicular_distance(point, a, b, mm_per_pixel):
    if not mm_per_pixel or mm_per_pixel <= 0:
        return None
    foot = project_point_to_line(point, a, b)
    if foot is None:
        return None
    return distance(point, foot) * mm_per_pixel


def extended_values(points, mm_per_pixel=None):
    p = points or {}
    r = {}

    # Tweed. Po→Or and Go/Me/Gn are posterior→anterior; L1a→L1i is root→crown.
    if all(k in p for k in ("Po", "Or", "Go", "Me")):
        r["Tweed · FMA"] = acute_line_angle(p["Po"], p["Or"], p["Go"], p["Me"])
    if all(k in p for k in ("Po", "Or", "L1a", "L1i")):
        r["Tweed · FMIA"] = directed_line_angle(p["Po"], p["Or"], p["L1a"], p["L1i"])
    if all(k in p for k in ("Go", "Me", "L1a", "L1i")):
        r["Tweed · IMPA"] = directed_line_angle(p["Go"], p["Me"], p["L1a"], p["L1i"])

    # McNamara. N-perpendicular is perpendicular to FH; signed displacement from
    # it equals projection of point-N along posterior→anterior FH.
    if all(k in p for k in ("Po", "Or", "N", "A")):
        r["McNamara · A–N⊥"] = _signed_along_line(p["A"], p["N"], p["Po"], p["Or"], mm_per_pixel)
    if all(k in p for k in ("Po", "Or", "N", "Pg")):
        r["McNamara · Pg–N⊥"] = _signed_along_line(p["Pg"], p["N"], p["Po"], p["Or"], mm_per_pixel)
    if mm_per_pixel and mm_per_pixel > 0:
        if all(k in p for k in ("Co", "A")):
            r["McNamara · Co–A"] = distance(p["Co"], p["A"]) * mm_per_pixel
        if all(k in p for k in ("Co", "Gn")):
            r["McNamara · Co–Gn"] = distance(p["Co"], p["Gn"]) * mm_per_pixel
        if all(k in p for k in ("Co", "Gn", "A")):
            r["McNamara · diferencia maxilomandibular"] = (
                distance(p["Co"], p["Gn"]) - distance(p["Co"], p["A"])
            ) * mm_per_pixel
        if all(k in p for k in ("ANS", "Me")):
            r["McNamara · ANS–Me"] = distance(p["ANS"], p["Me"]) * mm_per_pixel
    if all(k in p for k in ("Po", "Or", "Go", "Me")):
        r["McNamara · FH–GoMe"] = acute_line_angle(p["Po"], p["Or"], p["Go"], p["Me"])
    if all(k in p for k in ("Ba", "N", "Ptm", "Gn")):
        r["McNamara · eje facial BaN–PtmGn"] = directed_line_angle(p["Ba"], p["N"], p["Ptm"], p["Gn"])

    # Airway / Rocabado linear blocks.
    if mm_per_pixel and mm_per_pixel > 0:
        for key, a, b in (
            ("Vía aérea · faringe superior", "UPhA", "UPhP"),
            ("Vía aérea · faringe inferior", "LPhA", "LPhP"),
            ("Rocabado · C1–C2", "C1ip", "C2sp"),
            ("Rocabado · C3–RGn", "C3ai", "RGn"),
            ("Rocabado · C3–H", "C3ai", "H"),
            ("Rocabado · H–RGn", "H", "RGn"),
        ):
            if a in p and b in p:
                r[key] = distance(p[a], p[b]) * mm_per_pixel
        if all(k in p for k in ("PNS", "C0", "C1sp")):
            r["Rocabado · C0–C1"] = _perpendicular_distance(p["C1sp"], p["PNS"], p["C0"], mm_per_pixel)
        if all(k in p for k in ("C3ai", "RGn", "H")):
            r["Rocabado · H a C3–RGn"] = _perpendicular_distance(p["H"], p["C3ai"], p["RGn"], mm_per_pixel)

        if all(k in p for k in ("U1i", "A", "Pg")):
            r["Downs · U1 a A–Pg"] = _perpendicular_distance(p["U1i"], p["A"], p["Pg"], mm_per_pixel)

    # Downs: sectores anatómicamente definidos; no hay selección por norma.
    if all(k in p for k in ("Po", "Or", "N", "Pg")):
        r["Downs · ángulo facial"] = directed_line_angle(p["Po"], p["Or"], p["N"], p["Pg"])
    if all(k in p for k in ("Go", "Gn", "Po", "Or")):
        r["Downs · plano mandibular"] = acute_line_angle(p["Go"], p["Gn"], p["Po"], p["Or"])
    if all(k in p for k in ("S", "Gn", "Po", "Or")):
        r["Downs · eje Y"] = directed_line_angle(p["Po"], p["Or"], p["S"], p["Gn"])
    if all(k in p for k in ("OcP", "OcA", "Po", "Or")):
        r["Downs · plano oclusal"] = acute_line_angle(p["OcP"], p["OcA"], p["Po"], p["Or"])
    if all(k in p for k in ("L1a", "L1i", "OcP", "OcA")):
        r["Downs · L1–OP"] = directed_line_angle(p["OcP"], p["OcA"], p["L1a"], p["L1i"])
    if all(k in p for k in ("L1a", "L1i", "Go", "Gn")):
        r["Downs · L1–MP"] = directed_line_angle(p["Go"], p["Gn"], p["L1a"], p["L1i"])

    return {key: value for key, value in r.items() if value is not None and math.isfinite(value)}
