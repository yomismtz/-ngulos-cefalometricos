from pathlib import Path

path = Path('ci/adaptive-device-db-pdf.py')
text = path.read_text(encoding='utf-8')

# SavedStudyStore now assigns the current timestamp before persistence so the
# generated SQLite mirror must use the same value that is serialized to JSON.
text = text.replace(
    'StudyDatabase.save(context, study.id, root.toString(), study.updatedAt);',
    'StudyDatabase.save(context, study.id, root.toString(), updatedAt);'
)

old_delete_anchor = """    delete_anchor = '''        ids.remove(id);\\n\\n        prefs.edit()\\n'''\n"""
new_delete_anchor = """    delete_anchor = '''        ids.remove(id);\\n\\n        boolean committed = prefs.edit()\\n'''\n"""
if old_delete_anchor in text:
    text = text.replace(old_delete_anchor, new_delete_anchor, 1)

old_delete_replacement = """        '''        ids.remove(id);\\n        StudyDatabase.delete(context, id);\\n\\n        prefs.edit()\\n''', 1)\n"""
new_delete_replacement = """        '''        ids.remove(id);\\n        StudyDatabase.delete(context, id);\\n\\n        boolean committed = prefs.edit()\\n''', 1)\n"""
if old_delete_replacement in text:
    text = text.replace(old_delete_replacement, new_delete_replacement, 1)

# Guardrail: the generator must now recognize the hardened delete path.
if "boolean committed = prefs.edit()" not in text:
    raise RuntimeError('Could not adapt SQLite generator to hardened SavedStudyStore')

path.write_text(text, encoding='utf-8')
print('SQLite generator adapted to hardened SavedStudyStore.')
