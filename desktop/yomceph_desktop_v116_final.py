import sqlite3

import yomceph_desktop_hidpi as ui
import yomceph_desktop_v116 as universal

APP_VERSION = "0.11.6"


class YomCephV116Final(universal.YomCephV116):
    """Entrada final v0.11.6: restaura metadatos universales si un guardado se cancela."""

    def save_case_to_database(self):
        case_id = self.case_id.get().strip()
        snapshot = None
        history_before = None
        if case_id and self._db_path:
            try:
                with sqlite3.connect(self._db_path) as con:
                    snapshot = con.execute("""
                        SELECT app_profile, study_name, study_target, birth_date, sex_code,
                               gender_identity, country, institution, ui_language
                        FROM cases WHERE case_id=?
                    """, (case_id,)).fetchone()
                    row = con.execute(
                        "SELECT MAX(id) FROM case_history WHERE case_id=?", (case_id,)
                    ).fetchone()
                    history_before = row[0] if row else None
            except Exception:
                snapshot = None
                history_before = None

        result = super().save_case_to_database()

        if case_id and snapshot is not None:
            try:
                with sqlite3.connect(self._db_path) as con:
                    row = con.execute(
                        "SELECT MAX(id) FROM case_history WHERE case_id=?", (case_id,)
                    ).fetchone()
                    history_after = row[0] if row else None
                    if history_after == history_before:
                        con.execute("""
                            UPDATE cases SET
                                app_profile=?, study_name=?, study_target=?, birth_date=?, sex_code=?,
                                gender_identity=?, country=?, institution=?, ui_language=?
                            WHERE case_id=?
                        """, tuple(snapshot) + (case_id,))
                        con.commit()
            except Exception:
                pass
        return result


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = YomCephV116Final()
    app.mainloop()
