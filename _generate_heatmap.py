"""Genera Plano_Arquitectonico_Heatmap.drawio insertando heatmap WiFi 5GHz
sobre cada piso del Plano_Arquitectonico.drawio existente."""

import re
from pathlib import Path

SRC = Path("Plano_Arquitectonico.drawio")
DST = Path("Plano_Arquitectonico_Heatmap.drawio")

# Radios de cobertura en px (escala ~22 px/m)
# AP22 (estándar):   green 6.4m  · yellow 11m   · red 15.5m
# AP25 (alta dens.): green 7.3m  · yellow 12.3m · red 17.3m
R_22 = (140, 240, 340)
R_25 = (160, 270, 380)

# Definición de APs por piso
# (id_num, cx, cy, model, channel, descripcion)
APS = {
    "pb": [
        (1, 450, 240, "AP22", 36,  "Lobby / Recepción"),
        (2, 950, 240, "AP22", 52,  "SUM"),
        (3, 300, 480, "AP22", 100, "Biblioteca"),
        (4, 700, 430, "AP25", 116, "Aula Magna · tarima"),
        (5, 970, 540, "AP25", 149, "Aula Magna · fondo"),
        (6, 580, 605, "AP22", 132, "Pasillo posterior"),
    ],
    "p1": [
        (1, 330, 395, "AP22", 36,  "Pasillo central · T1-T2"),
        (2, 840, 395, "AP22", 52,  "Pasillo central · T3-T4"),
        (3, 310, 520, "AP25", 100, "Lab Informática A"),
        (4, 850, 520, "AP25", 116, "Lab Informática B"),
        (5, 1200, 500, "AP22", 132, "Núcleo / Hall asc."),
        (6, 500, 645, "AP22", 149, "Pasillo posterior · IDF"),
    ],
    "p2": [
        (1, 330, 250, "AP25", 36,  "Lab Multimedia"),
        (2, 860, 200, "AP22", 52,  "Estudio · cabina"),
        (3, 860, 310, "AP22", 100, "Sala Control Técnico"),
        (4, 330, 520, "AP25", 116, "Sala Videoconferencia"),
        (5, 500, 645, "AP22", 132, "Pasillo posterior · IDF"),
    ],
    "p3": [
        (1, 200, 250, "AP22", 36,  "Dirección"),
        (2, 620, 250, "AP22", 52,  "Administración"),
        (3, 1000, 230, "AP22", 100, "Sala Reuniones"),
        (4, 1200, 500, "AP22", 116, "Núcleo / Hall asc."),
        (5, 500, 720, "AP22", 132, "Sala personal / Archivo"),
    ],
}

# Conteos para los pies de página
def floor_info(floor):
    aps = APS[floor]
    n22 = sum(1 for a in aps if a[3] == "AP22")
    n25 = sum(1 for a in aps if a[3] == "AP25")
    channels = ", ".join(str(a[4]) for a in aps)
    return n22, n25, channels

FLOOR_TITLES = {
    "pb": "PLANTA BAJA",
    "p1": "1° PISO",
    "p2": "2° PISO",
    "p3": "3° PISO · DATACENTER SIN WiFi (zona segura)",
}

def ap_xml(floor, ap):
    n, cx, cy, model, ch, desc = ap
    r_g, r_y, r_r = R_22 if model == "AP22" else R_25
    pid = f"hm-{floor}-{n:02d}"
    # Coordenadas para cada círculo (centrado en cx,cy)
    rx_r, ry_r = cx - r_r, cy - r_r
    rx_y, ry_y = cx - r_y, cy - r_y
    rx_g, ry_g = cx - r_g, cy - r_g
    ic_x, ic_y = cx - 12, cy - 11
    lb_x, lb_y = cx - 55, cy + 13
    return f'''
        <!-- ===== AP-{floor.upper()}-{n:02d} · {desc} · {model} · ch {ch} ===== -->
        <mxCell id="{pid}-r" value="" style="ellipse;fillColor=#ef4444;strokeColor=#dc2626;strokeWidth=0.5;opacity=15;" vertex="1" parent="1">
          <mxGeometry x="{rx_r}" y="{ry_r}" width="{2*r_r}" height="{2*r_r}" as="geometry"/>
        </mxCell>
        <mxCell id="{pid}-y" value="" style="ellipse;fillColor=#facc15;strokeColor=#eab308;strokeWidth=0.5;opacity=25;" vertex="1" parent="1">
          <mxGeometry x="{rx_y}" y="{ry_y}" width="{2*r_y}" height="{2*r_y}" as="geometry"/>
        </mxCell>
        <mxCell id="{pid}-g" value="" style="ellipse;fillColor=#22c55e;strokeColor=#16a34a;strokeWidth=0.5;opacity=35;" vertex="1" parent="1">
          <mxGeometry x="{rx_g}" y="{ry_g}" width="{2*r_g}" height="{2*r_g}" as="geometry"/>
        </mxCell>
        <mxCell id="{pid}-ic" value="((·))" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1e293b;strokeColor=#0f172a;strokeWidth=2;fontColor=#ffffff;fontSize=8;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="{ic_x}" y="{ic_y}" width="24" height="22" as="geometry"/>
        </mxCell>
        <mxCell id="{pid}-lb" value="&lt;b&gt;AP-{floor.upper()}-{n:02d}&lt;/b&gt;&lt;br&gt;&lt;span style=&quot;font-size:8px;color:#475569;&quot;&gt;{model} · ch {ch}&lt;/span&gt;" style="text;html=1;align=center;fontSize=9;fontFamily=Georgia;fontColor=#1e293b;" vertex="1" parent="1">
          <mxGeometry x="{lb_x}" y="{lb_y}" width="110" height="26" as="geometry"/>
        </mxCell>'''

def legend_xml(floor):
    n22, n25, channels = floor_info(floor)
    title = FLOOR_TITLES[floor]
    total = n22 + n25
    pid = f"hm-{floor}-leg"
    summary = f"<b>HEATMAP WiFi 5 GHz · {title}</b> &#160;·&#160; {total} APs Aruba Instant On ({n22}×AP22 + {n25}×AP25) &#160;·&#160; Canales asignados: {channels}"
    return f'''
        <!-- ===== LEGEND HEATMAP {floor.upper()} ===== -->
        <mxCell id="{pid}-bg" value="" style="rounded=0;fillColor=#ffffff;strokeColor=#1f2937;strokeWidth=1;" vertex="1" parent="1">
          <mxGeometry x="70" y="815" width="1170" height="70" as="geometry"/>
        </mxCell>
        <mxCell id="{pid}-title" value="{summary}" style="text;html=1;align=left;verticalAlign=middle;fontSize=10;fontFamily=Georgia;fontColor=#1f2937;" vertex="1" parent="1">
          <mxGeometry x="80" y="820" width="1150" height="20" as="geometry"/>
        </mxCell>
        <mxCell id="{pid}-g" value="" style="rounded=0;fillColor=#22c55e;strokeColor=#16a34a;opacity=50;" vertex="1" parent="1">
          <mxGeometry x="80" y="852" width="20" height="20" as="geometry"/>
        </mxCell>
        <mxCell id="{pid}-glbl" value="Excelente ≥ -65 dBm (video HD)" style="text;html=1;align=left;verticalAlign=middle;fontSize=9;fontFamily=Georgia;fontColor=#1f2937;" vertex="1" parent="1">
          <mxGeometry x="105" y="852" width="220" height="20" as="geometry"/>
        </mxCell>
        <mxCell id="{pid}-y" value="" style="rounded=0;fillColor=#facc15;strokeColor=#eab308;opacity=50;" vertex="1" parent="1">
          <mxGeometry x="335" y="852" width="20" height="20" as="geometry"/>
        </mxCell>
        <mxCell id="{pid}-ylbl" value="Aceptable -65 a -75 dBm (web/email)" style="text;html=1;align=left;verticalAlign=middle;fontSize=9;fontFamily=Georgia;fontColor=#1f2937;" vertex="1" parent="1">
          <mxGeometry x="360" y="852" width="260" height="20" as="geometry"/>
        </mxCell>
        <mxCell id="{pid}-r" value="" style="rounded=0;fillColor=#ef4444;strokeColor=#dc2626;opacity=50;" vertex="1" parent="1">
          <mxGeometry x="630" y="852" width="20" height="20" as="geometry"/>
        </mxCell>
        <mxCell id="{pid}-rlbl" value="Marginal -75 a -85 dBm (reasoc.)" style="text;html=1;align=left;verticalAlign=middle;fontSize=9;fontFamily=Georgia;fontColor=#1f2937;" vertex="1" parent="1">
          <mxGeometry x="655" y="852" width="220" height="20" as="geometry"/>
        </mxCell>
        <mxCell id="{pid}-ap" value="((·))" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1e293b;strokeColor=#0f172a;strokeWidth=2;fontColor=#ffffff;fontSize=8;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="885" y="852" width="24" height="20" as="geometry"/>
        </mxCell>
        <mxCell id="{pid}-aplbl" value="Aruba Instant On AP (mounted en techo)" style="text;html=1;align=left;verticalAlign=middle;fontSize=9;fontFamily=Georgia;fontColor=#1f2937;" vertex="1" parent="1">
          <mxGeometry x="915" y="852" width="320" height="20" as="geometry"/>
        </mxCell>'''


def build_heatmap_block(floor):
    lines = ['', '        <!-- ##############  HEATMAP WiFi 5 GHz · ' + floor.upper() + '  ############## -->']
    for ap in APS[floor]:
        lines.append(ap_xml(floor, ap))
    lines.append(legend_xml(floor))
    return "\n".join(lines)


# Anchors únicos por piso (cell del compás)
ANCHORS = {
    "pb": '<mxCell id="pb-compass-circle"',
    "p1": '<mxCell id="p1-comp-c"',
    "p2": '<mxCell id="p2-comp-c"',
    "p3": '<mxCell id="p3-comp-c"',
}

# Leer fuente
content = SRC.read_text(encoding="utf-8")

# Insertar heatmap antes de cada anchor
for floor, anchor in ANCHORS.items():
    block = build_heatmap_block(floor)
    # buscar línea que contenga el anchor y agregar el bloque antes
    pattern = re.compile(r'(\s*)(<mxCell id="' + re.escape(anchor.split('"')[1]) + r'")')
    match = pattern.search(content)
    if not match:
        print(f"ANCHOR NO ENCONTRADO para {floor}: {anchor}")
        continue
    indent = match.group(1)
    insert_at = match.start()
    content = content[:insert_at] + "\n" + block + "\n" + indent + match.group(2) + content[match.end():]

# Escribir destino
DST.write_text(content, encoding="utf-8")
print(f"OK · {DST.name} generado · {DST.stat().st_size} bytes")
print(f"APs totales: {sum(len(v) for v in APS.values())}")
for f in APS:
    n22, n25, ch = floor_info(f)
    print(f"  {f.upper()}: {n22+n25} APs ({n22}×AP22 + {n25}×AP25) · canales {ch}")
