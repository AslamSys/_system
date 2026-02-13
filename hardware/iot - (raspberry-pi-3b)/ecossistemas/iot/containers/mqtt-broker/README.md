# 🌐 MQTT Broker

**Container:** `mqtt-broker`  
**Stack:** Eclipse Mosquitto  
**Protocolo:** MQTT 3.1.1 + 5.0

---

## 📋 Propósito

Broker MQTT local para dispositivos IoT. Bridge para NATS, retain messages para estado persistente, ACLs por device.

---

## 🎯 Features

- ✅ MQTT 3.1.1 + 5.0
- ✅ WebSockets support (port 9001)
- ✅ TLS/SSL (optional)
- ✅ Retained messages (device state)
- ✅ Bridge to NATS
- ✅ ACL authentication

---

## 🚀 Docker

```yaml
mqtt-broker:
  image: eclipse-mosquitto:2.0
  ports:
    - "1883:1883"  # MQTT
    - "9001:9001"  # WebSockets
  volumes:
    - ./mosquitto.conf:/mosquitto/config/mosquitto.conf
    - ./data:/mosquitto/data
    - ./log:/mosquitto/log
  deploy:
    resources:
      limits:
        cpus: '0.3'
        memory: 192M
```

---

## ⚙️ mosquitto.conf

```
listener 1883
protocol mqtt

listener 9001
protocol websockets

persistence true
persistence_location /mosquitto/data/

allow_anonymous false
password_file /mosquitto/config/passwd

# Bridge to NATS (via plugin)
connection nats_bridge
address nats://mordomo-nats:4222
topic iot/# out 0
topic mordomo/iot/# in 0
```

---

## 🔄 Changelog

### v1.0.0
- ✅ Mosquitto 2.0
- ✅ MQTT + WebSockets
- ✅ Persistence
- ✅ ACL auth
