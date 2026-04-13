# 📱 Ecossistema IoT (Orange Pi 5 Ultra)

> 📍 **Navegação:** [🏠 Início](../../../../README.md) > [🔧 Hardware](../../../README.md) > [🎯 Mordomo](../../README.md) > [🌐 Ecossistemas](../README.md) > [📱 IoT](README.md)

Gerenciamento de dispositivos ESP32 DIY via Wi-Fi Access Point e Bluetooth BLE, rodando diretamente no Orange Pi 5 Ultra. Sem LLM — execução direta de comandos já interpretados pelo Mordomo.

---

## 🏗️ Princípios de Arquitetura

**1. O Mordomo nunca fala MQTT**
O Brain conhece apenas NATS. MQTT é um detalhe interno do ecossistema IoT — invisível para o resto do sistema. Isso garante que o IoT pode ser movido para hardware separado futuramente sem tocar no código do Mordomo.

**2. NATS para comandos e eventos, Redis para leitura de estado**
- Comandos e eventos de presença: sempre via NATS (assíncrono, desacoplado)
- Query de estado ("a luz está acesa?"): leitura direta no Redis pelo Brain (< 5ms, sem round-trip)

**3. O `iot-orchestrator` é só um tradutor**
Recebe mensagem NATS → publica MQTT. Sem lógica de negócio. A inteligência fica no Brain.

---

## 🌐 Arquitetura de Rede

```
Internet/Rede doméstica
        │
     eth0 (Gigabit Ethernet)  ← Orange Pi conectado aqui
        │
   [Orange Pi 5 Ultra]
        │
     wlan0/ap0 (Wi-Fi 6 como Access Point)
        │
   ┌────┴────┐
  ESP32    ESP32   ...  (rede 10.0.0.x)
```

O Wi-Fi 6 do Orange Pi 5 Ultra opera em **modo Access Point dedicado** (hostapd + interface virtual `ap0`). A `eth0` fica exclusivamente para a rede doméstica/internet — sem conflito.

---

## 📦 Containers (4 total)

| Container | Função | Status | Repositório |
|-----------|--------|--------|-------------|
| **iot-orchestrator** | Tradução NATS → MQTT para ESP32 | 📋 | [AslamSys/iot-orchestrator](https://github.com/AslamSys/iot-orchestrator) |
| **mqtt-broker** | Broker MQTT local (Mosquitto) — retém último estado | 📋 | [AslamSys/iot-mqtt-broker](https://github.com/AslamSys/iot-mqtt-broker) |
| **iot-state-cache** | Redis — espelho de estados, leitura direta pelo Brain | 📋 | [AslamSys/iot-state-cache](https://github.com/AslamSys/iot-state-cache) |
| **bluetooth-scanner** | Presence detection via BLE → publica NATS | 📋 | *Repositório aguardando criação* |

---

## ⚡ Fluxos de Comunicação

### 1. Comando de controle (Mordomo → ESP32)

```
Usuário: "Acende a luz da sala"
    │
    ▼
Mordomo Brain (LLM interpreta + identifica dispositivo)
    │
    │  NATS publish — topic: iot.device.control
    │  payload: {device_id, action, params}
    ▼
iot-orchestrator  (mesmo host, ~0.3ms via loopback)
    │
    │  MQTT publish — topic: luz/sala/set
    │  payload: {"state": "ON", "brightness": 80}
    ▼
mqtt-broker (Mosquitto) → wlan0 AP → ESP32 (10.0.0.x)
    │
    │  MQTT publish ← confirmação do ESP32
    │  topic: luz/sala/state {"state": "ON"}
    ▼
iot-orchestrator atualiza Redis
    key: device:luz_sala:state → "ON"  TTL: 5min

Latência total: < 150ms
```

### 2. Leitura de estado (Mordomo consulta dispositivo)

```
Usuário: "A luz da sala está acesa?"
    │
    ▼
Mordomo Brain
    │
    │  Leitura direta no Redis (sem NATS)
    │  GET device:luz_sala:state → "ON"
    ▼
Resposta em < 5ms — sem round-trip para o IoT
```

### 3. Presença detectada (ESP32/BLE → Mordomo)

```
bluetooth-scanner detecta smartphone/Mi Band
    │
    │  NATS publish — topic: iot.presence.detected
    │  payload: {device_mac, rssi, location: "sala"}
    ▼
Mordomo Brain (assina iot.presence.*)
    │
    ▼
Automação: "João chegou em casa" → acende luzes, ajusta temperatura
```

---

## 📊 Responsabilidades por Container

| Container | Entrada | Saída | Armazena |
|---|---|---|---|
| **iot-orchestrator** | NATS `iot.device.control` | MQTT `<device>/set` | — |
| **mqtt-broker** | MQTT de ESP32 e orchestrator | MQTT retain | Último estado (retain) |
| **iot-state-cache** | Writes do orchestrator | Leitura pelo Brain (Redis GET) | Estado atual de cada dispositivo |
| **bluetooth-scanner** | BLE scan (host bluetooth) | NATS `iot.presence.*` | — |

---

## 📊 Análise de Recursos

| Container | RAM | CPU |
|-----------|-----|-----|
| iot-orchestrator | 180MB | 25% |
| mqtt-broker | 100MB | 15% |
| iot-state-cache (Redis) | 80MB | 10% |
| bluetooth-scanner | 100MB | 20% |
| **TOTAL** | **460MB** | **~70% (0.7 core)** |

_Impacto marginal — RAM total dos 4 ecossistemas fica em ~12GB dos 16GB disponíveis._

---

## 🛠️ Configuração do Access Point

O Access Point **não roda em container** — é configurado no host do Orange Pi via `hostapd` + `dnsmasq`:

```yaml
# /etc/hostapd/hostapd.conf
interface=ap0
ssid=IoT_Network
hw_mode=g
channel=6
wpa=2
wpa_passphrase=<senha_segura>

# /etc/dnsmasq.conf
interface=ap0
dhcp-range=10.0.0.10,10.0.0.254,12h
# IPs fixos por MAC para cada ESP32
dhcp-host=AA:BB:CC:DD:EE:FF,luz-sala,10.0.0.10
```

---

## 🔧 Tecnologias

- **MQTT Broker**: Eclipse Mosquitto
- **Cache/Estado**: Redis (< 5ms leitura direta pelo Brain)
- **BLE**: BlueZ + Python (scanning contínuo)
- **Wi-Fi AP**: hostapd (rede dedicada 10.0.0.x)
- **Dispositivos**: ESP32 DIY (~$3 cada)


> 📍 **Navegação:** [🏠 Início](../../../../README.md) > [🔧 Hardware](../../../README.md) > [🎯 Mordomo](../../README.md) > [🌐 Ecossistemas](../README.md) > [📱 IoT](README.md)

Gerenciamento de dispositivos ESP32 DIY via Wi-Fi Access Point e Bluetooth BLE, rodando diretamente no Orange Pi 5 Ultra. Sem LLM — execução direta de comandos já interpretados pelo Mordomo.

---

## 🌐 Arquitetura de Rede

```
Internet/Rede doméstica
        │
     eth0 (Gigabit Ethernet)  ← Orange Pi conectado aqui
        │
   [Orange Pi 5 Ultra]
        │
     wlan0/ap0 (Wi-Fi 6 como Access Point)
        │
   ┌────┴────┐
  ESP32    ESP32   ...  (rede 10.0.0.x)
```

O Wi-Fi 6 do Orange Pi 5 Ultra opera em **modo Access Point dedicado** (hostapd + interface virtual `ap0`). A `eth0` fica exclusivamente para a rede doméstica/internet — sem conflito.

---

## 📦 Containers (4 total)

| Container | Função | Status | Repositório |
|-----------|--------|--------|-------------|
| **iot-orchestrator** | Tradução NATS → MQTT para ESP32 | 📋 | [AslamSys/iot-orchestrator](https://github.com/AslamSys/iot-orchestrator) |
| **mqtt-broker** | Broker MQTT local (Mosquitto) | 📋 | [AslamSys/iot-mqtt-broker](https://github.com/AslamSys/iot-mqtt-broker) |
| **iot-state-cache** | Cache Redis para estados IoT | 📋 | [AslamSys/iot-state-cache](https://github.com/AslamSys/iot-state-cache) |
| **bluetooth-scanner** | Presence detection via BLE | 📋 | *Repositório aguardando criação* |

---

## ⚡ Fluxo de Comando

```
Usuário: "Acende a luz da sala"
    ↓
Mordomo Brain: LLM interpreta + identifica dispositivo
    ↓
NATS publish → iot.device.control
  {"device_id": "luz_sala_esp32", "action": "turn_on", "brightness": 80}
    ↓
iot-orchestrator: Recebe NATS → Traduz para MQTT
    ↓
MQTT publish → luz/sala/set {"state": "ON", "brightness": 80}
    ↓
ESP32 (10.0.0.10 via wlan0 AP): Recebe e executa < 50ms
    ↓
MQTT publish → luz/sala/state {"state": "ON"}  ← Confirmação
    ↓
Latência total: < 150ms
```

---

## 📊 Análise de Recursos

| Container | RAM | CPU |
|-----------|-----|-----|
| iot-orchestrator | 180MB | 25% |
| mqtt-broker | 100MB | 15% |
| iot-state-cache (Redis) | 80MB | 10% |
| bluetooth-scanner | 100MB | 20% |
| **TOTAL** | **460MB** | **~70% (0.7 core)** |

_Impacto marginal no Orange Pi — a RAM total do hardware usado pelos 4 ecossistemas fica em ~12GB dos 16GB disponíveis._

---

## 🛠️ Configuração do Access Point

O Access Point **não roda em container** — é configurado no host do Orange Pi via `hostapd` + `dnsmasq`:

```yaml
# /etc/hostapd/hostapd.conf
interface=ap0
ssid=IoT_Network
hw_mode=g
channel=6
wpa=2
wpa_passphrase=<senha_segura>

# /etc/dnsmasq.conf
interface=ap0
dhcp-range=10.0.0.10,10.0.0.254,12h
# IPs fixos por MAC para cada ESP32
dhcp-host=AA:BB:CC:DD:EE:FF,luz-sala,10.0.0.10
```

---

## 🔧 Tecnologias

- **MQTT Broker**: Eclipse Mosquitto
- **Cache**: Redis (< 5ms latência)
- **BLE**: BlueZ + Python (scanning contínuo)
- **Wi-Fi AP**: hostapd (rede dedicada 10.0.0.x)
- **Dispositivos**: ESP32 DIY (~$3 cada)

---

## 📁 Containers (documentação detalhada)

- [iot-orchestrator](./containers/iot-orchestrator/)
- [mqtt-broker](./containers/mqtt-broker/)
- [iot-state-cache](./containers/iot-state-cache/)
