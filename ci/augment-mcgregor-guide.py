from pathlib import Path

# Runs after extend-clinical-build.py. It makes the cranio-cervical visual guide
# explicit: McGregor plane, odontoid plane and the constructed/implicit references
# used by the measurements are all visible in the same schematic.

view = Path('app/src/main/java/com/cefalo/angulos/ReferenceDiagramView.java')
s = view.read_text(encoding='utf-8')

# Keep the analysis mode so landmarks shared by airway and posture (ENA/ENP, H, etc.)
# can open the appropriate diagram for the module that is being traced.
s = s.replace(
    '    private String label = "";\n',
    '    private String label = "";\n    private String mode = "";\n',
    1
)

s = s.replace(
    '''    public void setLandmark(String label) {\n        this.label = label == null ? "" : label;\n        invalidate();\n    }\n''',
    '''    public void setLandmark(String label) {\n        this.label = label == null ? "" : label;\n        invalidate();\n    }\n\n    public void setContext(String mode, String label) {\n        this.mode = mode == null ? "" : mode;\n        this.label = label == null ? "" : label;\n        invalidate();\n    }\n''',
    1
)

old_draw = '''        if (isCervical()) drawCervical(canvas);\n        else if (isAirway()) drawAirway(canvas);\n        else if (isHyoid()) drawHyoid(canvas);\n        else drawCephalometric(canvas);\n'''
new_draw = '''        if ("VERTEBRAL".equals(mode)) {\n            if (isHyoid()) drawHyoid(canvas);\n            else drawCervical(canvas);\n        } else if ("AIRWAY".equals(mode)) {\n            drawAirway(canvas);\n        } else if (isCervical()) drawCervical(canvas);\n        else if (isAirway()) drawAirway(canvas);\n        else if (isHyoid()) drawHyoid(canvas);\n        else drawCephalometric(canvas);\n'''
s = s.replace(old_draw, new_draw, 1)

start = s.find('    private void drawCervical(Canvas c) {')
end = s.find('    private void drawHyoid(Canvas c) {', start)
if start == -1 or end == -1:
    raise RuntimeError('Could not locate drawCervical method')

new_cervical = r'''    private void drawCervical(Canvas c) {
        float w = getWidth(), h = getHeight();

        // Simplified posterior cranial base and hard palate.
        Path cranial = new Path();
        cranial.moveTo(w*.10f,h*.22f);
        cranial.cubicTo(w*.22f,h*.10f,w*.48f,h*.08f,w*.62f,h*.18f);
        cranial.cubicTo(w*.67f,h*.22f,w*.66f,h*.28f,w*.60f,h*.31f);
        c.drawPath(cranial,line);

        // Hard palate: ANS -> PNS/ENP. PNS is the posterior endpoint used by McGregor.
        c.drawLine(w*.18f,h*.33f,w*.43f,h*.34f,line);
        point(c,w*.18f,h*.33f,"ENA");
        point(c,w*.43f,h*.34f,"PNS/ENP");

        // M/C0: lowest point of the occipital curve. McGregor = PNS/ENP -> M/C0.
        float mx = w*.60f, my = h*.29f;
        point(c,mx,my,"M/C0");
        Paint mg = new Paint(line);
        mg.setStrokeWidth(dp(3));
        mg.setColor(Color.rgb(126,87,194));
        c.drawLine(w*.43f,h*.34f,mx,my,mg);
        c.drawText("Plano de McGregor", w*.28f,h*.25f,text);

        // Atlas (C1): anterior/posterior arches, with the posterior-superior point
        // used for the C0-C1 perpendicular distance.
        float atlasY = h*.39f;
        c.drawArc(w*.48f,atlasY-dp(13),w*.66f,atlasY+dp(13),185,170,false,line);
        point(c,w*.62f,atlasY-dp(5),"C1 post.");
        point(c,w*.50f,atlasY,"AA");

        // Odontoid and C2 body.
        float x = w*.58f;
        c.drawRoundRect(x-dp(8), h*.42f, x+dp(8), h*.57f, dp(6), dp(6), line);
        c.drawRoundRect(x-dp(27), h*.56f, x+dp(27), h*.62f, dp(5), dp(5), line);
        point(c,x,h*.42f,"Od ápice");
        point(c,x+dp(24),h*.62f,"C2ai");
        point(c,x-dp(15),h*.46f,"CV2tg");
        point(c,x-dp(25),h*.62f,"CV2ip");

        // Odontoid plane = apex of dens -> C2 antero-inferior.
        Paint od = new Paint(line);
        od.setStrokeWidth(dp(3));
        od.setColor(Color.rgb(34,191,199));
        c.drawLine(x,h*.42f,x+dp(24),h*.62f,od);
        c.drawText("Plano odontoideo", w*.64f,h*.50f,text);

        // C0-C1 is a perpendicular relationship to McGregor; show its construction.
        c.drawLine(w*.62f,atlasY-dp(5),w*.61f,h*.30f,od);
        c.drawText("C0–C1 ⟂ McGregor", w*.05f,h*.43f,text);

        // Remaining cervical bodies. Their posterior-inferior landmarks build CVT/EVT.
        for (int i=0;i<5;i++) {
            int level = i + 3;
            float top = h*(.64f + i*.065f);
            c.drawRoundRect(x-dp(27), top, x+dp(27), top+h*.045f, dp(4), dp(4), line);
            c.drawText("C"+level, x+dp(34), top+h*.04f, text);
        }
        point(c,x-dp(25),h*(.64f+1*.065f)+h*.045f,"CV4ip");
        point(c,x-dp(25),h*(.64f+2*.065f)+h*.045f,"C5pi");
        point(c,x-dp(25),h*(.64f+3*.065f)+h*.045f,"CV6ip");
        point(c,x-dp(25),h*(.64f+4*.065f)+h*.045f,"C7pi");

        // Cervical construction lines that were previously implicit.
        c.drawLine(x-dp(15),h*.46f,x-dp(25),h*(.64f+1*.065f)+h*.045f,line); // CVT
        c.drawLine(x-dp(25),h*(.64f+1*.065f)+h*.045f,x-dp(25),h*(.64f+3*.065f)+h*.045f,line); // EVT
        c.drawText("CVT", w*.43f,h*.69f,text);
        c.drawText("EVT", w*.38f,h*.83f,text);

        c.drawText("McGregor = PNS/ENP–M/C0 · Odontoideo = Od ápice–C2ai", dp(8), h*.95f, text);
        c.drawText("Si C6/C7 no se ven: use C2–C5 solo como evaluación parcial", dp(8), h*.995f-dp(2), text);
    }

'''
s = s[:start] + new_cervical + s[end:]
view.write_text(s, encoding='utf-8')

# Pass the current module into the diagram so shared landmarks route correctly.
activity = Path('app/src/main/java/com/cefalo/angulos/AnalysisActivity.java')
a = activity.read_text(encoding='utf-8')
a = a.replace('        diagram.setLandmark(label);\n', '        diagram.setContext(mode, label);\n', 1)
activity.write_text(a, encoding='utf-8')

# Clarify the point labels in the textual guide as well.
guide = Path('app/src/main/java/com/cefalo/angulos/PointGuide.java')
g = guide.read_text(encoding='utf-8')
g = g.replace(
    'GUIDE.put("Occipital", "Punto occipital para el plano de McGregor: punto más inferior de la escama/base occipital visible. Únalo con ENP/PNS para formar el plano de McGregor.");',
    'GUIDE.put("Occipital", "M/C0 para el plano de McGregor: marque el punto más inferior de la curva occipital visible. El plano de McGregor se forma con exactamente 2 referencias: PNS/ENP + M/C0. No use opisthion como sustituto si el protocolo elegido es McGregor.");'
)
g = g.replace(
    'GUIDE.put("C1 sup. posterior", "C1 superior/posterior: punto más superior y posterior del arco posterior del atlas. Se utiliza para medir perpendicularmente el espacio C0-C1 respecto al plano de McGregor.");',
    'GUIDE.put("C1 sup. posterior", "C1 superior/posterior: punto más superior y posterior del arco posterior del atlas. La distancia C0-C1 se construye desde este punto perpendicularmente al plano de McGregor (PNS/ENP-M/C0); por eso PNS/ENP y M/C0 están implícitos en esa medición aunque no formen parte del nombre C0-C1.");'
)
guide.write_text(g, encoding='utf-8')

print('McGregor and implicit cranio-cervical references added to visual guide.')
