import tkinter as tk

import yomceph_desktop as core
import yomceph_desktop_hidpi as ui
import yomceph_desktop_v06_extended as v06
import yomceph_desktop_v07_powell as v07

APP_VERSION = "0.8.0"


def clinical_powell_classify(name, value):
    lo, hi, norm = v07.POWELL_NORMS[name]

    if name == "Nasofrontal":
        if value < lo:
            return (
                "TRANSICIÓN FRONTONASAL AGUDA",
                "Hallazgo compatible con una transición frente–raíz nasal más aguda y una raíz nasal relativamente más marcada. Debe correlacionarse con la forma de la glabela y del radix."
            )
        if value > hi:
            return (
                "TRANSICIÓN FRONTONASAL OBTUSA",
                "Hallazgo compatible con una transición frente–raíz nasal más abierta; el radix puede verse relativamente alto o menos definido."
            )
        return (
            "TRANSICIÓN FRONTONASAL ARMÓNICA",
            "Relación frontonasal compatible con el intervalo estético de referencia de Powell."
        )

    if name == "Nasofacial":
        if value < lo:
            return (
                "PROYECCIÓN NASAL RELATIVA DISMINUIDA",
                "El perfil muestra menor prominencia nasal relativa respecto al plano facial. Debe valorarse junto con la posición del mentón y la frente."
            )
        if value > hi:
            return (
                "PROMINENCIA NASAL RELATIVA AUMENTADA",
                "El perfil es compatible con una proyección nasal relativamente aumentada respecto al plano facial."
            )
        return (
            "PROYECCIÓN NASAL ARMÓNICA",
            "La proyección nasal guarda una relación armónica con el plano facial según la referencia de Powell."
        )

    if name == "Nasomental":
        if value < lo:
            return (
                "DESARMONÍA NARIZ–MENTÓN · ÁNGULO REDUCIDO",
                "La relación entre nariz y mentón se encuentra más cerrada de lo esperado. El hallazgo no permite atribuir la causa únicamente a la nariz o al mentón; deben revisarse ambas estructuras."
            )
        if value > hi:
            return (
                "DESARMONÍA NARIZ–MENTÓN · ÁNGULO AUMENTADO",
                "La relación nariz–mentón se encuentra más abierta de lo esperado. Puede participar una diferencia relativa en la proyección nasal y/o mentoniana; revise ambas estructuras."
            )
        return (
            "BALANCE NARIZ–MENTÓN ARMÓNICO",
            "La relación angular entre nariz y mentón es compatible con el intervalo estético de Powell."
        )

    if name == "Mentocervical":
        if value < lo:
            return (
                "ÁNGULO CERVICOMENTAL MUY AGUDO",
                "Hallazgo compatible con una definición cervicomental marcada y/o mayor proyección relativa del mentón. También depende del contorno de tejidos blandos submandibulares."
            )
        if value > hi:
            return (
                "ÁNGULO CERVICOMENTAL ABIERTO",
                "Hallazgo compatible con menor definición cervicomental. Puede asociarse con menor proyección relativa del mentón y/o mayor volumen de tejidos blandos submandibulares."
            )
        return (
            "RELACIÓN CERVICOMENTAL ARMÓNICA",
            "La relación mentón–cuello se encuentra dentro del intervalo estético de Powell."
        )

    return "HALLAZGO DESCRIPTIVO", f"Referencia adoptada: {norm}."


# La clase de Powell usa una función de módulo; se sustituye por la versión clínica.
v07.classify = clinical_powell_classify


class ClinicalYomCeph(v07.PowellYomCeph):
    def __init__(self):
        super().__init__()
        self.title("YomCeph Desktop · Interpretación clínica · v0.8")
        self.status.config(
            text="v0.8 · Resultados con interpretación cefalométrica clínica · F6 OPT/CVT · F9 McGregor · F10 incisivos · F12 Powell"
        )

    def interpret(self, name, value):
        """Convierte las medidas principales en hallazgos cefalométricos clínicos."""
        if name == "SNA":
            if value < 80:
                finding = "Posición maxilar retrusiva respecto a la base craneal; hallazgo compatible con retrognatismo/retrusión maxilar cefalométrica."
            elif value > 84:
                finding = "Posición maxilar adelantada respecto a la base craneal; hallazgo compatible con prognatismo/protrusión maxilar cefalométrica."
            else:
                finding = "Posición sagital maxilar compatible con una relación maxilar ortognática respecto a SN."
            return f"Referencia: 82° ± 2°.\nInterpretación clínica: {finding}"

        if name == "SNB":
            if value < 78:
                finding = "Posición mandibular retrusiva respecto a la base craneal; hallazgo compatible con retrognatismo/retrusión mandibular cefalométrica."
            elif value > 82:
                finding = "Posición mandibular adelantada respecto a la base craneal; hallazgo compatible con prognatismo/protrusión mandibular cefalométrica."
            else:
                finding = "Posición sagital mandibular compatible con una relación mandibular ortognática respecto a SN."
            return f"Referencia: 80° ± 2°.\nInterpretación clínica: {finding}"

        if name == "ANB":
            if value < 0:
                finding = "Relación sagital maxilomandibular compatible con patrón esquelético Clase III. Revise SNA y SNB para identificar si predomina retrusión maxilar, prognatismo mandibular o un componente combinado."
            elif value > 4:
                finding = "Relación sagital maxilomandibular compatible con patrón esquelético Clase II. Revise SNA y SNB para identificar si predomina protrusión maxilar, retrognatismo mandibular o un componente combinado."
            else:
                finding = "Relación sagital maxilomandibular compatible con patrón esquelético Clase I según la referencia de Steiner."
            return f"Referencia: 2° ± 2°.\nInterpretación clínica: {finding}"

        if name == "SN–GoGn":
            if value < 27:
                finding = "Patrón vertical hipodivergente, con tendencia de crecimiento horizontal y rotación mandibular anterior."
            elif value > 37:
                finding = "Patrón vertical hiperdivergente, con tendencia de crecimiento vertical y rotación mandibular posterior."
            else:
                finding = "Patrón vertical normodivergente según la referencia de Steiner."
            return f"Referencia: 32° ± 5°.\nInterpretación clínica: {finding}"

        if name == "SN–PoOr":
            if value < 4:
                finding = "Relación SN–Frankfort reducida; indica una configuración/inclinación craneal diferente al intervalo adoptado. No constituye por sí sola un diagnóstico esquelético."
            elif value > 10:
                finding = "Relación SN–Frankfort aumentada; indica una configuración/inclinación craneal diferente al intervalo adoptado. No constituye por sí sola un diagnóstico esquelético."
            else:
                finding = "Relación angular SN–Frankfort dentro del intervalo adoptado."
            return f"Referencia adoptada: 7° ± 3°.\nInterpretación clínica: {finding}"

        if name == "SN–OPT":
            if value < 94:
                finding = "Angulación craneocervical SN–OPT reducida respecto al protocolo. Interprétese como hallazgo postural y no como diagnóstico aislado; la postura natural de la cabeza y la técnica radiográfica influyen en esta medida."
            elif value > 100:
                finding = "Angulación craneocervical SN–OPT aumentada respecto al protocolo. Interprétese como hallazgo postural y no como diagnóstico aislado; la postura natural de la cabeza y la técnica radiográfica influyen en esta medida."
            else:
                finding = "Relación craneocervical SN–OPT compatible con el intervalo adoptado en el protocolo."
            return f"Referencia del protocolo: 94°–100°.\nInterpretación clínica: {finding}"

        if name == "SN–CVT":
            if value < 96:
                finding = "Angulación craneocervical SN–CVT reducida respecto al protocolo; hallazgo postural que debe correlacionarse con SN–OPT, OPT–CVT y la posición de adquisición."
            elif value > 102:
                finding = "Angulación craneocervical SN–CVT aumentada respecto al protocolo; hallazgo postural que debe correlacionarse con SN–OPT, OPT–CVT y la posición de adquisición."
            else:
                finding = "Relación craneocervical SN–CVT compatible con el intervalo adoptado en el protocolo."
            return f"Referencia del protocolo: 96°–102°.\nInterpretación clínica: {finding}"

        return super().interpret(name, value)

    def _interpret_mgp_op(self, value):
        if value < 96:
            return "Postura craneocervical compatible con EXTENSIÓN de la cabeza respecto a la columna cervical superior según Rocabado."
        if value > 106:
            return "Postura craneocervical compatible con FLEXIÓN de la cabeza respecto a la columna cervical superior según Rocabado."
        return "Postura craneocervical NEUTRA/funcional dentro del intervalo de referencia de Rocabado (96°–106°)."

    def _interpret_u1na(self, value):
        if value < 20:
            return "INCISIVO SUPERIOR RETROINCLINADO respecto a NA. Clínicamente corresponde a una inclinación palatina reducida del eje del incisivo superior."
        if value > 24:
            return "INCISIVO SUPERIOR PROINCLINADO respecto a NA. Clínicamente corresponde a una inclinación vestibular aumentada del eje del incisivo superior."
        return "INCISIVO SUPERIOR con inclinación cefalométrica dentro del intervalo de Steiner."

    def _interpret_l1nb(self, value):
        if value < 23:
            return "INCISIVO INFERIOR RETROINCLINADO respecto a NB, con inclinación lingual relativa del eje incisivo."
        if value > 27:
            return "INCISIVO INFERIOR PROINCLINADO respecto a NB, con inclinación vestibular relativa del eje incisivo."
        return "INCISIVO INFERIOR con inclinación cefalométrica dentro del intervalo de Steiner."

    def _interpret_interincisal(self, value):
        if value > 135:
            return "ÁNGULO INTERINCISAL AUMENTADO: patrón compatible con incisivos relativamente más verticalizados/retroinclinados. Determine cuál arcada contribuye revisando U1–NA y L1–NB."
        if value < 125:
            return "ÁNGULO INTERINCISAL DISMINUIDO: patrón compatible con mayor proinclinación dentoalveolar; si U1–NA y L1–NB también están aumentados, es compatible con protrusión/proinclinación bimaxilar."
        return "Relación interincisal compatible con una inclinación dentaria equilibrada según la referencia convencional."

    def cervical_interpretation(self, r):
        # Mantiene los umbrales del protocolo ya configurado, pero cambia la redacción a hallazgo clínico.
        if "Profundidad cervical (mm)" not in r:
            return "No es posible establecer el patrón de curvatura cervical en milímetros sin calibración radiográfica."
        mm = r["Profundidad cervical (mm)"]
        direction = r.get("_cervical_anterior_sign", 1)
        if direction < 0:
            return f"{mm:.2f} mm hacia el lado posterior de la tangente: patrón compatible con CIFOSIS / INVERSIÓN de la curvatura cervical según el protocolo; confirme el trazado."
        if mm < 7:
            return f"{mm:.2f} mm: patrón compatible con RECTIFICACIÓN o disminución de la lordosis cervical según el protocolo adoptado."
        if mm <= 15:
            return f"{mm:.2f} mm: patrón compatible con LORDOSIS CERVICAL dentro del intervalo adoptado por el protocolo."
        return f"{mm:.2f} mm: patrón compatible con HIPERLORDOSIS / incremento de la curvatura cervical según el protocolo adoptado."

    def _skeletal_summary(self, r):
        if "ANB" not in r:
            return None
        anb = r["ANB"]
        sna = r.get("SNA")
        snb = r.get("SNB")
        if 0 <= anb <= 4:
            return "Patrón sagital esquelético Clase I."
        if anb > 4:
            if sna is not None and snb is not None:
                if sna > 84 and snb < 78:
                    return "Patrón esquelético Clase II de componente combinado: protrusión maxilar y retrognatismo mandibular."
                if snb < 78 and sna <= 84:
                    return "Patrón esquelético Clase II con predominio de retrognatismo mandibular."
                if sna > 84 and snb >= 78:
                    return "Patrón esquelético Clase II con predominio de protrusión maxilar."
            return "Patrón esquelético Clase II; revisar SNA y SNB para definir el componente predominante."
        if sna is not None and snb is not None:
            if sna < 80 and snb > 82:
                return "Patrón esquelético Clase III de componente combinado: retrusión maxilar y prognatismo mandibular."
            if sna < 80 and snb <= 82:
                return "Patrón esquelético Clase III con predominio de retrusión maxilar."
            if snb > 82 and sna >= 80:
                return "Patrón esquelético Clase III con predominio de prognatismo mandibular."
        return "Patrón esquelético Clase III; revisar SNA y SNB para definir el componente predominante."

    def calculate(self):
        super().calculate()
        r = self.results_cache
        summary = ["", "RESUMEN CEFALOMÉTRICO CLÍNICO"]

        sk = self._skeletal_summary(r)
        if sk:
            summary.append("• Esquelético: " + sk)

        if "SN–GoGn" in r:
            v = r["SN–GoGn"]
            if v < 27:
                summary.append("• Vertical: patrón hipodivergente / crecimiento horizontal.")
            elif v > 37:
                summary.append("• Vertical: patrón hiperdivergente / crecimiento vertical.")
            else:
                summary.append("• Vertical: patrón normodivergente.")

        dental = []
        if "U1–NA" in r:
            dental.append("superior retroinclinado" if r["U1–NA"] < 20 else "superior proinclinado" if r["U1–NA"] > 24 else "superior en inclinación de referencia")
        if "L1–NB" in r:
            dental.append("inferior retroinclinado" if r["L1–NB"] < 23 else "inferior proinclinado" if r["L1–NB"] > 27 else "inferior en inclinación de referencia")
        if dental:
            summary.append("• Incisivos: " + "; ".join(dental) + ".")

        if "MGP–OP" in r:
            v = r["MGP–OP"]
            posture = "extensión craneocervical" if v < 96 else "flexión craneocervical" if v > 106 else "postura craneocervical dentro del intervalo de Rocabado"
            summary.append("• Postura cráneo-cervical (McGregor/odontoides): " + posture + ".")

        if "Profundidad cervical (mm)" in r:
            summary.append("• Curvatura cervical: " + self.cervical_interpretation(r))

        summary += [
            "",
            "Nota: este apartado expresa HALLAZGOS CEFALOMÉTRICOS CLÍNICOS compatibles con el trazado. Un diagnóstico ortodóncico integral requiere correlación con edad, etapa de crecimiento, examen clínico, oclusión y demás registros."
        ]

        try:
            self.results_text.config(state=tk.NORMAL)
            self.results_text.insert(tk.END, "\n" + "\n".join(summary))
            self.results_text.config(state=tk.DISABLED)
        except Exception:
            pass


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = ClinicalYomCeph()
    app.mainloop()
