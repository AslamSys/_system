# 📊 Event Analyzer

**Container:** `event-analyzer`  
**Ecossistema:** Segurança  
**Hardware:** Jetson Orin Nano  
**Tecnologias:** Python + OpenCV + NumPy

---

## 📋 Propósito

Analisa sequências de detecções YOLO para identificar comportamentos suspeitos: loitering, intrusion, fall detection, zone violations.

---

## 🎯 Responsabilidades

- ✅ Loitering detection (pessoa parada > 5 min)
- ✅ Intrusion detection (entrada em zona restrita)
- ✅ Fall detection (pessoa horizontal no chão)
- ✅ Zone crossing (linha virtual cruzada)
- ✅ Heatmaps de movimento

---

## 📊 Algoritmos

```yaml
Loitering: Tracking ID parado > 300s
Intrusion: Bounding box dentro de polígono restrito
Fall Detection: Aspect ratio bbox > 2.0
Zone Crossing: Centroid atravessa linha
Heatmap: Densidade de movimento por pixel
```

---

## 🔌 NATS Topics

### Subscribe
- `seguranca.yolo.detections` - Detecções do YOLO

### Publish
- `seguranca.event.loitering` - Pessoa parada suspeita
- `seguranca.event.intrusion` - Invasão detectada
- `seguranca.event.fall` - Queda detectada
- `seguranca.event.crossing` - Linha cruzada

---

## 🚀 Docker

```yaml
event-analyzer:
  build: ./event-analyzer
  environment:
    - LOITERING_THRESHOLD_SECONDS=300
    - FALL_ASPECT_RATIO=2.0
    - ZONES_CONFIG=/config/zones.json
  volumes:
    - ./config:/config
  deploy:
    resources:
      limits:
        cpus: '0.5'
        memory: 512M
```

---

## 🗺️ Configuração de Zonas

```json
{
  "cam_1": {
    "restricted_zones": [
      {
        "name": "quintal",
        "polygon": [[100,200], [500,200], [500,600], [100,600]],
        "allowed_hours": "08:00-18:00"
      }
    ],
    "crossing_lines": [
      {
        "name": "entrada_principal",
        "p1": [300, 400],
        "p2": [600, 400],
        "direction": "both"
      }
    ]
  }
}
```

---

## 🔄 Changelog

### v1.0.0
- ✅ Loitering detection
- ✅ Zone intrusion
- ✅ Fall detection
- ✅ Line crossing
