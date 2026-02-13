# 🚨 Alert Manager

**Container:** `alert-manager`  
**Ecossistema:** Segurança  
**Hardware:** Jetson Orin Nano  
**Tecnologias:** Node.js + NATS

---

## 📋 Propósito

Gerencia alertas de segurança, priorização (normal < alerta < crítico < emergência), cooldown anti-spam e envio ao Mordomo via NATS.

---

## 🎯 Responsabilidades

- ✅ Receber eventos de todos os containers
- ✅ Priorizar alertas (scoring)
- ✅ Cooldown anti-spam (1 alerta/min por câmera)
- ✅ Gerar snapshots + clips de vídeo
- ✅ Enviar ao Mordomo via NATS

---

## 📊 Prioridades

```yaml
NORMAL: Movimento cotidiano
  - Pessoa conhecida entrando
  - Pet transitando

ALERTA: Incomum mas não urgente
  - Pessoa desconhecida (dia)
  - Veículo parado > 10 min
  
CRÍTICO: Suspeito, requer atenção
  - Pessoa desconhecida (noite)
  - Invasão de zona restrita
  - Loitering > 5 min

EMERGÊNCIA: Perigo iminente
  - Múltiplas pessoas invadindo
  - Queda detectada
  - Fogo/fumaça detectado
```

---

## 🔌 NATS Topics

### Subscribe
- `seguranca.event.*` - Todos eventos
- `seguranca.analysis.result` - Análise do Brain
- `seguranca.face.unknown` - Rosto desconhecido

### Publish
- `mordomo.alert.security` - Alerta ao Mordomo central

```javascript
{
  "alert_id": "sec_alert_123",
  "priority": "critical|alerta|normal|emergencia",
  "camera_id": "cam_1",
  "timestamp": 1732723200.123,
  "event_type": "intrusion|loitering|fall|unknown_person",
  "description": "Pessoa desconhecida na entrada às 02:15",
  "snapshot_url": "http://storage/snapshots/alert_123.jpg",
  "video_clip_url": "http://storage/clips/alert_123.mp4",
  "recommendations": [
    "Acender luzes externas",
    "Enviar notificação push",
    "Gravar vídeo contínuo"
  ]
}
```

---

## 🚀 Docker

```yaml
alert-manager:
  build: ./alert-manager
  environment:
    - NATS_URL=nats://mordomo-nats:4222
    - COOLDOWN_SECONDS=60
    - MAX_ALERTS_PER_HOUR=10
    - STORAGE_URL=http://mordomo-minio:9000
  volumes:
    - /mnt/ssd/recordings:/recordings
  deploy:
    resources:
      limits:
        cpus: '0.3'
        memory: 256M
```

---

## 🧪 Anti-Spam Logic

```javascript
const alertCooldowns = new Map();

function shouldSendAlert(camera_id, event_type) {
    const key = `${camera_id}_${event_type}`;
    const lastAlert = alertCooldowns.get(key);
    
    if (!lastAlert || Date.now() - lastAlert > COOLDOWN_MS) {
        alertCooldowns.set(key, Date.now());
        return true;
    }
    
    return false;
}
```

---

## 🔄 Changelog

### v1.0.0
- ✅ Priorização de alertas
- ✅ Cooldown anti-spam
- ✅ Snapshot/clip generation
- ✅ Integração Mordomo via NATS
