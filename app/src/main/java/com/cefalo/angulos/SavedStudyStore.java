package com.cefalo.angulos;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.PointF;
import android.net.Uri;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.UUID;

public final class SavedStudyStore {

    private static final String TAG = "SavedStudyStore";
    private static final String PREFS = "yom_saved_studies";
    private static final String IDS = "study_ids";
    private static final int SCHEMA_VERSION = 2;

    public static class StudyData {
        public String id;
        public String mode;
        public String imageUri;
        public String studyName;
        public String patientName;
        public String patientAge;
        public String patientSex;
        public long updatedAt;
        public boolean locked;
        public double mmPerPixel = Double.NaN;
        public String calibrationLabel = "";
        public List<String> labels = new ArrayList<>();
        public List<PointF> points = new ArrayList<>();
        public List<Boolean> pointLocks = new ArrayList<>();

        public int placedCount() {
            int count = 0;
            for (PointF p : points) {
                if (p != null) count++;
            }
            return count;
        }
    }

    private SavedStudyStore() {}

    public static String newId() {
        return UUID.randomUUID().toString();
    }

    public static String suggestedStudyName(Context context) {
        int max = 0;

        for (StudyData study : list(context)) {
            if (study == null || study.studyName == null) continue;

            String name = study.studyName.trim();
            if (!name.toLowerCase(Locale.ROOT).startsWith("estudio ")) continue;

            try {
                int value = Integer.parseInt(
                        name.substring("Estudio ".length()).trim()
                );
                if (value > max) max = value;
            } catch (Exception ignored) {
                // Custom names do not participate in automatic numbering.
            }
        }

        return "Estudio " + (max + 1);
    }

    /**
     * Persists one study synchronously and reports whether Android confirmed the
     * compatibility-mirror write. The build-time SQLite migration also stores
     * the same JSON payload in the indexed local database.
     */
    public static boolean save(Context context, StudyData study) {
        if (context == null
                || study == null
                || isBlank(study.id)
                || isBlank(study.imageUri)) {
            return false;
        }

        final long updatedAt = System.currentTimeMillis();
        study.updatedAt = updatedAt;

        try {
            JSONObject root = new JSONObject();

            root.put("schemaVersion", SCHEMA_VERSION);
            root.put("id", study.id);
            root.put("mode", study.mode == null ? "STEINER" : study.mode);
            root.put("imageUri", study.imageUri);
            root.put("studyName", safe(study.studyName));
            root.put("patientName", safe(study.patientName));
            root.put("patientAge", safe(study.patientAge));
            root.put("patientSex", safe(study.patientSex));
            root.put("updatedAt", updatedAt);
            root.put("locked", study.locked);

            if (Double.isNaN(study.mmPerPixel) || Double.isInfinite(study.mmPerPixel)) {
                root.put("mmPerPixel", JSONObject.NULL);
            } else {
                root.put("mmPerPixel", study.mmPerPixel);
            }
            root.put("calibrationLabel", safe(study.calibrationLabel));

            JSONArray labels = new JSONArray();
            if (study.labels != null) {
                for (String label : study.labels) {
                    labels.put(safe(label));
                }
            }
            root.put("labels", labels);

            JSONArray points = new JSONArray();
            if (study.points != null) {
                for (PointF p : study.points) {
                    if (p == null
                            || !Float.isFinite(p.x)
                            || !Float.isFinite(p.y)) {
                        points.put(JSONObject.NULL);
                    } else {
                        JSONObject obj = new JSONObject();
                        obj.put("x", p.x);
                        obj.put("y", p.y);
                        points.put(obj);
                    }
                }
            }
            root.put("points", points);

            JSONArray locks = new JSONArray();
            if (study.pointLocks != null) {
                for (Boolean value : study.pointLocks) {
                    locks.put(Boolean.TRUE.equals(value));
                }
            }
            root.put("pointLocks", locks);

            SharedPreferences prefs =
                    context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);

            Set<String> ids = new HashSet<>(
                    prefs.getStringSet(IDS, Collections.emptySet())
            );
            ids.add(study.id);

            boolean committed = prefs.edit()
                    .putString("study_" + study.id, root.toString())
                    .putStringSet(IDS, ids)
                    .commit();

            if (!committed) {
                Log.e(TAG, "SharedPreferences commit returned false for study " + study.id);
            }
            return committed;

        } catch (Exception e) {
            Log.e(TAG, "Could not persist study " + study.id, e);
            return false;
        }
    }

    public static StudyData load(Context context, String id) {
        if (context == null || isBlank(id)) return null;

        SharedPreferences prefs =
                context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);

        String raw = prefs.getString("study_" + id, null);
        if (raw == null) return null;

        try {
            JSONObject root = new JSONObject(raw);
            int schemaVersion = root.optInt("schemaVersion", 1);
            if (schemaVersion < 1 || schemaVersion > SCHEMA_VERSION) {
                Log.e(TAG, "Unsupported study schema version: " + schemaVersion);
                return null;
            }

            StudyData study = new StudyData();
            study.id = root.optString("id", id);
            study.mode = root.optString("mode", "STEINER");
            study.imageUri = root.optString("imageUri", null);
            study.studyName = root.optString("studyName", "");
            study.patientName = root.optString("patientName", "");
            study.patientAge = root.optString("patientAge", "");
            study.patientSex = root.optString("patientSex", "");
            study.updatedAt = root.optLong("updatedAt", 0L);
            study.locked = root.optBoolean("locked", false);
            study.mmPerPixel = root.isNull("mmPerPixel")
                    ? Double.NaN
                    : root.optDouble("mmPerPixel", Double.NaN);
            study.calibrationLabel = root.optString("calibrationLabel", "");

            if (isBlank(study.studyName)) {
                study.studyName = "Estudio";
            }

            JSONArray labels = root.optJSONArray("labels");
            if (labels != null) {
                for (int i = 0; i < labels.length(); i++) {
                    study.labels.add(labels.optString(i, ""));
                }
            }

            JSONArray points = root.optJSONArray("points");
            if (points != null) {
                for (int i = 0; i < points.length(); i++) {
                    if (points.isNull(i)) {
                        study.points.add(null);
                        continue;
                    }

                    JSONObject p = points.optJSONObject(i);
                    if (p == null) {
                        study.points.add(null);
                        continue;
                    }

                    double x = p.optDouble("x", Double.NaN);
                    double y = p.optDouble("y", Double.NaN);
                    if (!Double.isFinite(x) || !Double.isFinite(y)) {
                        study.points.add(null);
                    } else {
                        study.points.add(new PointF((float) x, (float) y));
                    }
                }
            }

            while (study.points.size() < study.labels.size()) {
                study.points.add(null);
            }
            while (study.points.size() > study.labels.size()) {
                study.points.remove(study.points.size() - 1);
            }

            JSONArray locks = root.optJSONArray("pointLocks");
            if (locks != null) {
                for (int i = 0; i < locks.length(); i++) {
                    study.pointLocks.add(locks.optBoolean(i, false));
                }
            }

            while (study.pointLocks.size() < study.labels.size()) {
                study.pointLocks.add(false);
            }
            while (study.pointLocks.size() > study.labels.size()) {
                study.pointLocks.remove(study.pointLocks.size() - 1);
            }

            return study;

        } catch (Exception e) {
            Log.e(TAG, "Could not load study " + id, e);
            return null;
        }
    }

    public static List<StudyData> list(Context context) {
        if (context == null) return new ArrayList<>();

        SharedPreferences prefs =
                context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);

        Set<String> ids =
                prefs.getStringSet(IDS, Collections.emptySet());

        List<StudyData> result = new ArrayList<>();

        for (String id : ids) {
            StudyData study = load(context, id);
            if (study != null) result.add(study);
        }

        result.sort((a, b) -> Long.compare(b.updatedAt, a.updatedAt));
        return result;
    }

    public static boolean delete(Context context, String id) {
        if (context == null || isBlank(id)) return false;

        StudyData removedStudy = load(context, id);

        SharedPreferences prefs =
                context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);

        Set<String> ids = new HashSet<>(
                prefs.getStringSet(IDS, Collections.emptySet())
        );
        ids.remove(id);

        boolean committed = prefs.edit()
                .remove("study_" + id)
                .putStringSet(IDS, ids)
                .commit();

        if (!committed) {
            Log.e(TAG, "Could not delete study " + id);
            return false;
        }

        if (removedStudy == null || isBlank(removedStudy.imageUri)) {
            return true;
        }

        boolean stillUsed = false;
        for (String remainingId : ids) {
            StudyData remaining = load(context, remainingId);
            if (remaining != null
                    && removedStudy.imageUri.equals(remaining.imageUri)) {
                stillUsed = true;
                break;
            }
        }

        if (!stillUsed) {
            try {
                context.getContentResolver().releasePersistableUriPermission(
                        Uri.parse(removedStudy.imageUri),
                        Intent.FLAG_GRANT_READ_URI_PERMISSION
                );
            } catch (SecurityException ignored) {
                // Provider may not have granted a persistable permission.
            } catch (Exception e) {
                Log.w(TAG, "Could not release image URI permission", e);
            }
        }

        return true;
    }

    private static boolean isBlank(String value) {
        return value == null || value.trim().isEmpty();
    }

    private static String safe(String value) {
        return value == null ? "" : value;
    }
}
