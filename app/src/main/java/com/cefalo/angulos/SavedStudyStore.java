package com.cefalo.angulos;

import android.content.Context;
import android.content.SharedPreferences;
import android.content.Intent;
import android.graphics.PointF;
import android.net.Uri;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

public final class SavedStudyStore {

    private static final String PREFS = "yom_saved_studies";
    private static final String IDS = "study_ids";

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
        return String.valueOf(System.currentTimeMillis());
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
            }
        }

        return "Estudio " + (max + 1);
    }

    public static void save(Context context, StudyData study) {
        if (study == null || study.id == null || study.imageUri == null) return;

        study.updatedAt = System.currentTimeMillis();

        try {
            JSONObject root = new JSONObject();

            root.put("id", study.id);
            root.put("mode", study.mode);
            root.put("imageUri", study.imageUri);
            root.put("studyName", study.studyName == null ? "" : study.studyName);
            root.put("patientName", study.patientName == null ? "" : study.patientName);
            root.put("patientAge", study.patientAge == null ? "" : study.patientAge);
            root.put("patientSex", study.patientSex == null ? "" : study.patientSex);
            root.put("updatedAt", study.updatedAt);
            root.put("locked", study.locked);
            if (Double.isNaN(study.mmPerPixel) || Double.isInfinite(study.mmPerPixel)) {
                root.put("mmPerPixel", JSONObject.NULL);
            } else {
                root.put("mmPerPixel", study.mmPerPixel);
            }
            root.put("calibrationLabel", study.calibrationLabel == null ? "" : study.calibrationLabel);

            JSONArray labels = new JSONArray();
            for (String label : study.labels) {
                labels.put(label);
            }
            root.put("labels", labels);

            JSONArray points = new JSONArray();
            for (PointF p : study.points) {
                if (p == null) {
                    points.put(JSONObject.NULL);
                } else {
                    JSONObject obj = new JSONObject();
                    obj.put("x", p.x);
                    obj.put("y", p.y);
                    points.put(obj);
                }
            }
            root.put("points", points);

            SharedPreferences prefs =
                    context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);

            Set<String> ids = new HashSet<>(
                    prefs.getStringSet(IDS, Collections.emptySet())
            );
            ids.add(study.id);

            prefs.edit()
                    .putString("study_" + study.id, root.toString())
                    .putStringSet(IDS, ids)
                    .apply();

        } catch (Exception ignored) {
        }
    }

    public static StudyData load(Context context, String id) {
        if (id == null) return null;

        SharedPreferences prefs =
                context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);

        String raw = prefs.getString("study_" + id, null);
        if (raw == null) return null;

        try {
            JSONObject root = new JSONObject(raw);

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

            if (study.studyName == null || study.studyName.trim().isEmpty()) {
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
                    } else {
                        JSONObject p = points.optJSONObject(i);

                        if (p == null) {
                            study.points.add(null);
                        } else {
                            study.points.add(
                                    new PointF(
                                            (float) p.optDouble("x", 0),
                                            (float) p.optDouble("y", 0)
                                    )
                            );
                        }
                    }
                }
            }

            while (study.points.size() < study.labels.size()) {
                study.points.add(null);
            }

            return study;

        } catch (Exception e) {
            return null;
        }
    }

    public static List<StudyData> list(Context context) {
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

    public static void delete(Context context, String id) {
        if (id == null) return;

        StudyData removedStudy = load(context, id);

        SharedPreferences prefs =
                context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);

        Set<String> ids = new HashSet<>(
                prefs.getStringSet(IDS, Collections.emptySet())
        );

        ids.remove(id);

        prefs.edit()
                .remove("study_" + id)
                .putStringSet(IDS, ids)
                .apply();

        if (removedStudy == null
                || removedStudy.imageUri == null
                || removedStudy.imageUri.trim().isEmpty()) {
            return;
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
                context.getContentResolver()
                        .releasePersistableUriPermission(
                                Uri.parse(removedStudy.imageUri),
                                Intent.FLAG_GRANT_READ_URI_PERMISSION
                        );
            } catch (Exception ignored) {
            }
        }
    }
}
