# TFI · Gestión de Redes Informáticas · EduTech Campus S.A.

> Trabajo Práctico Integrador · UCBA · 2026
> **Caso de análisis:** rediseño integral de la red de un campus educativo (CABA + 2 sedes regionales) para soportar BYOD, clases en vivo por videoconferencia, NAC/802.1X, segmentación lógica y videovigilancia IP.

El enunciado completo está en [`Contexto/TFI -Gestión de Redes Informáticas Edu Tech Campus.pdf`](./Contexto/) y en [`Contexto/Enunciado-TP.txt`](./Contexto/Enunciado-TP.txt).

---

## Estructura del repositorio

```
TP-Redes/
├── Contexto/                              # Material base provisto por la cátedra
│   ├── TFI -Gestión de Redes...pdf        #   ↳ Enunciado oficial del TP
│   ├── Enunciado-TP.txt                   #   ↳ Versión texto del enunciado
│   └── Descripcion_fisica_campus.png      #   ↳ Imagen referencia del campus
│
├── Superado/                              # Versiones viejas/descartadas (no borrar)
│   ├── Diagrama Topologico.drawio         #   ↳ Topología v1 antes del rediseño
│   ├── Diagrama_Fisico.html               #   ↳ Diagrama físico tipo bloques (descartado)
│   └── Plano_Arquitectonico.html          #   ↳ Plano arquitectónico v1 (con dispositivos sobre el mapa)
│
├── Diagrama Topologico.drawio             # ⚠ Topología actual (PENDIENTE rediseño completo)
├── Diagrama Logico de Redes.xlsx          # ⚠ Diagrama lógico (PENDIENTE actualizar VLANs)
├── Diagrama_Arquitectonico.html           # Vista por piso con dispositivos (referencia rápida)
├── Plano_Arquitectonico.drawio            # ⭐ Plano arquitectónico LIMPIO (base para heatmap)
├── Plano_Arquitectonico_Heatmap.drawio    # ⭐ Plano + heatmap WiFi 5GHz con 22 APs
├── Tabla de Vlans - Switches.xlsx         # ⚠ Tabla VLANs (PENDIENTE actualizar con los 9 finales)
├── _generate_heatmap.py                   # Script generador del heatmap (regenerable)
└── README.md
```

⭐ = archivo principal · ⚠ = pendiente de actualización

---

## Lo hecho hasta hoy (estado del diseño)

### 1) Arquitectura LAN definida

- **Core colapsado** en el campus central (CABA): 2 switches L3 en stack/MLAG en el datacenter del P3.
- **Acceso por piso:** 4 IDFs (PB, P1, P2 y el MDF del P3) con switches L2 PoE+ uplinkeados al core con doble fibra LACP.
- **Sedes regionales (Rosario, Mendoza):** core+acceso reducido, FortiGate local, VPN IPsec al campus central.

### 2) Segmentación VLAN definitiva (9 VLANs)

| # | VLAN | Tag | Subred sugerida | Propósito |
|---|---|---|---|---|
| 1 | `MGMT` | 10 | `10.10.10.0/24` | Gestión de switches, APs, FortiGate, UPS, controladora WiFi |
| 2 | `Datacenter` | 20 | `10.10.20.0/24` | Servidores AD/DNS/DHCP/File/Backup/IPBX/Monitoreo/WLC |
| 3 | `Administración` | 30 | `10.10.30.0/24` | Staff admin, dirección, puestos docentes cableados, teléfonos IP |
| 4 | `Docente` (WiFi) | 40 | `10.10.40.0/22` | Notebooks/cels docentes vía SSID `EDU-Docentes` (WPA3-Enterprise) |
| 5 | `Alumno` (cableado) | 50 | `10.10.50.0/24` | PCs Labs P1 (60) + PCs Biblioteca + WS Lab Multimedia P2 |
| 6 | `Alumno-WiFi` | 60 | `10.10.60.0/22` | BYOD alumnos vía SSID `EDU-Alumnos` (Portal cautivo + WPA3-E) |
| 7 | `Invitado` | 70 | `10.10.70.0/24` | Visitas vía SSID `EDU-Invitados` (sólo Internet) |
| 8 | `IoT` | 80 | `10.10.80.0/24` | Sensores, lectores biométricos, tornos, displays, equipos producción estudio |
| 9 | `CCTV` | 90 | `10.10.90.0/24` | Cámaras IP + NVR (aislada, sólo NVR sale a otras VLANs) |

> **Nota DMZ:** se omite por simplicidad del TP. Si se aprueba en una próxima iteración, se agregaría como VLAN 100 con web/mail/portales expuestos a Internet.

### 3) WLAN diseñada (4 SSIDs)

| SSID | VLAN destino | Auth |
|---|---|---|
| `EDU-Corp` | Administración | WPA3-Enterprise (RADIUS contra AD) |
| `EDU-Docentes` | Docente | WPA3-Enterprise (RADIUS contra AD) |
| `EDU-Alumnos` | Alumno-WiFi | Portal cautivo + WPA3-Enterprise |
| `EDU-Invitados` | Invitado | Portal cautivo sin auth |

**22 APs Aruba Instant On en el campus central:**
- 16 × **AP22** (estándar) — ~AR$ 380.000 c/u
- 6 × **AP25** (alta densidad) — para Aula Magna (×2), Labs P1 (×2), Lab Multimedia P2, Sala Videoconferencia — ~AR$ 550.000 c/u
- Sin licencia anual (gestión cloud gratuita).
- **Inversión APs Campus Central: ~AR$ 9.380.000**
- Datacenter P3 **sin WiFi por diseño** (zona segura).

Plan de canales 5 GHz: `36, 52, 100, 116, 132, 149` distribuidos para evitar co-channel interference horizontal y verticalmente entre pisos.

### 4) Plano arquitectónico (Plano_Arquitectonico.drawio)

- 4 pisos con paredes interiores, doors, fixtures (sanitarios, mostradores, racks).
- **Doble circulación horizontal por piso:** pasillo central (acceso a aulas/salas) + pasillo posterior de servicio (acceso a baños/IDF/depósito).
- **Núcleo de circulación vertical a la derecha** (x≈1100–1310): escaleras + ascensor + hall asc., conecta los dos pasillos en cada piso.
- **Paso transversal** entre las salas centrales (Lab A/Lab B, Biblioteca/Aula Magna, etc.) para no obligar a recorrer todo el piso.
- IDF dedicado en cada piso (PB, P1, P2) y MDF en P3 (datacenter).

### 5) Heatmap WiFi (Plano_Arquitectonico_Heatmap.drawio)

- Mismo plano arquitectónico + heatmap por AP (3 zonas concéntricas):
  - 🟢 **Verde** ≥ -65 dBm (excelente · video HD)
  - 🟡 **Amarillo** -65 a -75 dBm (aceptable · web/email)
  - 🔴 **Rojo** -75 a -85 dBm (marginal · reasoc.)
- Cada AP etiquetado con su código (`AP-PB-01`, etc.), modelo y canal asignado.
- Leyenda al pie de cada piso con resumen ejecutivo.

### 6) Repositorio versionado

- Conectado a GitHub: [`mdBricons/Gestion-Redes-Informaticas`](https://github.com/mdBricons/Gestion-Redes-Informaticas)
- Branch principal: `main`

---

## Pendientes — Pasos siguientes (orden sugerido)

### Día siguiente (prioridad alta)

- [ ] **1. Actualizar `Tabla de Vlans - Switches.xlsx`** con las 9 VLANs definitivas
   - Hoja **"VLANs maestras"**: ID, nombre, tag, subred, gateway, DHCP, DNS, QoS/DSCP, notas
   - Hoja **"VLANs por switch"**: por cada switch (SW-CORE-01/02, SW-DC-ToR, SW-IDF-PB/P1/P2/MDF) listar VLANs presentes, puertos access vs trunk
   - Hoja **"Mapeo SSID → VLAN"**: 4 SSIDs con su VLAN destino y modo de autenticación

- [ ] **2. Rediseñar `Diagrama Topologico.drawio`** según la arquitectura final
   - Mover doble uplink LACP entre acceso y core
   - Marcar VPN IPsec con sedes regionales
   - Limpiar elementos del v1 que ya no aplican
   - Sumar leyenda y tabla de VLANs en el mismo .drawio

- [ ] **3. Tabla de cámaras CCTV** (videovigilancia, punto 4.7 del TFI)
   - Lista de cámaras por piso/ubicación (lobby, pasillos, accesos, Aula Magna, Labs, datacenter)
   - Bitrate por cámara (estimar 4-8 Mbps a 1080p H.265)
   - Cálculo de capacidad del NVR (cantidad × bitrate × retención en días)
   - Segmentación: CCTV aislada, sólo NVR puede ser accedido desde MGMT

### Día +2 / +3

- [ ] **4. Diseño WAN** (punto 4.4 del TFI)
   - Selección de ISP principal (fibra dedicada) + ISP backup (FTTH consumer-grade)
   - Túnel IPsec a Rosario y Mendoza
   - SD-WAN básico (FortiGate native SD-WAN)
   - Criterios QoS exigidos al proveedor

- [ ] **5. Políticas QoS** (punto 4.5)
   - DSCP marking por VLAN (ya pre-asignado en este README)
   - Prioridad estricta a VC en vivo y voz
   - Queue scheduling en switches L3 y FortiGate

- [ ] **6. NAC / 802.1X** (punto 4.6)
   - RADIUS server (FreeRADIUS o Microsoft NPS)
   - Integración con AD
   - Política para BYOD (portal cautivo) vs notebooks corporativas (cert + AD)
   - Acción para dispositivos no reconocidos: VLAN de cuarentena

- [ ] **7. Datacenter detallado** (punto 4.8)
   - Cantidad de racks (ya hay 8 racks en el plano)
   - Redundancia eléctrica (UPS principal + UPS secundario + generador)
   - Refrigeración N+1 (ya esbozado: A/C principal + A/C respaldo)
   - Monitoreo (Zabbix/PRTG) y alertas
   - Mantrap con doble huella (ya en el plano)

### Día +4 / +5

- [ ] **8. Presupuesto comparativo** (punto 10 del TFI)
   - Equipamiento (switches, APs, FortiGate, servidores, UPS, racks)
   - Cableado estructurado (TIA/EIA-568-C.2): fibra OM4 troncal + UTP Cat6A horizontal
   - Mano de obra (instalación + certificación)
   - Dos proveedores reales en Argentina (ej: Diveo + Iplan, o ITC + Telecentro Empresas, etc.)
   - Cotizaciones expresadas en AR$ a junio 2026

- [ ] **9. Documento final TFI**
   - Memoria descriptiva (Word/PDF) explicando cada punto del enunciado (4.1 a 4.8 + objetivos 1 a 10)
   - Cada justificación atada al diagrama/plano/tabla correspondiente
   - Sección "alternativas evaluadas" para cada decisión técnica

---

## Convenciones del proyecto

- **Naming switches:** `SW-{rol}-{ubicación}-{nn}`
  - Ejemplos: `SW-CORE-01`, `SW-IDF-PB-01`, `SW-DC-ToR-01`
- **Naming APs:** `AP-{piso}-{nn}`
  - Ejemplos: `AP-PB-04`, `AP-P1-03`
- **Subnetting:** `10.10.{tag_vlan}.0/24` para VLANs chicas, `/22` para Docente-WiFi y Alumno-WiFi (rango grande por roaming + BYOD).
- **VLAN tags:** múltiplos de 10 (más fácil de recordar y deja espacio para crecer).
- **Cableado:** Cat6A horizontal (90 m máx) + OM4 vertical para uplinks entre IDFs y MDF.

---

## Cómo abrir cada archivo

| Extensión | Programa recomendado |
|---|---|
| `.drawio` | [draw.io desktop](https://www.drawio.com/) o [diagrams.net](https://app.diagrams.net/) (web) |
| `.html` | Cualquier navegador (Chrome, Firefox, Edge) |
| `.xlsx` | Microsoft Excel o LibreOffice Calc |
| `.pdf` | Cualquier lector PDF |
| `.py` | Python 3.10+ (`py _generate_heatmap.py` regenera el heatmap si modificás APs) |

---

## Equipo

Trabajo Práctico Final · Cátedra Gestión de Redes Informáticas · UCBA
