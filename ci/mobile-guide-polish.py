from pathlib import Path

view = Path('app/src/main/java/com/cefalo/angulos/ReferenceDiagramView.java')
s = view.read_text(encoding='utf-8')

# Make every schematic point context-sensitive: the selected landmark is large
# and purple; supporting landmarks remain smaller and gray.
old_point = '''    private void point(Canvas c, float x, float y, String name) {
        c.drawCircle(x,y,dp(4),accent);
        c.drawText(name,x+dp(7),y-dp(5),text);
    }
'''
new_point = '''    private boolean pointMatches(String name) {
        String a = label == null ? "" : label.toLowerCase();
        String b = name == null ? "" : name.toLowerCase();
        if (a.equals(b)) return true;
        if (a.startsWith("cv2tg") && b.startsWith("cv2tg")) return true;
        if (a.startsWith("cv2ip") && b.startsWith("cv2ip")) return true;
        if (a.startsWith("cv4ip") && b.startsWith("cv4ip")) return true;
        if (a.startsWith("cv6ip") && b.startsWith("cv6ip")) return true;
        if (a.startsWith("c5") && b.startsWith("c5")) return true;
        if (a.startsWith("c7") && b.startsWith("c7")) return true;
        if ((a.equals("enp") || a.contains("pns")) && b.contains("pns/enp")) return true;
        if (a.contains("occipital") && b.contains("m/c0")) return true;
        if (a.contains("odontoides") && b.contains("od ápice")) return true;
        if (a.startsWith("ad1") && b.startsWith("ad1")) return true;
        if (a.startsWith("ad2") && b.startsWith("ad2")) return true;
        if (a.startsWith("pas ant") && b.startsWith("pas ant")) return true;
        if (a.startsWith("pas post") && b.startsWith("pas post")) return true;
        return false;
    }

    private void point(Canvas c, float x, float y, String name) {
        boolean active = pointMatches(name);
        Paint marker = new Paint(Paint.ANTI_ALIAS_FLAG);
        marker.setStyle(Paint.Style.FILL);
        marker.setColor(active ? Color.rgb(126,87,194) : Color.rgb(120,126,138));
        c.drawCircle(x, y, dp(active ? 5.5f : 3.0f), marker);
        Paint labelPaint = new Paint(text);
        labelPaint.setColor(active ? Color.rgb(91,53,164) : Color.rgb(70,74,82));
        labelPaint.setFakeBoldText(active);
        c.drawText(name, x+dp(7), y-dp(5), labelPaint);
    }
'''
if old_point in s:
    s = s.replace(old_point, new_point, 1)

# Richer cephalometric construction guide for S, N, A, B, Go, Pg, Po and Or.
start = s.find('    private void drawCephalometric(Canvas c) {')
end = s.find('    private void drawCervical(Canvas c) {', start)
if start != -1 and end != -1:
    new_ceph = r'''    private void drawCephalometric(Canvas c) {
        float w = getWidth(), h = getHeight();
        Path skull = new Path();
        skull.moveTo(w*.16f,h*.61f); skull.cubicTo(w*.10f,h*.24f,w*.32f,h*.09f,w*.61f,h*.14f);
        skull.cubicTo(w*.78f,h*.17f,w*.86f,h*.37f,w*.78f,h*.53f);
        skull.cubicTo(w*.73f,h*.63f,w*.70f,h*.69f,w*.63f,h*.76f);
        skull.cubicTo(w*.54f,h*.88f,w*.30f,h*.84f,w*.25f,h*.70f);
        c.drawPath(skull,line);

        float sx=w*.38f, sy=h*.28f, nx=w*.59f, ny=h*.25f;
        float ax=w*.67f, ay=h*.44f, bx=w*.65f, by=h*.57f;
        float arx=w*.40f, ary=h*.49f, gox=w*.45f, goy=h*.69f;
        float mex=w*.65f, mey=h*.73f, pgx=w*.68f, pgy=h*.63f;
        float pox=w*.39f, poy=h*.38f, orx=w*.58f, ory=h*.39f;

        Paint construct = new Paint(line);
        construct.setColor(Color.rgb(34,191,199));
        construct.setStrokeWidth(dp(2.4f));
        c.drawLine(sx,sy,nx,ny,construct); // SN always visible
        if (label.equals("A") || label.equals("N")) c.drawLine(nx,ny,ax,ay,construct);
        if (label.equals("B") || label.equals("N")) c.drawLine(nx,ny,bx,by,construct);
        if (label.equals("Po") || label.equals("Or") || label.contains("Frankfort")) {
            c.drawLine(pox,poy,orx,ory,construct);
            c.drawText("Frankfort Po–Or", w*.40f,h*.34f,text);
        }
        if (label.equals("Go")) {
            c.drawLine(arx,ary,gox,goy,construct);
            c.drawLine(gox,goy,mex,mey,construct);
            c.drawLine(gox,goy,gox+dp(42),goy-dp(30),construct);
            c.drawText("Go: 2 tangentes + bisectriz", dp(10), dp(18), text);
        }

        point(c,sx,sy,"S"); point(c,nx,ny,"N"); point(c,ax,ay,"A"); point(c,bx,by,"B");
        point(c,arx,ary,"Ar"); point(c,gox,goy,"Go"); point(c,mex,mey,"Me"); point(c,pgx,pgy,"Pg");
        point(c,pox,poy,"Po"); point(c,orx,ory,"Or");
        c.drawText("SN", (sx+nx)/2, (sy+ny)/2-dp(6), text);
        c.drawText("El punto morado es el landmark seleccionado", dp(10), h-dp(10), text);
    }

'''
    s = s[:start] + new_ceph + s[end:]

# Airway guide: show the actual AD1 and AD2 constructions rather than only a
# generic pharyngeal wall.
start = s.find('    private void drawAirway(Canvas c) {')
end = s.find('    private boolean pointMatches(', start)
if end == -1:
    end = s.find('    private void point(Canvas c', start)
if start != -1 and end != -1:
    new_airway = r'''    private void drawAirway(Canvas c) {
        float w=getWidth(), h=getHeight();
        Path face = new Path();
        face.moveTo(w*.17f,h*.20f); face.cubicTo(w*.38f,h*.08f,w*.69f,h*.12f,w*.73f,h*.28f);
        face.cubicTo(w*.78f,h*.42f,w*.70f,h*.51f,w*.72f,h*.70f);
        c.drawPath(face,line);

        Paint construct = new Paint(line);
        construct.setColor(Color.rgb(34,191,199));
        construct.setStrokeWidth(dp(2.4f));

        float sx=w*.29f, sy=h*.22f, bax=w*.40f, bay=h*.36f;
        float enax=w*.35f,enay=h*.42f,enpx=w*.57f,enpy=h*.42f;
        float px=w*.64f,py=h*.58f;
        float ad1x=w*.77f,ad1y=h*.39f, ad2x=w*.77f,ad2y=h*.50f;
        float pasaX=w*.69f,pasaY=h*.72f,paspX=w*.78f,paspY=h*.72f;

        // Palate and posterior wall.
        c.drawLine(enax,enay,enpx,enpy,line);
        c.drawLine(enpx,enpy,px,py,line);
        c.drawLine(w*.78f,h*.30f,w*.78f,h*.81f,line);

        // AD1 = intersection of ENP/PNS-Ba with the anterior adenoid/posterior wall.
        c.drawLine(enpx,enpy,bax,bay,construct);
        // AD2 = perpendicular from ENP/PNS to S-Ba.
        c.drawLine(sx,sy,bax,bay,construct);
        c.drawLine(enpx,enpy,ad2x,ad2y,construct);
        // PAS level cue.
        c.drawLine(pasaX,pasaY,paspX,paspY,construct);

        point(c,sx,sy,"S"); point(c,bax,bay,"Ba");
        point(c,enax,enay,"ENA"); point(c,enpx,enpy,"PNS/ENP"); point(c,px,py,"P");
        point(c,ad1x,ad1y,"AD1"); point(c,ad2x,ad2y,"AD2");
        point(c,pasaX,pasaY,"PAS ant."); point(c,paspX,paspY,"PAS post.");

        if (label.startsWith("AD1")) c.drawText("AD1: sobre la línea PNS/ENP–Ba", dp(10), dp(18), text);
        else if (label.startsWith("AD2")) c.drawText("AD2: perpendicular desde PNS/ENP hacia S–Ba", dp(10), dp(18), text);
        else c.drawText("Construcciones de vía aérea · no coloque puntos al azar", dp(10), dp(18), text);
    }

'''
    s = s[:start] + new_airway + s[end:]

view.write_text(s, encoding='utf-8')
print('Original landmark guides refined with selected-point highlighting and constructions.')
