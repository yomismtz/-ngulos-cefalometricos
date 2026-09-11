"""Geometría pura y comprobable para mediciones nuevas de YomCeph v0.12.

Este módulo no contiene normas clínicas. Sólo transforma coordenadas en valores
geométricos. Esto permite probar las fórmulas sin crear una interfaz Tk.
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
