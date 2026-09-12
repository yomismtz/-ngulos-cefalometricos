from pathlib import Path

java_dir = Path('app/src/main/java/com/cefalo/angulos')

# -----------------------------------------------------------------------------
# Preserve the optional CVM sex/reference selector across configuration changes.
# -----------------------------------------------------------------------------
activity = java_dir / 'RadiographicAssessmentActivity.java'
a = activity.read_text(encoding='utf-8')

save_anchor = '''        if (MODE_CVM.equals(mode)) {
            if (spC2Concavity != null) outState.putInt("CVM_C2C", spC2Concavity.getSelectedItemPosition());
'''
save_replacement = '''        if (MODE_CVM.equals(mode)) {
            if (spCvmSex != null) outState.putInt("CVM_SEX", spCvmSex.getSelectedItemPosition());
            if (spC2Concavity != null) outState.putInt("CVM_C2C", spC2Concavity.getSelectedItemPosition());
'''
if 'outState.putInt("CVM_SEX"' not in a:
    if save_anchor not in a:
        raise RuntimeError('Could not locate CVM save-state anchor')
    a = a.replace(save_anchor, save_replacement, 1)

restore_anchor = '''        if (MODE_CVM.equals(mode)) {
            spC2Concavity.setSelection(state.getInt("CVM_C2C", 0));
'''
restore_replacement = '''        if (MODE_CVM.equals(mode)) {
            if (spCvmSex != null) spCvmSex.setSelection(state.getInt("CVM_SEX", 0));
            spC2Concavity.setSelection(state.getInt("CVM_C2C", 0));
'''
if 'spCvmSex.setSelection(state.getInt("CVM_SEX"' not in a:
    if restore_anchor not in a:
        raise RuntimeError('Could not locate CVM restore-state anchor')
    a = a.replace(restore_anchor, restore_replacement, 1)

activity.write_text(a, encoding='utf-8')

# -----------------------------------------------------------------------------
# Make SQLite mutations report success; persistence must not silently succeed.
# -----------------------------------------------------------------------------
database = java_dir / 'StudyDatabase.java'
d = database.read_text(encoding='utf-8')

old_save = '''    public static void save(Context context, String id, String payload, long updatedAt) {
        if (id == null || payload == null) return;
        ContentValues values = new ContentValues();
        values.put("id", id);
        values.put("payload", payload);
        values.put("updated_at", updatedAt);
        get(context).getWritableDatabase().insertWithOnConflict(
                TABLE, null, values, SQLiteDatabase.CONFLICT_REPLACE
        );
    }
'''
new_save = '''    public static boolean save(Context context, String id, String payload, long updatedAt) {
        if (context == null || id == null || payload == null) return false;
        ContentValues values = new ContentValues();
        values.put("id", id);
        values.put("payload", payload);
        values.put("updated_at", updatedAt);
        long rowId = get(context).getWritableDatabase().insertWithOnConflict(
                TABLE, null, values, SQLiteDatabase.CONFLICT_REPLACE
        );
        return rowId != -1L;
    }
'''
if 'public static boolean save(Context context' not in d:
    if old_save not in d:
        raise RuntimeError('Could not locate StudyDatabase.save')
    d = d.replace(old_save, new_save, 1)

old_delete = '''    public static void delete(Context context, String id) {
        if (id == null) return;
        get(context).getWritableDatabase().delete(TABLE, "id=?", new String[]{id});
    }
'''
new_delete = '''    public static boolean delete(Context context, String id) {
        if (context == null || id == null) return false;
        return get(context).getWritableDatabase().delete(
                TABLE,
                "id=?",
                new String[]{id}
        ) > 0;
    }
'''
if 'public static boolean delete(Context context' not in d:
    if old_delete not in d:
        raise RuntimeError('Could not locate StudyDatabase.delete')
    d = d.replace(old_delete, new_delete, 1)

database.write_text(d, encoding='utf-8')

store = java_dir / 'SavedStudyStore.java'
s = store.read_text(encoding='utf-8')

old_db_save = '''            StudyDatabase.save(context, study.id, root.toString(), updatedAt);

            SharedPreferences prefs =
'''
new_db_save = '''            boolean databaseSaved = StudyDatabase.save(
                    context,
                    study.id,
                    root.toString(),
                    updatedAt
            );
            if (!databaseSaved) {
                Log.e(TAG, "SQLite write failed for study " + study.id);
                return false;
            }

            SharedPreferences prefs =
'''
if 'boolean databaseSaved = StudyDatabase.save' not in s:
    if old_db_save not in s:
        raise RuntimeError('Could not locate generated database save call')
    s = s.replace(old_db_save, new_db_save, 1)

old_migration = '''            if (migrateFromLegacy) {
                StudyDatabase.save(context, id, raw, root.optLong("updatedAt", 0L));
            }
'''
new_migration = '''            if (migrateFromLegacy) {
                boolean migrated = StudyDatabase.save(
                        context,
                        id,
                        raw,
                        root.optLong("updatedAt", 0L)
                );
                if (!migrated) {
                    Log.w(TAG, "Could not migrate legacy study " + id + " to SQLite");
                }
            }
'''
if 'boolean migrated = StudyDatabase.save' not in s:
    if old_migration not in s:
        raise RuntimeError('Could not locate legacy migration database save')
    s = s.replace(old_migration, new_migration, 1)

old_db_delete = '''        ids.remove(id);
        StudyDatabase.delete(context, id);

        boolean committed = prefs.edit()
'''
new_db_delete = '''        ids.remove(id);
        boolean databaseDeleted = StudyDatabase.delete(context, id);
        if (!databaseDeleted && removedStudy != null) {
            Log.e(TAG, "SQLite delete failed for study " + id);
            return false;
        }

        boolean committed = prefs.edit()
'''
if 'boolean databaseDeleted = StudyDatabase.delete' not in s:
    if old_db_delete not in s:
        raise RuntimeError('Could not locate generated database delete call')
    s = s.replace(old_db_delete, new_db_delete, 1)

store.write_text(s, encoding='utf-8')

checks = {
    'CVM sex save': 'outState.putInt("CVM_SEX"' in activity.read_text(encoding='utf-8'),
    'CVM sex restore': 'spCvmSex.setSelection(state.getInt("CVM_SEX"' in activity.read_text(encoding='utf-8'),
    'database save boolean': 'public static boolean save(Context context' in database.read_text(encoding='utf-8'),
    'database delete boolean': 'public static boolean delete(Context context' in database.read_text(encoding='utf-8'),
    'store database check': 'boolean databaseSaved = StudyDatabase.save' in store.read_text(encoding='utf-8'),
}
missing = [name for name, ok in checks.items() if not ok]
if missing:
    raise RuntimeError('Post-generation safety checks failed: ' + ', '.join(missing))

print('Post-generation safety applied: CVM state + checked SQLite persistence.')
