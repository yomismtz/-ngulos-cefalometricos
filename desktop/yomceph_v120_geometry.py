"""Geometría pura y comprobable para YomCeph v0.12.

Este módulo no contiene normas clínicas. Sólo transforma coordenadas en valores
geométricos. Las decisiones agudo/obtuso/direccional se definen por el método,
no por cercanía a un valor esperado.
"""

import math


def distance(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def angle3(a, vertex, c):
    u = (a[0] - vertex[0], a[1] - vertex[1])
    v = (c[0] - vertex[0], c[1] - vertex[1])
    nu = math.hypot(*u)
    nv = math.hypot(*v)
    if nu <= 1e-12 or nv <= 1e-12:
        return None
    cosine = max(-1.0, min(1.0, (u[0] * v[0] + u[1] * v[1]) / (nu * nv)))
    return math.degrees(math.acos(cosine))


def directed_line_angle(a, b, c, d):
    """Ángulo 0–180° entre los vectores anatómicamente ordenados a→b y c→d.

    Invertir ambos ejes o reflejar toda la radiografía conserva el resultado.
    Invertir sólo uno cambia al suplemento, por eso los extremos se documentan
    explícitamente en cada medición que usa esta función.
    """
    ux, uy = b[0] - a[0], b[1] - a[1]
    vx, vy = d[0] - c[0], d[1] - c[1]
    nu = math.hypot(ux, uy)
    nv = math.hypot(vx, vy)
    if nu <= 1e-12 or nv <= 1e-12:
        return None
    cosine = max(-1.0, min(1.0, (ux * vx + uy * vy) / (nu * nv)))
    return math.degrees(math.acos(cosine))


def acute_line_angle(a, b, c, d):
    """Ángulo agudo/no obtuso entre dos líneas, independiente de su sentido."""
    raw = directed_line_angle(a, b, c, d)
    if raw is None:
        return None
    return min(raw, 180.0 - raw)


def obtuse_line_angle(a, b, c, d):
    """Suplemento obtuso/no agudo entre dos líneas, independiente de su sentido."""
    acute = acute_line_angle(a, b, c, d)
    if acute is None:
        return None
    return 180.0 - acute


def project_point_to_line(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    den = dx * dx + dy * dy
    if den <= 1e-12:
        return None
    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / den
    return a[0] + t * dx, a[1] + t * dy


def yen_angle(s, m, g):
    """Ángulo S-M-G, vértice M."""
    return angle3(s, m, g)


def w_angle(s, m, g):
    """Ángulo entre M-G y la perpendicular desde M a S-G."""
    foot = project_point_to_line(m, s, g)
    if foot is None:
        return None
    return angle3(foot, m, g)


def wits_ao_bo(a_point, b_point, occlusal_posterior, occlusal_anterior, mm_per_pixel):
    """Wits AO−BO con signo anatómico posterior→anterior.

    Un resultado positivo significa que AO queda por delante de BO en la
    dirección anatómica definida por el plano oclusal posterior→anterior.
    """
    if not mm_per_pixel or mm_per_pixel <= 0:
        return None
    ao = project_point_to_line(a_point, occlusal_posterior, occlusal_anterior)
    bo = project_point_to_line(b_point, occlusal_posterior, occlusal_anterior)
    if ao is None or bo is None:
        return None
    dx = occlusal_anterior[0] - occlusal_posterior[0]
    dy = occlusal_anterior[1] - occlusal_posterior[1]
    den = math.hypot(dx, dy)
    if den <= 1e-12:
        return None
    ux, uy = dx / den, dy / den
    return ((ao[0] - bo[0]) * ux + (ao[1] - bo[1]) * uy) * mm_per_pixel


def legacy_active_angles(points):
    """Recalcula las medidas activas que históricamente usaban closest_supplement.

    Devuelve únicamente valores cuya geometría queda definida sin consultar una
    norma. Las claves ausentes significan que faltan landmarks.
    """
    p = points
    r = {}

    # Steiner: ángulos entre planos definidos como sector agudo.
    if all(k in p for k in ("S", "N", "Po", "Or")):
        r["SN–PoOr"] = acute_line_angle(p["S"], p["N"], p["Po"], p["Or"])
    if all(k in p for k in ("S", "N", "Go", "Gn")):
        r["SN–GoGn"] = acute_line_angle(p["S"], p["N"], p["Go"], p["Gn"])
    if all(k in p for k in ("A", "B", "Go", "Gn")):
        r["AB–GoGn"] = acute_line_angle(p["A"], p["B"], p["Go"], p["Gn"])

    # U1-SN se expresa convencionalmente como el sector obtuso del eje incisivo
    # con SN (aprox. 100°, no su suplemento agudo).
    if all(k in p for k in ("U1a", "U1i", "S", "N")):
        r["IS–SN"] = obtuse_line_angle(p["U1a"], p["U1i"], p["S"], p["N"])

    # Solow–Tallgren: SN/OPT y SN/CVT son el ángulo que abre inferiormente;
    # con estas líneas equivale al sector obtuso, independiente del espejo.
    if all(k in p for k in ("S", "N", "cv2tg", "cv2ip")):
        r["SN–OPT"] = obtuse_line_angle(p["S"], p["N"], p["cv2tg"], p["cv2ip"])
    if all(k in p for k in ("S", "N", "cv2tg", "cv4ip")):
        r["SN–CVT"] = obtuse_line_angle(p["S"], p["N"], p["cv2tg"], p["cv4ip"])

    # Rocabado: el ángulo McGregor/odontoideo se expresa como sector obtuso.
    if all(k in p for k in ("PNS", "C0", "Ops", "Opi")):
        r["MGP–OP"] = obtuse_line_angle(p["PNS"], p["C0"], p["Ops"], p["Opi"])

    # MGP–CVT se conserva como variable descriptiva con la dirección anatómica
    # que ya usaba YomCeph. closest_supplement(..., 90) era matemáticamente un
    # no-op: ambas opciones están a la misma distancia de 90°.
    if all(k in p for k in ("PNS", "C0", "cv2tg", "cv4ip")):
        r["MGP–CVT"] = directed_line_angle(p["PNS"], p["C0"], p["cv2tg"], p["cv4ip"])

    # Powell: nasomental es el sector obtuso entre la tangente dorsonasal y la
    # línea Prn-Pg'. Mentocervical usa el sector definido por G'→Pg' y Me'→C.
    if all(k in p for k in ("Nsoft", "Dn", "Prn", "Pgsoft")):
        r["Powell Nasomental"] = obtuse_line_angle(p["Nsoft"], p["Dn"], p["Prn"], p["Pgsoft"])
    if all(k in p for k in ("Gsoft", "Pgsoft", "Mesoft", "Csoft")):
        r["Powell Mentocervical"] = directed_line_angle(p["Gsoft"], p["Pgsoft"], p["Mesoft"], p["Csoft"])

    return {key: value for key, value in r.items() if value is not None}


def jarabak_values(points, mm_per_pixel=None):
    """Devuelve las variables Björk–Jarabak posibles con los puntos presentes."""
    r = {}
    p = points
    if all(k in p for k in ("N", "S", "Ar")):
        r["Jarabak · Saddle"] = angle3(p["N"], p["S"], p["Ar"])
    if all(k in p for k in ("S", "Ar", "Go")):
        r["Jarabak · Articular"] = angle3(p["S"], p["Ar"], p["Go"])
    if all(k in p for k in ("Ar", "Go", "Me")):
        r["Jarabak · Gonial"] = angle3(p["Ar"], p["Go"], p["Me"])
    if all(k in p for k in ("Ar", "Go", "N")):
        r["Jarabak · Upper gonial"] = angle3(p["Ar"], p["Go"], p["N"])
    if all(k in p for k in ("N", "Go", "Me")):
        r["Jarabak · Lower gonial"] = angle3(p["N"], p["Go"], p["Me"])
    if all(r.get(k) is not None for k in ("Jarabak · Saddle", "Jarabak · Articular", "Jarabak · Gonial")):
        r["Jarabak · Sum"] = r["Jarabak · Saddle"] + r["Jarabak · Articular"] + r["Jarabak · Gonial"]

    if mm_per_pixel and mm_per_pixel > 0:
        for key, a, b in (
            ("Jarabak · S-N", "S", "N"),
            ("Jarabak · S-Ar", "S", "Ar"),
            ("Jarabak · Ar-Go", "Ar", "Go"),
            ("Jarabak · Go-Me", "Go", "Me"),
            ("Jarabak · S-Go", "S", "Go"),
            ("Jarabak · N-Me", "N", "Me"),
        ):
            if a in p and b in p:
                r[key] = distance(p[a], p[b]) * mm_per_pixel

    if all(k in p for k in ("S", "Go", "N", "Me")):
        anterior = distance(p["N"], p["Me"])
        if anterior > 1e-12:
            r["Jarabak ratio"] = distance(p["S"], p["Go"]) / anterior * 100.0
    return r
