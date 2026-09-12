"""Remaining scientifically reproducible cephalometric blocks for YomCeph Desktop v0.12.6.

The module keeps geometric construction separate from population reference values.
Only measurements with an explicit, reproducible construction on a lateral
cephalogram are activated. Alexander remains reference-only and
Ritucci–Burstone remains an SMV/submentovertex method.
"""

from __future__ import annotations

import math

import yomceph_scientific_catalog as catalog
from yomceph_v120_geometry import (
    acute_line_angle,
    angle3,
    directed_line_angle,
    distance,
    obtuse_line_angle,
    project_point_to_line,
)

EPS = 1e-12

NEW_POINTS = [
    ("Pt", "Ricketts · punto pterigoideo (Pt)",
     "Intersección del borde inferior del foramen redondo con la pared posterior de la fisura pterigomaxilar. No confundir con Ptm."),
    ("Pm", "Ricketts · protuberancia menti (Pm)",
     "Punto del borde anterior de la sínfisis donde la curvatura cambia de cóncava a convexa, entre B y Pg."),
    ("DC", "Ricketts · centro condilar (DC)",
     "Punto de bisección del cuello/proceso condilar usado por Ricketts para el eje condilar DC–Xi; se localiza respecto de Ba–N."),
    ("R1", "Ricketts · R1",
     "Punto más profundo del borde anterior de la rama, aproximadamente a mitad entre las curvaturas superior e inferior."),
    ("R2", "Ricketts · R2",
     "Punto del borde posterior de la rama directamente opuesto a R1."),
    ("R3", "Ricketts · R3",
     "Punto más profundo de la escotadura sigmoidea, aproximadamente a mitad entre sus curvaturas anterior y posterior."),
    ("R4", "Ricketts · R4",
     "Punto del borde inferior de la rama directamente opuesto a R3."),
    ("U6", "Primer molar superior · referencia COGS",
     "Marque la cúspide mesiobucal / referencia oclusal del primer molar superior usada en el trazado COGS."),
    ("L6", "Primer molar inferior · referencia COGS",
     "Marque la cúspide mesiobucal / referencia oclusal del primer molar inferior usada en el trazado COGS."),
    ("SasCl", "Sassouni · clinoidale anterior (Cl)",
     "Punto superior de la apófisis clinoides anterior utilizado para definir la dirección supraorbitaria."),
    ("SasRo", "Sassouni · techo orbitario (Ro)",
     "Punto más superior del contorno del techo de la órbita; con Cl define el plano supraorbitario."),
    ("SasSi", "Sassouni · sella inferior (Si)",
     "Punto más inferior del contorno de la silla turca. El plano basal es paralelo a Cl–Ro y tangente/pasante por Si."),
    ("SasMbP", "Sassouni · punto posterior del plano mandibular",
     "Punto más inferior de la rama, inmediatamente posterior a la escotadura antegonial; con Me define la base mandibular de Sassouni."),
    ("GoA", "Bimler · punto antegonial (GoA)",
     "Punto más alto de la escotadura antegonial. Con Me define la inclinación mandibular (factor 3) de Bimler."),
    ("Cls", "Bimler · clivion superior (Cls)",
     "Referencia superior para la tangente/línea del clivus en el análisis de Bimler."),
    ("Cli", "Bimler · clivion inferior (Cli)",
     "Referencia inferior para la tangente/línea del clivus en el análisis de Bimler."),
    ("Gtri", "G-triangle · glabela de tejido blando (G)",
     "Punto medio más prominente de la frente en tejido blando usado por el Sagittal G-triangle. Es distinto del punto G de YEN/W."),
]

RICKETTS_REQ = ["Po", "Or", "R1", "R2", "R3", "R4"]

EXTENDED_MEASUREMENTS = {
    "Ricketts · eje facial": dict(analysis="ricketts", label="Ricketts · eje facial Ba–N/Pt–Gn", unit="°", required=["Ba", "N", "Pt", "Gn"], status=catalog.STATUS_ACTIVE),
    "Ricketts · profundidad facial": dict(analysis="ricketts", label="Ricketts · profundidad facial FH/N–Pg", unit="°", required=["Po", "Or", "N", "Pg"], status=catalog.STATUS_ACTIVE),
    "Ricketts · plano mandibular": dict(analysis="ricketts", label="Ricketts · plano mandibular FH/Go–Me", unit="°", required=["Po", "Or", "Go", "Me"], status=catalog.STATUS_ACTIVE),
    "Ricketts · altura facial inferior": dict(analysis="ricketts", label="Ricketts · altura facial inferior ANS–Xi–Pm", unit="°", required=RICKETTS_REQ + ["ANS", "Pm"], status=catalog.STATUS_ACTIVE),
    "Ricketts · arco mandibular": dict(analysis="ricketts", label="Ricketts · arco mandibular DC–Xi/Xi–Pm", unit="°", required=RICKETTS_REQ + ["DC", "Pm"], status=catalog.STATUS_ACTIVE),
    "Ricketts · profundidad maxilar": dict(analysis="ricketts", label="Ricketts · profundidad maxilar FH/N–A", unit="°", required=["Po", "Or", "N", "A"], status=catalog.STATUS_ACTIVE),
    "Ricketts · convexidad A–NPg": dict(analysis="ricketts", label="Ricketts · convexidad A a N–Pg", unit="mm", required=["Po", "Or", "N", "A", "Pg"], status=catalog.STATUS_ACTIVE),
    "Ricketts · longitud corpus Xi–Pm": dict(analysis="ricketts", label="Ricketts · longitud del cuerpo Xi–Pm", unit="mm", required=RICKETTS_REQ + ["Pm"], status=catalog.STATUS_ACTIVE),
    "Ricketts · L1 a A–Pg (mm)": dict(analysis="ricketts", label="Ricketts · incisivo inferior a A–Pg", unit="mm", required=["Po", "Or", "L1i", "A", "Pg"], status=catalog.STATUS_ACTIVE),
    "Ricketts · L1/A–Pg (°)": dict(analysis="ricketts", label="Ricketts · inclinación L1/A–Pg", unit="°", required=["L1a", "L1i", "A", "Pg"], status=catalog.STATUS_ACTIVE),
    "Ricketts · U6 a PTV": dict(analysis="ricketts", label="Ricketts · molar superior a PTV", unit="mm", required=["Po", "Or", "Pt", "U6"], status=catalog.STATUS_ACTIVE),

    "COGS · Ar–Ptm // HP": dict(analysis="cogs", label="COGS · Ar–Ptm paralelo a HP", unit="mm", required=["S", "N", "Po", "Or", "Ar", "Ptm"], status=catalog.STATUS_ACTIVE),
    "COGS · Ptm–N // HP": dict(analysis="cogs", label="COGS · Ptm–N paralelo a HP", unit="mm", required=["S", "N", "Po", "Or", "Ptm"], status=catalog.STATUS_ACTIVE),
    "COGS · N–A–Pg": dict(analysis="cogs", label="COGS · convexidad N–A–Pg", unit="°", required=["Po", "Or", "N", "A", "Pg"], status=catalog.STATUS_ACTIVE),
    "COGS · N–A // HP": dict(analysis="cogs", label="COGS · N–A paralelo a HP", unit="mm", required=["S", "N", "Po", "Or", "A"], status=catalog.STATUS_ACTIVE),
    "COGS · N–B // HP": dict(analysis="cogs", label="COGS · N–B paralelo a HP", unit="mm", required=["S", "N", "Po", "Or", "B"], status=catalog.STATUS_ACTIVE),
    "COGS · N–Pg // HP": dict(analysis="cogs", label="COGS · N–Pg paralelo a HP", unit="mm", required=["S", "N", "Po", "Or", "Pg"], status=catalog.STATUS_ACTIVE),
    "COGS · N–ANS ⟂ HP": dict(analysis="cogs", label="COGS · N–ANS perpendicular a HP", unit="mm", required=["S", "N", "Po", "Or", "ANS"], status=catalog.STATUS_ACTIVE),
    "COGS · ANS–Gn ⟂ HP": dict(analysis="cogs", label="COGS · ANS–Gn perpendicular a HP", unit="mm", required=["S", "N", "Po", "Or", "ANS", "Gn"], status=catalog.STATUS_ACTIVE),
    "COGS · PNS–N ⟂ HP": dict(analysis="cogs", label="COGS · PNS–N perpendicular a HP", unit="mm", required=["S", "N", "Po", "Or", "PNS"], status=catalog.STATUS_ACTIVE),
    "COGS · MP–HP": dict(analysis="cogs", label="COGS · plano mandibular–HP", unit="°", required=["S", "N", "Po", "Or", "Go", "Me"], status=catalog.STATUS_ACTIVE),
    "COGS · U1–NF ⟂": dict(analysis="cogs", label="COGS · altura U1 a piso nasal", unit="mm", required=["U1i", "ANS", "PNS"], status=catalog.STATUS_ACTIVE),
    "COGS · U6–NF ⟂": dict(analysis="cogs", label="COGS · altura U6 a piso nasal", unit="mm", required=["U6", "ANS", "PNS"], status=catalog.STATUS_ACTIVE),
    "COGS · L1–MP ⟂": dict(analysis="cogs", label="COGS · altura L1 a plano mandibular", unit="mm", required=["L1i", "Go", "Me"], status=catalog.STATUS_ACTIVE),
    "COGS · L6–MP ⟂": dict(analysis="cogs", label="COGS · altura L6 a plano mandibular", unit="mm", required=["L6", "Go", "Me"], status=catalog.STATUS_ACTIVE),
    "COGS · PNS–ANS // HP": dict(analysis="cogs", label="COGS · longitud maxilar PNS–ANS paralela a HP", unit="mm", required=["S", "N", "Po", "Or", "PNS", "ANS"], status=catalog.STATUS_ACTIVE),
    "COGS · Ar–Go": dict(analysis="cogs", label="COGS · longitud de rama Ar–Go", unit="mm", required=["Ar", "Go"], status=catalog.STATUS_ACTIVE),
    "COGS · Go–Pg": dict(analysis="cogs", label="COGS · longitud mandibular Go–Pg", unit="mm", required=["Go", "Pg"], status=catalog.STATUS_ACTIVE),
    "COGS · B–Pg // MP": dict(analysis="cogs", label="COGS · B–Pg paralelo a plano mandibular", unit="mm", required=["B", "Pg", "Go", "Me"], status=catalog.STATUS_ACTIVE),
    "COGS · Ar–Go–Gn": dict(analysis="cogs", label="COGS · ángulo gonial Ar–Go–Gn", unit="°", required=["Ar", "Go", "Gn"], status=catalog.STATUS_ACTIVE),
    "COGS · OP–HP": dict(analysis="cogs", label="COGS · plano oclusal–HP", unit="°", required=["S", "N", "Po", "Or", "U6", "L6", "L1i", "L1a"], status=catalog.STATUS_ACTIVE),
    "COGS · A–B // OP": dict(analysis="cogs", label="COGS · A–B paralelo al plano oclusal", unit="mm", required=["A", "B", "U6", "L6", "L1i", "L1a"], status=catalog.STATUS_ACTIVE),
    "COGS · U1–NF (°)": dict(analysis="cogs", label="COGS · inclinación U1/piso nasal", unit="°", required=["U1a", "U1i", "ANS", "PNS"], status=catalog.STATUS_ACTIVE),
    "COGS · L1–MP (°)": dict(analysis="cogs", label="COGS · inclinación L1/plano mandibular", unit="°", required=["L1a", "L1i", "Go", "Me"], status=catalog.STATUS_ACTIVE),

    "Sassouni · basal–palatino": dict(analysis="sassouni", label="Sassouni · divergencia basal–palatino", unit="°", required=["SasCl", "SasRo", "SasSi", "PNS", "ANS"], status=catalog.STATUS_ACTIVE),
    "Sassouni · basal–oclusal": dict(analysis="sassouni", label="Sassouni · divergencia basal–oclusal", unit="°", required=["SasCl", "SasRo", "SasSi", "U6", "L6", "U1i", "L1i"], status=catalog.STATUS_ACTIVE),
    "Sassouni · basal–mandibular": dict(analysis="sassouni", label="Sassouni · divergencia basal–mandibular", unit="°", required=["SasCl", "SasRo", "SasSi", "SasMbP", "Me"], status=catalog.STATUS_ACTIVE),
    "Sassouni · palatino–oclusal": dict(analysis="sassouni", label="Sassouni · divergencia palatino–oclusal", unit="°", required=["PNS", "ANS", "U6", "L6", "U1i", "L1i"], status=catalog.STATUS_ACTIVE),
    "Sassouni · palatino–mandibular": dict(analysis="sassouni", label="Sassouni · divergencia palatino–mandibular", unit="°", required=["PNS", "ANS", "SasMbP", "Me"], status=catalog.STATUS_ACTIVE),
    "Sassouni · oclusal–mandibular": dict(analysis="sassouni", label="Sassouni · divergencia oclusal–mandibular", unit="°", required=["U6", "L6", "U1i", "L1i", "SasMbP", "Me"], status=catalog.STATUS_ACTIVE),

    "Bimler · F1 perfil superior": dict(analysis="bimler", label="Bimler · F1 ángulo superior del perfil", unit="°", required=["Po", "Or", "N", "A"], status=catalog.STATUS_ACTIVE),
    "Bimler · F2 perfil inferior": dict(analysis="bimler", label="Bimler · F2 ángulo inferior del perfil", unit="°", required=["Po", "Or", "A", "B"], status=catalog.STATUS_ACTIVE),
    "Bimler · F3 inclinación mandibular": dict(analysis="bimler", label="Bimler · F3 inclinación mandibular", unit="°", required=["Po", "Or", "Me", "GoA"], status=catalog.STATUS_ACTIVE),
    "Bimler · F4 inclinación maxilar": dict(analysis="bimler", label="Bimler · F4 inclinación maxilar", unit="°", required=["Po", "Or", "PNS", "ANS"], status=catalog.STATUS_ACTIVE),
    "Bimler · F5 inclinación clivus": dict(analysis="bimler", label="Bimler · F5 inclinación del clivus", unit="°", required=["Po", "Or", "Cls", "Cli"], status=catalog.STATUS_ACTIVE),
    "Bimler · F7 inclinación SN": dict(analysis="bimler", label="Bimler · F7 inclinación de S–N", unit="°", required=["Po", "Or", "S", "N"], status=catalog.STATUS_ACTIVE),
    "Bimler · ángulo de perfil": dict(analysis="bimler", label="Bimler · ángulo de perfil F1+F2", unit="°", required=["Po", "Or", "N", "A", "B"], status=catalog.STATUS_ACTIVE),
    "Bimler · ángulo basal superior": dict(analysis="bimler", label="Bimler · ángulo basal superior F4+F5", unit="°", required=["Po", "Or", "PNS", "ANS", "Cls", "Cli"], status=catalog.STATUS_ACTIVE),
    "Bimler · ángulo basal inferior": dict(analysis="bimler", label="Bimler · ángulo basal inferior |F3|+|F4|", unit="°", required=["Po", "Or", "Me", "GoA", "PNS", "ANS"], status=catalog.STATUS_ACTIVE),
    "Bimler · ángulo basal total": dict(analysis="bimler", label="Bimler · ángulo basal total", unit="°", required=["Po", "Or", "Me", "GoA", "PNS", "ANS", "Cls", "Cli"], status=catalog.STATUS_ACTIVE),
    "Bimler · U1/FH": dict(analysis="bimler", label="Bimler · incisivo superior/FH", unit="°", required=["Po", "Or", "U1a", "U1i"], status=catalog.STATUS_ACTIVE),
    "Bimler · L1/FH": dict(analysis="bimler", label="Bimler · incisivo inferior/FH", unit="°", required=["Po", "Or", "L1a", "L1i"], status=catalog.STATUS_ACTIVE),
    "Bimler · interincisal": dict(analysis="bimler", label="Bimler · ángulo interincisal", unit="°", required=["U1a", "U1i", "L1a", "L1i"], status=catalog.STATUS_ACTIVE),

    "G-triangle · AXK": dict(analysis="g_triangle", label="Sagittal G-triangle · AXK", unit="°", required=["Ba", "Bo", "Po", "Or", "Gtri", "A"], status=catalog.STATUS_ACTIVE),
    "G-triangle · BXK": dict(analysis="g_triangle", label="Sagittal G-triangle · BXK", unit="°", required=["Ba", "Bo", "Po", "Or", "Gtri", "B"], status=catalog.STATUS_ACTIVE),

    "Downs · convexidad N–A–Pg": dict(analysis="downs", label="Downs · ángulo de convexidad N–A/A–Pg", unit="°", required=["Po", "Or", "N", "A", "Pg"], status=catalog.STATUS_ACTIVE),
    "Downs · plano A–B": dict(analysis="downs", label="Downs · ángulo plano A–B / N–Pg", unit="°", required=["Po", "Or", "A", "B", "N", "Pg"], status=catalog.STATUS_ACTIVE),
    "Downs · interincisal": dict(analysis="downs", label="Downs · ángulo interincisal", unit="°", required=["U1a", "U1i", "L1a", "L1i"], status=catalog.STATUS_ACTIVE),
}

REFERENCES = {
    "ricketts": [
        "Ricketts RM. Bioprogressive Therapy / cephalometric analysis; raw components corroborated in PMCID: PMC7486496 and PMC3971129.",
        "VERT components and age-dependent references corroborated in PMCID: PMC10625683.",
    ],
    "cogs": [
        "Burstone CJ, James RB, Legan H, Murphy GA, Norton LA. Cephalometrics for orthognathic surgery. J Oral Surg. 1978;36:269-277. PMID:273073.",
        "Hard-tissue variables and 7-degree horizontal plane reproduced in PMCID: PMC4252385, PMC3244091, PMC3723291.",
    ],
    "sassouni": [
        "Sassouni V. A roentgenographic cephalometric analysis of cephalo-facio-dental relationships. Am J Orthod. 1955;41:735-764.",
        "Sassouni Plus Analysis. Ohlendorf Company, 1987.",
    ],
    "bimler": [
        "Bimler HP. Bimler therapy. Part 1. Bimler cephalometric analysis. J Clin Orthod. 1985;19(7):501-523. PMID:3861619.",
        "Bastien GB. The Bimler Cephalometric Analysis. Ortho Organizers; 1985.",
    ],
    "g_triangle": [
        "Li B, Zhang Z, Lin X, Dong Y. Sagittal Cephalometric Evaluation Without Point Nasion: Sagittal G-Triangle Analysis. J Craniofac Surg. 2022;33(2):521-525. PMID:34669681; PMCID:PMC8865203.",
    ],
    "downs": [
        "Downs WB. Variations in facial relationships: their significance in treatment and prognosis. Am J Orthod. 1948.",
        "Downs variable definitions corroborated in PMCID: PMC12949154 and PMC6266314.",
    ],
}


def _vec(a, b):
    return b[0] - a[0], b[1] - a[1]


def _add(a, v, scale=1.0):
    return a[0] + v[0] * scale, a[1] + v[1] * scale


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def _cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def _norm(v):
    return math.hypot(v[0], v[1])


def _unit_vec(v):
    n = _norm(v)
    if n <= EPS:
        return None
    return v[0] / n, v[1] / n


def _unit(a, b):
    return _unit_vec(_vec(a, b))


def _rotate(v, degrees):
    r = math.radians(degrees)
    c, s = math.cos(r), math.sin(r)
    return v[0] * c - v[1] * s, v[0] * s + v[1] * c


def _mid(a, b):
    return (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0


def _line_intersection(a, b, c, d):
    r = _vec(a, b)
    s = _vec(c, d)
    den = _cross(r, s)
    if abs(den) <= EPS:
        return None
    qmp = c[0] - a[0], c[1] - a[1]
    t = _cross(qmp, s) / den
    u = _cross(qmp, r) / den
    return _add(a, r, t), t, u


def anatomical_basis(points):
    """Return Frankfort anterior unit vector and an image-independent inferior vector."""
    p = points or {}
    if "Po" not in p or "Or" not in p:
        return None
    anterior = _unit(p["Po"], p["Or"])
    if anterior is None:
        return None
    candidate = (-anterior[1], anterior[0])
    opposite = (-candidate[0], -candidate[1])
    pairs = [
        ("N", "Me"), ("N", "Gn"), ("N", "B"), ("S", "Me"),
        ("Gtri", "A"), ("Gtri", "B"), ("Or", "Me"), ("Ba", "Gn"),
    ]
    inferior = None
    for upper, lower in pairs:
        if upper not in p or lower not in p:
            continue
        delta = _vec(p[upper], p[lower])
        value = _dot(delta, candidate)
        if abs(value) > EPS:
            inferior = candidate if value > 0 else opposite
            break
    if inferior is None:
        inferior = candidate if candidate[1] >= 0 else opposite
    return anterior, inferior


def _signed_distance(point, a, b, sign_axis, mm_per_pixel=1.0):
    foot = project_point_to_line(point, a, b)
    if foot is None:
        return None
    mag = distance(point, foot) * mm_per_pixel
    side = _dot(_vec(foot, point), sign_axis)
    if abs(side) <= EPS:
        return 0.0
    return mag if side > 0 else -mag


def _signed_convexity_angle(n, a, pg, anterior):
    raw = angle3(n, a, pg)
    if raw is None:
        return None
    magnitude = abs(180.0 - raw)
    signed = _signed_distance(a, n, pg, anterior, 1.0)
    if signed is None or abs(signed) <= EPS:
        return 0.0
    return magnitude if signed > 0 else -magnitude


def _signed_ab_plane_angle(a, b, n, pg, anterior):
    magnitude = acute_line_angle(a, b, n, pg)
    if magnitude is None:
        return None
    shift = _dot(_vec(a, b), anterior)
    if abs(shift) <= EPS:
        return 0.0
    return magnitude if shift > 0 else -magnitude


def _signed_vertical_inclination(a, b, anterior, positive_when_anterior=True):
    theta = acute_line_angle((0.0, 0.0), anterior, a, b)
    if theta is None:
        return None
    magnitude = abs(90.0 - theta)
    shift = _dot(_vec(a, b), anterior)
    sign = 1.0 if shift >= 0 else -1.0
    if not positive_when_anterior:
        sign *= -1.0
    return sign * magnitude


def _signed_plane_inclination(posterior, anterior_point, fh_u, inferior):
    magnitude = acute_line_angle((0.0, 0.0), fh_u, posterior, anterior_point)
    if magnitude is None:
        return None
    vertical = _dot(_vec(posterior, anterior_point), inferior)
    if abs(vertical) <= EPS:
        return 0.0
    return magnitude if vertical > 0 else -magnitude


def xi_point(points):
    """Construct Ricketts Xi as the center of the R1/R2/R3/R4 ramus rectangle."""
    p = points or {}
    if not all(k in p for k in ("Po", "Or", "R1", "R2", "R3", "R4")):
        return None
    basis = anatomical_basis(p)
    if basis is None:
        return None
    u, v = basis
    origin = p["Po"]
    x1 = _dot(_vec(origin, p["R1"]), u)
    x2 = _dot(_vec(origin, p["R2"]), u)
    y3 = _dot(_vec(origin, p["R3"]), v)
    y4 = _dot(_vec(origin, p["R4"]), v)
    x = (x1 + x2) / 2.0
    y = (y3 + y4) / 2.0
    return origin[0] + u[0] * x + v[0] * y, origin[1] + u[1] * x + v[1] * y


def burstone_hp_direction(points):
    """Construct COGS HP direction: 7 degrees from SN, choosing the FH-consistent branch."""
    p = points or {}
    if not all(k in p for k in ("S", "N", "Po", "Or")):
        return None
    sn = _unit(p["S"], p["N"])
    fh = _unit(p["Po"], p["Or"])
    if sn is None or fh is None:
        return None
    candidates = [_rotate(sn, 7.0), _rotate(sn, -7.0)]
    candidate = max(candidates, key=lambda v: _dot(v, fh))
    if _dot(candidate, fh) < 0:
        candidate = (-candidate[0], -candidate[1])
    return candidate


def _cogs_occlusal(points, mm_per_pixel):
    p = points or {}
    if not mm_per_pixel or mm_per_pixel <= 0:
        return None
    if not all(k in p for k in ("U6", "L6", "L1i", "L1a", "Po", "Or")):
        return None
    posterior = _mid(p["U6"], p["L6"])
    apical = _unit(p["L1i"], p["L1a"])
    if apical is None:
        return None
    anterior_point = _add(p["L1i"], apical, 1.0 / mm_per_pixel)
    fh = _unit(p["Po"], p["Or"])
    op = _unit(posterior, anterior_point)
    if fh is None or op is None:
        return None
    if _dot(op, fh) < 0:
        posterior, anterior_point = anterior_point, posterior
        op = (-op[0], -op[1])
    return posterior, anterior_point, op


def _perp_component(a, b, direction, mm_per_pixel):
    delta = _vec(a, b)
    return abs(_cross(direction, delta)) * mm_per_pixel


def _parallel_component(a, b, direction, mm_per_pixel, absolute=False):
    value = _dot(_vec(a, b), direction) * mm_per_pixel
    return abs(value) if absolute else value


def g_triangle_frame(points):
    """Return I, X, K from the published sagittal G-triangle construction."""
    p = points or {}
    if not all(k in p for k in ("Ba", "Bo", "Po", "Or", "Gtri")):
        return None
    hit_i = _line_intersection(p["Ba"], p["Gtri"], p["Po"], p["Or"])
    if hit_i is None:
        return None
    i = hit_i[0]
    bo_i = _unit(p["Bo"], i)
    if bo_i is None:
        return None
    choices = []
    for degrees in (60.0, -60.0):
        d = _rotate(bo_i, degrees)
        hit = _line_intersection(p["Bo"], _add(p["Bo"], bo_i), p["Gtri"], _add(p["Gtri"], d))
        if hit is None:
            continue
        x, t, _ = hit
        if t >= -1e-9:
            choices.append((max(0.0, t), x))
    if not choices:
        return None
    _, x = min(choices, key=lambda item: item[0])
    base = _vec(p["Bo"], x)
    side = _norm(base)
    if side <= EPS:
        return None
    mid = _mid(p["Bo"], x)
    perp = (-base[1] / side, base[0] / side)
    height = math.sqrt(3.0) * side / 2.0
    k1 = _add(mid, perp, height)
    k2 = _add(mid, perp, -height)
    basis = anatomical_basis(p)
    if basis is None:
        return None
    _, inferior = basis
    k = max((k1, k2), key=lambda point: _dot(_vec(mid, point), inferior))
    return i, x, k


def _g_triangle_signed(target, x, k, anterior):
    magnitude = angle3(target, x, k)
    if magnitude is None:
        return None
    signed = _signed_distance(target, x, k, anterior, 1.0)
    magnitude = min(magnitude, 180.0 - magnitude)
    if signed is None or abs(signed) <= EPS:
        return 0.0
    return magnitude if signed > 0 else -magnitude


def ricketts_values(points, mm_per_pixel=None):
    p = points or {}
    r = {}
    basis = anatomical_basis(p)
    anterior = basis[0] if basis else None
    xi = xi_point(p)
    if all(k in p for k in ("Ba", "N", "Pt", "Gn")):
        r["Ricketts · eje facial"] = directed_line_angle(p["Ba"], p["N"], p["Pt"], p["Gn"])
    if all(k in p for k in ("Po", "Or", "N", "Pg")):
        r["Ricketts · profundidad facial"] = directed_line_angle(p["Po"], p["Or"], p["N"], p["Pg"])
    if all(k in p for k in ("Po", "Or", "Go", "Me")):
        r["Ricketts · plano mandibular"] = acute_line_angle(p["Po"], p["Or"], p["Go"], p["Me"])
    if xi is not None and all(k in p for k in ("ANS", "Pm")):
        r["Ricketts · altura facial inferior"] = angle3(p["ANS"], xi, p["Pm"])
    if xi is not None and all(k in p for k in ("DC", "Pm")):
        r["Ricketts · arco mandibular"] = angle3(p["DC"], xi, p["Pm"])
    if all(k in p for k in ("Po", "Or", "N", "A")):
        r["Ricketts · profundidad maxilar"] = directed_line_angle(p["Po"], p["Or"], p["N"], p["A"])
    if mm_per_pixel and mm_per_pixel > 0:
        if anterior is not None and all(k in p for k in ("N", "A", "Pg")):
            r["Ricketts · convexidad A–NPg"] = _signed_distance(p["A"], p["N"], p["Pg"], anterior, mm_per_pixel)
        if xi is not None and "Pm" in p:
            r["Ricketts · longitud corpus Xi–Pm"] = distance(xi, p["Pm"]) * mm_per_pixel
        if anterior is not None and all(k in p for k in ("L1i", "A", "Pg")):
            r["Ricketts · L1 a A–Pg (mm)"] = _signed_distance(p["L1i"], p["A"], p["Pg"], anterior, mm_per_pixel)
        if anterior is not None and all(k in p for k in ("Pt", "U6")):
            r["Ricketts · U6 a PTV"] = _dot(_vec(p["Pt"], p["U6"]), anterior) * mm_per_pixel
    if all(k in p for k in ("L1a", "L1i", "A", "Pg")):
        r["Ricketts · L1/A–Pg (°)"] = acute_line_angle(p["L1a"], p["L1i"], p["A"], p["Pg"])
    return r


def cogs_values(points, mm_per_pixel=None):
    p = points or {}
    r = {}
    hp = burstone_hp_direction(p)
    basis = anatomical_basis(p)
    anterior = basis[0] if basis else None
    if anterior is not None and all(k in p for k in ("N", "A", "Pg")):
        r["COGS · N–A–Pg"] = _signed_convexity_angle(p["N"], p["A"], p["Pg"], anterior)
    if hp is not None and all(k in p for k in ("Go", "Me")):
        r["COGS · MP–HP"] = acute_line_angle((0.0, 0.0), hp, p["Go"], p["Me"])
    if all(k in p for k in ("Ar", "Go", "Gn")):
        r["COGS · Ar–Go–Gn"] = angle3(p["Ar"], p["Go"], p["Gn"])
    if all(k in p for k in ("U1a", "U1i", "ANS", "PNS")):
        r["COGS · U1–NF (°)"] = obtuse_line_angle(p["U1a"], p["U1i"], p["PNS"], p["ANS"])
    if all(k in p for k in ("L1a", "L1i", "Go", "Me")):
        r["COGS · L1–MP (°)"] = obtuse_line_angle(p["L1a"], p["L1i"], p["Go"], p["Me"])
    if mm_per_pixel and mm_per_pixel > 0:
        if hp is not None:
            for key, a, b, absolute in (
                ("COGS · Ar–Ptm // HP", "Ar", "Ptm", True),
                ("COGS · Ptm–N // HP", "Ptm", "N", True),
                ("COGS · N–A // HP", "N", "A", False),
                ("COGS · N–B // HP", "N", "B", False),
                ("COGS · N–Pg // HP", "N", "Pg", False),
                ("COGS · PNS–ANS // HP", "PNS", "ANS", True),
            ):
                if a in p and b in p:
                    r[key] = _parallel_component(p[a], p[b], hp, mm_per_pixel, absolute=absolute)
            for key, a, b in (
                ("COGS · N–ANS ⟂ HP", "N", "ANS"),
                ("COGS · ANS–Gn ⟂ HP", "ANS", "Gn"),
                ("COGS · PNS–N ⟂ HP", "PNS", "N"),
            ):
                if a in p and b in p:
                    r[key] = _perp_component(p[a], p[b], hp, mm_per_pixel)
        for key, point, a, b in (
            ("COGS · U1–NF ⟂", "U1i", "PNS", "ANS"),
            ("COGS · U6–NF ⟂", "U6", "PNS", "ANS"),
            ("COGS · L1–MP ⟂", "L1i", "Go", "Me"),
            ("COGS · L6–MP ⟂", "L6", "Go", "Me"),
        ):
            if point in p and a in p and b in p:
                foot = project_point_to_line(p[point], p[a], p[b])
                if foot is not None:
                    r[key] = distance(p[point], foot) * mm_per_pixel
        for key, a, b in (("COGS · Ar–Go", "Ar", "Go"), ("COGS · Go–Pg", "Go", "Pg")):
            if a in p and b in p:
                r[key] = distance(p[a], p[b]) * mm_per_pixel
        if all(k in p for k in ("B", "Pg", "Go", "Me")):
            mp = _unit(p["Go"], p["Me"])
            if mp is not None:
                r["COGS · B–Pg // MP"] = abs(_dot(_vec(p["B"], p["Pg"]), mp)) * mm_per_pixel
        op = _cogs_occlusal(p, mm_per_pixel)
        if op is not None:
            op_a, op_b, op_u = op
            if hp is not None:
                r["COGS · OP–HP"] = acute_line_angle((0.0, 0.0), hp, op_a, op_b)
            if all(k in p for k in ("A", "B")):
                r["COGS · A–B // OP"] = _dot(_vec(p["B"], p["A"]), op_u) * mm_per_pixel
    return r


def _sassouni_occlusal(points):
    p = points or {}
    if not all(k in p for k in ("U6", "L6", "U1i", "L1i")):
        return None
    posterior = _mid(p["U6"], p["L6"])
    anterior = _mid(p["U1i"], p["L1i"])
    if distance(posterior, anterior) <= EPS:
        return None
    return posterior, anterior


def sassouni_values(points):
    p = points or {}
    r = {}
    if not all(k in p for k in ("SasCl", "SasRo", "SasSi")):
        return r
    basal = (p["SasCl"], p["SasRo"])
    occlusal = _sassouni_occlusal(p)
    mandibular = (p["SasMbP"], p["Me"]) if all(k in p for k in ("SasMbP", "Me")) else None
    palatal = (p["PNS"], p["ANS"]) if all(k in p for k in ("PNS", "ANS")) else None
    if palatal:
        r["Sassouni · basal–palatino"] = acute_line_angle(*basal, *palatal)
    if occlusal:
        r["Sassouni · basal–oclusal"] = acute_line_angle(*basal, *occlusal)
    if mandibular:
        r["Sassouni · basal–mandibular"] = acute_line_angle(*basal, *mandibular)
    if palatal and occlusal:
        r["Sassouni · palatino–oclusal"] = acute_line_angle(*palatal, *occlusal)
    if palatal and mandibular:
        r["Sassouni · palatino–mandibular"] = acute_line_angle(*palatal, *mandibular)
    if occlusal and mandibular:
        r["Sassouni · oclusal–mandibular"] = acute_line_angle(*occlusal, *mandibular)
    return r


def bimler_values(points):
    p = points or {}
    r = {}
    basis = anatomical_basis(p)
    if basis is None:
        return r
    fh_u, inferior = basis
    if all(k in p for k in ("N", "A")):
        r["Bimler · F1 perfil superior"] = _signed_vertical_inclination(p["N"], p["A"], fh_u, True)
    if all(k in p for k in ("A", "B")):
        r["Bimler · F2 perfil inferior"] = _signed_vertical_inclination(p["A"], p["B"], fh_u, False)
    if all(k in p for k in ("GoA", "Me")):
        mag = acute_line_angle((0.0, 0.0), fh_u, p["GoA"], p["Me"])
        if mag is not None:
            down = _dot(_vec(p["GoA"], p["Me"]), inferior)
            r["Bimler · F3 inclinación mandibular"] = mag if down >= 0 else -mag
    if all(k in p for k in ("PNS", "ANS")):
        r["Bimler · F4 inclinación maxilar"] = _signed_plane_inclination(p["PNS"], p["ANS"], fh_u, inferior)
    if all(k in p for k in ("Cls", "Cli")):
        r["Bimler · F5 inclinación clivus"] = acute_line_angle((0.0, 0.0), fh_u, p["Cls"], p["Cli"])
    if all(k in p for k in ("S", "N")):
        r["Bimler · F7 inclinación SN"] = acute_line_angle((0.0, 0.0), fh_u, p["S"], p["N"])
    if all(k in r for k in ("Bimler · F1 perfil superior", "Bimler · F2 perfil inferior")):
        r["Bimler · ángulo de perfil"] = r["Bimler · F1 perfil superior"] + r["Bimler · F2 perfil inferior"]
    if all(k in r for k in ("Bimler · F4 inclinación maxilar", "Bimler · F5 inclinación clivus")):
        r["Bimler · ángulo basal superior"] = r["Bimler · F4 inclinación maxilar"] + r["Bimler · F5 inclinación clivus"]
    if all(k in r for k in ("Bimler · F3 inclinación mandibular", "Bimler · F4 inclinación maxilar")):
        r["Bimler · ángulo basal inferior"] = abs(r["Bimler · F3 inclinación mandibular"]) + abs(r["Bimler · F4 inclinación maxilar"])
    if all(k in r for k in ("Bimler · ángulo basal superior", "Bimler · ángulo basal inferior")):
        r["Bimler · ángulo basal total"] = r["Bimler · ángulo basal superior"] + r["Bimler · ángulo basal inferior"]
    if all(k in p for k in ("U1a", "U1i")):
        r["Bimler · U1/FH"] = obtuse_line_angle((0.0, 0.0), fh_u, p["U1a"], p["U1i"])
    if all(k in p for k in ("L1a", "L1i")):
        r["Bimler · L1/FH"] = obtuse_line_angle((0.0, 0.0), fh_u, p["L1a"], p["L1i"])
    if all(k in p for k in ("U1a", "U1i", "L1a", "L1i")):
        r["Bimler · interincisal"] = obtuse_line_angle(p["U1a"], p["U1i"], p["L1a"], p["L1i"])
    return r


def g_triangle_values(points):
    p = points or {}
    frame = g_triangle_frame(p)
    basis = anatomical_basis(p)
    if frame is None or basis is None:
        return {}
    _, x, k = frame
    anterior, _ = basis
    r = {}
    if "A" in p:
        r["G-triangle · AXK"] = _g_triangle_signed(p["A"], x, k, anterior)
    if "B" in p:
        r["G-triangle · BXK"] = _g_triangle_signed(p["B"], x, k, anterior)
    return r


def downs_completion_values(points):
    p = points or {}
    basis = anatomical_basis(p)
    if basis is None:
        return {}
    anterior, _ = basis
    r = {}
    if all(k in p for k in ("N", "A", "Pg")):
        r["Downs · convexidad N–A–Pg"] = _signed_convexity_angle(p["N"], p["A"], p["Pg"], anterior)
    if all(k in p for k in ("A", "B", "N", "Pg")):
        r["Downs · plano A–B"] = _signed_ab_plane_angle(p["A"], p["B"], p["N"], p["Pg"], anterior)
    if all(k in p for k in ("U1a", "U1i", "L1a", "L1i")):
        r["Downs · interincisal"] = obtuse_line_angle(p["U1a"], p["U1i"], p["L1a"], p["L1i"])
    return r


def remaining_values(points, mm_per_pixel=None):
    result = {}
    for block in (
        ricketts_values(points, mm_per_pixel),
        cogs_values(points, mm_per_pixel),
        sassouni_values(points),
        bimler_values(points),
        g_triangle_values(points),
        downs_completion_values(points),
    ):
        result.update(block)
    return {key: value for key, value in result.items() if value is not None and math.isfinite(value)}


def install_remaining_analyses():
    """Install verified v0.12.6 blocks into the shared mutable catalog."""
    seen = {item[0] for item in catalog.EXTRA_POINTS}
    for item in NEW_POINTS:
        if item[0] not in seen:
            catalog.EXTRA_POINTS.append(item)
            seen.add(item[0])
    catalog.MEASUREMENTS.update(EXTENDED_MEASUREMENTS)

    legacy = catalog.MEASUREMENTS.get("McNamara · eje facial BaN–PtmGn")
    if legacy is not None:
        legacy["status"] = catalog.STATUS_VALIDATION
        legacy["label"] = "Obsoleto · BaN–PtmGn (no usar; Pt ≠ Ptm)"

    catalog.ANALYSES["ricketts"].update(status=catalog.STATUS_ACTIVE, summary="Núcleo reproducible: eje facial, profundidad facial/maxilar, plano mandibular, Xi construido, altura facial inferior, arco mandibular, convexidad, corpus y relaciones dentales. VERT no se clasifica sin referencia etaria explícita.", missing_landmarks=["Pt", "Pm", "DC", "R1", "R2", "R3", "R4"])
    catalog.ANALYSES["cogs"].update(status=catalog.STATUS_ACTIVE, summary="COGS/Burstone de tejidos duros con HP a 7° de SN, proyecciones paralelas/perpendiculares, dimensiones maxilomandibulares y relaciones dentales. Las normas por sexo/población quedan separadas.", missing_landmarks=["U6", "L6"])
    catalog.ANALYSES["sassouni"].update(status=catalog.STATUS_ACTIVE, summary="Núcleo estructural reproducible de los cuatro planos de Sassouni y sus divergencias. El punto O y los arcos no se automatizan hasta fijar un constructor canónico de la zona mínima de convergencia.", missing_landmarks=["SasCl", "SasRo", "SasSi", "SasMbP", "U6", "L6"])
    catalog.ANALYSES["bimler"].update(status=catalog.STATUS_ACTIVE, summary="Núcleo verificable de Bimler: factores F1–F5 y F7, perfil, ángulos basales e incisivos en el sistema ortogonal de Frankfurt. F6/F8–F10 y correlómetro permanecen fuera para no inventar construcciones.", missing_landmarks=["GoA", "Cls", "Cli"])
    catalog.ANALYSES["g_triangle"].update(status=catalog.STATUS_ACTIVE, summary="Sagittal G-triangle: construcción Bo–X–K y ángulos firmados AXK/BXK según el método publicado. Sus rangos originales son de adultos del sur de China y no se aplican universalmente.", missing_landmarks=["Gtri"])
    catalog.ANALYSES["downs"].update(status=catalog.STATUS_ACTIVE, summary="Downs reproducible: bloque previo más convexidad N–A/A–Pg y ángulo A–B/N–Pg con signo anatómico explícito e interincisal.", missing_landmarks=[])
    catalog.ANALYSES["alexander"].update(status=catalog.STATUS_REFERENCE_ONLY, summary="Alexander Discipline es una filosofía/técnica de tratamiento; no se ha identificado un único análisis cefalométrico canónico equivalente a Steiner que pueda activarse sin inventarlo.")
    catalog.ANALYSES["ritucci"].update(status=catalog.STATUS_OTHER_PROJECTION, summary="Ritucci–Burstone para asimetría usa radiografía submentovertex (SMV) con landmarks bilaterales; no corresponde a una sola lateral de cráneo.")

    for analysis_id, refs in REFERENCES.items():
        current = list(catalog.REFERENCES.get(analysis_id, []))
        for ref in refs:
            if ref not in current:
                current.append(ref)
        catalog.REFERENCES[analysis_id] = current


install_remaining_analyses()
