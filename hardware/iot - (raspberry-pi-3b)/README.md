# Raspberry Pi 3B+ - Módulo IoT (ESP32 DIY + Access Point)

> 🗂️ **Navegação:** [🏠 Início](../../README.md) > [🔧 Hardware](../README.md) > [🌐 IoT (RPi 3B+)](README.md)

## 📋 Especificações do Hardware

### Raspberry Pi 3 Model B+
- **SoC**: Broadcom BCM2837B0 (Cortex-A53 quad-core 1.4GHz)
- **RAM**: 1GB LPDDR2
- **Rede**: Gigabit Ethernet (300Mbps via USB 2.0) + **Wi-Fi 5 (802.11ac) como Access Point** + Bluetooth 4.2
- **USB**: 4x USB 2.0
- **GPIO**: 40 pinos
- **Alimentação**: 5V/2.5A via Micro USB (12.5W)
- **Preço**: **$35** (board only)

### Periféricos Necessários
- **MicroSD 32GB**: $8
- **Fonte Micro USB 5V/2.5A**: $10
- **Case básico com ventilação**: $5
- **Antena Wi-Fi externa 5dBi**: $12 (alcance 50-100m)
- **Antena Bluetooth externa 3dBi** (opcional): $10
- **Cabo Ethernet Cat6**: $3
- **TOTAL**: **$83** (sem BT) / **$93** (com BT)

## 🎯 Função no Sistema

Este hardware executa o **Módulo IoT (Internet of Things)**, responsável por:
- **Wi-Fi Access Point**: Rede dedicada para dispositivos ESP32 DIY (10.0.0.x)
- **MQTT Broker**: Comunicação com ESP32 (lâmpadas, sensores, tomadas custom)
- **Bluetooth Gateway**: Presence detection (smartphones, Mi Band, tags)
- **Cache Redis**: Estados em tempo real (< 5ms latência)
- **SEM LLM**: Execução direta de comandos do Mordomo (baixa latência crítica)
- **Resposta instantânea**: "acender luz da sala" → < 150ms (NATS + MQTT + ESP32)

## ⚡ Por que ESP32 DIY ao invés de dispositivos prontos?

### Justificativa Técnica
1. **Custo**: ESP32 ~$3 vs Lâmpada Zigbee ~$15 (5x mais barato)
2. **Controle Total**: Você programa funcionalidades customizadas
3. **Sem Vendor Lock-in**: Não depende de fabricantes (Philips, Xiaomi)
4. **Wi-Fi Nativo**: ESP32 conecta direto no Access Point (sem dongles extras)
5. **Escalável**: Mesh Wi-Fi para grandes distâncias (ESP-MESH)

### Por que SEM LLM no IoT?
1. **Latência Crítica**: Acender luz < 150ms, LLM levaria 300-500ms
2. **Comandos Determinísticos**: "Liga luz X" já foi interpretado pelo Mordomo
3. **Recursos Limitados**: 1GB RAM para Access Point + MQTT + Redis
4. **Confiabilidade**: Execução direta sem inferência probabilística

### Fluxo de Decisão
```
Usuário: "Acende a luz da sala"
    ↓
Mordomo Brain (Orange Pi): LLM interpreta intenção + identifica dispositivo
    ↓
NATS publish → iot.device.control {"device_id": "luz_sala_esp32", "action": "turn_on", "brightness": 80}
    ↓
iot-orchestrator (RPi): Recebe NATS → Traduz para MQTT
    ↓
MQTT publish → luz/sala/set {"state": "ON", "brightness": 80}
    ↓
ESP32 (Wi-Fi 10.0.0.10): Recebe via Access Point do RPi
    ↓
digitalWrite(LED_PIN, HIGH); // < 50ms
    ↓
MQTT publish → luz/sala/state {"state": "ON"} // Confirmação
    ↓
Luz acende em < 150ms total
```

**Resultado**: Mordomo = cérebro (LLM), IoT = braço executor (MQTT + ESP32).

## 📦 Ecossistema: IoT

### Containers (4 total)

#### 1. **iot-orchestrator**
- Recebe comandos estruturados via NATS (do Mordomo Brain)
- Traduz para MQTT e publica para ESP32 devices
- Sem interpretação (Mordomo já fez isso)
- Latência < 10ms (NATS → MQTT)
- **Recursos**: 180MB RAM, 25% CPU

#### 2. **mqtt-broker** (Eclipse Mosquitto)
- Broker MQTT local para ESP32 devices (Wi-Fi 10.0.0.x)
- Retain messages (último estado conhecido)
- ACLs por device (segurança)
- Bridge NATS opcional (sincronização)
- **Recursos**: 100MB RAM, 15% CPU

#### 3. **iot-state-cache** (Redis)
- Cache local de estados (latência < 5ms)
- 50-100 dispositivos ESP32 (lâmpadas, sensores, tomadas)
- TTL 5min (sincroniza com PostgreSQL do Mordomo)
- Pub/Sub para mudanças de estado
- **Recursos**: 80MB RAM, 10% CPU

#### 4. **bluetooth-scanner**
- Escaneamento BLE contínuo (presence detection)
- Rastreamento de smartphones, Mi Band, tags
- RSSI para proximidade (perto/longe)
- Automações: "chegou em casa" → acende luzes
- **Recursos**: 100MB RAM, 20% CPU

### Análise de Recursos

| Container | RAM | CPU | Disco |
|-----------|-----|-----|-------|
| iot-orchestrator | 180MB | 25% | 100MB |
| mqtt-broker | 100MB | 15% | 50MB |
| iot-state-cache | 80MB | 10% | 100MB |
| bluetooth-scanner | 100MB | 20% | 50MB |
| **TOTAL** | **460MB** | **70%** | **~300MB** |

### Viabilidade
- **RAM**: 460MB (containers) + 200MB (sistema + Docker + Access Point) = **660MB / 1GB** = **66% utilizado** ✅ (340MB livre)
- **CPU**: 70% / 400% = **18% utilizado** ✅ (3.3 cores livres)
- **Disco**: 300MB / 32GB = **1% utilizado** ✅

---

## 📦 Containers e Repositórios

Este hardware executa **4 containers** especializados em IoT:

### 🌐 Ecossistema IoT (4 containers)

| Container | Função | Status | Repositório |
|-----------|--------|--------|-------------|
| **iot-orchestrator** | Tradução NATS → MQTT para ESP32 | 📋 | [AslamSys/iot-orchestrator](https://github.com/AslamSys/iot-orchestrator) |
| **mqtt-broker** | Broker MQTT local (Mosquitto) | 📋 | [AslamSys/iot-mqtt-broker](https://github.com/AslamSys/iot-mqtt-broker) |
| **iot-state-cache** | Cache Redis para estados IoT | 📋 | [AslamSys/iot-state-cache](https://github.com/AslamSys/iot-state-cache) |
| **bluetooth-scanner** | Presence detection via BLE | 📋 | [AslamSys/iot-bluetooth-scanner](https://github.com/AslamSys/iot-bluetooth-scanner) |

**💡 Status:**
- ✅ **Implementado** - Container funcionando em produção  
- ⏳ **Em desenvolvimento** - Código em progresso ativo
- 📋 **Especificado** - Documentado, repositório criado, aguardando implementação

**📊 Fase atual:** Todos os containers estão em **fase de estudo/planejamento** (📋)

**🔧 Tecnologias:**
- **MQTT**: Eclipse Mosquitto (broker local)
- **Cache**: Redis (< 5ms latência)
- **BLE**: BlueZ + Python (scanning contínuo)
- **Wi-Fi AP**: hostapd (rede dedicada 10.0.0.x)

### Por que REMOVEMOS Zigbee2MQTT:
- ❌ **Custo**: Dongle USB Zigbee ~$25 (economizado)
- ❌ **Dependência**: Dispositivos prontos caros ($15-20 cada)
- ❌ **Complexidade**: Pareamento, firmware updates, compatibilidade
- ✅ **Alternativa**: ESP32 DIY ($3 cada) + controle total + Wi-Fi nativo

### Arquitetura Access Point:
### Arquitetura Access Point:
```
┌─────────────────────────────────────────────────┐
│      Raspberry Pi 3B+ (Módulo IoT)              │
├─────────────────────────────────────────────────┤
│ 1. Wi-Fi Access Point (hostapd)                 │
│    ├─ SSID: "IoT_Network"                       │
│    ├─ Canal: 6 (2.4GHz)                         │
│    ├─ Range: 50-100m (antena externa 5dBi)      │
│    └─ Subnet: 10.0.0.0/24                       │
│                                                  │
│ 2. DHCP Server (dnsmasq)                        │
│    ├─ Range: 10.0.0.10-254                      │
│    └─ IPs fixos por MAC (ESP32 devices)         │
│                                                  │
│ 3. Bluetooth 4.2 (bluez)                        │
│    └─ Range: 10-30m (antena externa 3dBi)       │
│                                                  │
│ 4. Containers Docker                            │
│    ├─ mqtt-broker (porta 1883)                  │
│    ├─ iot-orchestrator                          │
│    ├─ iot-state-cache (Redis)                   │
│    └─ bluetooth-scanner                         │
└─────────────────────────────────────────────────┘
         │                            │
         │ Wi-Fi AP                   │ Bluetooth
         ↓                            ↓
    ┌─────────────┐            ┌──────────────┐
    │ ESP32 Luz   │            │ Smartphone   │
    │ 10.0.0.10   │            │ (Presence)   │
    │ MQTT Client │            │ BLE Beacon   │
    └─────────────┘            └──────────────┘
```

### Vantagens Access Point Próprio:
- ✅ **Centralizado**: Tudo em 1 hardware (gateway + AP + BT)
- ✅ **Economia**: Sem roteador extra (~$30-50 economizados)
- ✅ **Controle Total**: SSID, canal, potência, ACL
- ✅ **Segurança**: Rede isolada (não expõe Internet)
- ✅ **Latência MENOR**: ESP32 → RPi direto (< 50ms, sem hop pelo roteador)
- ✅ **Escalável**: Mesh Wi-Fi com ESP-MESH para > 100m

## 🌐 Padronização W3C Web of Things (WoT)

Para evitar alucinações do LLM (ex: enviar brilho 255 para um dispositivo que só aceita 0-100), adotamos o padrão **W3C Web Thing Description**.

Isso permite que o dispositivo anuncie não apenas "o que faz", mas "como faz" (tipos de dados, limites min/max, unidades).

### Exemplo de Schema (JSON-LD)
O `iot-orchestrator` normaliza todos os dispositivos para este formato antes de enviar ao Mordomo Brain. O padrão W3C é genérico e cobre qualquer tipo de dispositivo (sensores, câmeras, fechaduras, termostatos, etc).

#### Exemplo 1: Lâmpada Inteligente
```json
{
  "@context": "https://webthings.io/schemas",
  "@type": ["Light", "OnOffSwitch"],
  "id": "urn:dev:ops:32473-LuzSala-1",
  "title": "Luz da Sala",
  "description": "Luz principal da sala de estar",
  "properties": {
    "on": {
      "@type": "OnOffProperty",
      "title": "On/Off",
      "type": "boolean",
      "description": "Estado de energia"
    },
    "brightness": {
      "@type": "BrightnessProperty",
      "title": "Brilho",
      "type": "integer",
      "minimum": 0,
      "maximum": 100,
      "unit": "percent"
    }
  }
}
```

#### Exemplo 2: Termostato (Ar Condicionado)
```json
{
  "@context": "https://webthings.io/schemas",
  "@type": ["Thermostat"],
  "id": "urn:dev:ops:AC-Quarto",
  "title": "Ar Condicionado Quarto",
  "properties": {
    "temperature": {
      "@type": "TemperatureProperty",
      "title": "Temperatura Atual",
      "type": "number",
      "unit": "degree celsius",
      "readOnly": true
    },
    "targetTemperature": {
      "@type": "TargetTemperatureProperty",
      "title": "Temperatura Alvo",
      "type": "number",
      "minimum": 16,
      "maximum": 30,
      "unit": "degree celsius"
    },
    "mode": {
      "@type": "ThermostatModeProperty",
      "title": "Modo",
      "type": "string",
      "enum": ["off", "cool", "heat", "fan_only"]
    }
  }
}
```

#### Exemplo 3: Fechadura Inteligente
```json
{
  "@context": "https://webthings.io/schemas",
  "@type": ["Lock"],
  "id": "urn:dev:ops:Fechadura-Porta",
  "title": "Porta Principal",
  "properties": {
    "locked": {
      "@type": "LockedProperty",
      "title": "Trancada",
      "type": "string",
      "enum": ["locked", "unlocked", "jammed"]
    }
  },
  "actions": {
    "unlock": {
      "@type": "UnlockAction",
      "title": "Destrancar",
      "description": "Destrancar a porta remotamente"
    }
  }
}
```

---

## 🔌 Integração com Mordomo

### Protocolo NATS

#### Tópicos Subscritos (IoT escuta)
```
iot.device.control           # Comando genérico
  Payload: {
    "device_id": "luz_sala",
    "action": "turn_on|turn_off|set_brightness|set_color",
    "params": {"brightness": 80, "color": {"r": 255, "g": 200, "b": 150}}
  }

iot.scene.activate           # Ativar cena (múltiplas ações)
  Payload: {
    "scene": "all_lights_off",
    "devices": [{"device_id": "luz_sala", "action": "turn_off"}, ...]
  }

iot.query.state              # Consultar estado de dispositivo
  Payload: {"device_id": "sensor_temperatura_quarto"}
```

#### Tópicos Publicados (IoT notifica)
```
iot.device.state_changed     # Dispositivo mudou de estado
  Payload: {
    "device_id": "luz_sala",
    "state": {"power": "ON", "brightness": 80},
    "timestamp": "2025-11-27T20:15:33Z"
  }

iot.sensor.reading           # Leitura de sensor
  Payload: {
    "device_id": "sensor_temperatura",
    "type": "temperature|humidity|motion|door",
    "value": 23.5,
    "timestamp": "2025-11-27T20:15:33Z"
  }

iot.presence.detected        # BLE detectou presença
  Payload: {
    "device": "smartphone_renan",
    "state": "home|away",
    "rssi": -45
  }

iot.status                   # Heartbeat do módulo
  Payload: {"status": "online", "devices_count": 42}
```

### Fluxo de Comando (Exemplo)

```
Usuário: "Apaga todas as luzes"
    ↓
Mordomo Brain (Orange Pi): 
  - Interpreta intenção via LLM
  - Identifica dispositivos: [luz_sala, luz_quarto, luz_cozinha]
  - Consulta PostgreSQL: device_registry (IDs, protocolos)
    ↓
Mordomo publish NATS → iot.scene.activate
  {
    "scene": "all_lights_off",
    "devices": [
      {"device_id": "luz_sala", "action": "turn_off"},
      {"device_id": "luz_quarto", "action": "turn_off"},
      {"device_id": "luz_cozinha", "action": "turn_off"}
    ]
  }
    ↓
iot-orchestrator (RPi 4): Recebe via NATS (< 10ms)
  - Verifica cache Redis: estados atuais
  - Executa comandos em paralelo
    ↓
Para cada dispositivo:
  MQTT publish → zigbee2mqtt/luz_X/set {"state": "OFF"}
    ↓
Lâmpadas Zigbee executam (< 80ms cada)
    ↓
zigbee2mqtt publica confirmação via MQTT
    ↓
iot-orchestrator:
  - Atualiza Redis local (< 1ms)
  - Publica NATS → iot.device.state_changed (cada luz)
    ↓
Mordomo:
  - Atualiza PostgreSQL (background, assíncrono)
  - TTS: "Luzes apagadas!" (< 200ms total)
```

**Latência Total**: ~150ms (usuário fala → luz apaga)

## 🗄️ Dispositivos Suportados

### ESP32 DIY (Wi-Fi via Access Point)
- **Lâmpadas**: LED strips, relés, PWM dimmers
- **Tomadas**: ESP32 + Relé 5V/10A (controle 110V/220V)
- **Sensores**: DHT22 (temp/humidity), PIR (movimento), Reed switch (porta/janela)
- **Servos**: Portões, cortinas, persianas
- **IR Blaster**: Controle remoto universal (TVs, ACs)

**Stack ESP32**:
- Firmware: Arduino IDE / ESP-IDF / MicroPython
- Protocolo: MQTT (QoS 0/1)
- Biblioteca: PubSubClient (Arduino), umqtt (MicroPython)
- OTA: Update via Wi-Fi (sem USB)

### Bluetooth LE (via bluetooth-scanner)
- **Mi Band**: Detecção de presença, notificações
- **Tags**: Tiles, AirTags, BeaconX (proximidade)
- **Smartphones**: iOS/Android (BLE advertising)
- **Sensores**: Xiaomi Mi Temp/Humidity (BLE)

### MQTT Bridges (opcional)
- **Shelly**: Relés, dimmers (via Wi-Fi, MQTT nativo)
- **Tasmota**: ESP8266/ESP32 flasheado (MQTT)

## 🐳 Docker Compose

```yaml
version: '3.8'

services:
  iot-orchestrator:
    build: ./containers/iot-orchestrator
    container_name: iot-orchestrator
    environment:
      - NATS_URL=nats://mordomo-nats:4222
      - NATS_TOKEN_FILE=/run/secrets/nats_token
      - MQTT_URL=mqtt://mqtt-broker:1883
      - REDIS_URL=redis://iot-state-cache:6379
    secrets:
      - nats_token
    depends_on:
      - mqtt-broker
      - iot-state-cache
    networks:
      - iot-net
      - shared-nats
    deploy:
      resources:
        limits:
          memory: 180M
          cpus: '0.25'
    restart: unless-stopped

  mqtt-broker:
    image: eclipse-mosquitto:2.0
    container_name: mqtt-broker
    ports:
      - "1883:1883"  # MQTT
      - "9001:9001"  # WebSocket
    volumes:
      - ./config/mosquitto.conf:/mosquitto/config/mosquitto.conf
      - ./data/mqtt:/mosquitto/data
    networks:
      - iot-net
    deploy:
      resources:
        limits:
          memory: 100M
          cpus: '0.15'
    restart: unless-stopped

  iot-state-cache:
    image: redis:7-alpine
    container_name: iot-state-cache
    volumes:
      - ./data/redis:/data
    command: redis-server --appendonly yes --maxmemory 64mb --maxmemory-policy allkeys-lru
    networks:
      - iot-net
    deploy:
      resources:
        limits:
          memory: 80M
          cpus: '0.1'
    restart: unless-stopped

  bluetooth-scanner:
    build: ./containers/bluetooth-scanner
    container_name: bluetooth-scanner
    network_mode: host  # Necessário para BLE
    privileged: true
    volumes:
      - /var/run/dbus:/var/run/dbus
    environment:
      - NATS_URL=nats://mordomo-nats:4222
      - NATS_TOKEN_FILE=/run/secrets/nats_token
    secrets:
      - nats_token
    deploy:
      resources:
        limits:
          memory: 100M
    restart: unless-stopped

networks:
  iot-net:
    driver: bridge
  shared-nats:
    external: true
    name: infraestrutura_nats-net

secrets:
  nats_token:
    file: ./secrets/nats_token.txt
```

## 🚀 Deploy e Configuração

### Pré-requisitos
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar pacotes para Access Point
sudo apt update
sudo apt install hostapd dnsmasq bluez

# Parar serviços temporariamente
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq
```

### Configurar Wi-Fi Access Point

#### 1. Interface estática (`/etc/dhcpcd.conf`):
```conf
interface wlan0
    static ip_address=10.0.0.1/24
    nohook wpa_supplicant
```

#### 2. DHCP Server (`/etc/dnsmasq.conf`):
> *Nota: Com o Auto-Discovery, a configuração de IPs fixos no `dnsmasq.conf` torna-se opcional, pois o orquestrador saberá o IP atual do dispositivo através da mensagem de descoberta.*

```conf
interface=wlan0
dhcp-range=10.0.0.10,10.0.0.254,255.255.255.0,24h
domain=iot.local

# IPs fixos por MAC (ESP32 devices)
dhcp-host=AA:BB:CC:DD:EE:01,10.0.0.10,luz_sala
dhcp-host=AA:BB:CC:DD:EE:02,10.0.0.11,luz_quarto
dhcp-host=AA:BB:CC:DD:EE:03,10.0.0.12,tomada_tv
```

#### 3. Access Point (`/etc/hostapd/hostapd.conf`):
```conf
interface=wlan0
driver=nl80211
ssid=IoT_Network
hw_mode=g
channel=6
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0

# Segurança WPA2
wpa=2
wpa_passphrase=SuaSenhaSegura123
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP

# Potência máxima (com antena externa)
country_code=BR
ieee80211d=1
ieee80211h=1
```

#### 4. Habilitar serviços:
```bash
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq
sudo reboot
```

### Código ESP32 (Exemplo: Lâmpada DIY)

```cpp
#include <WiFi.h>
#include <PubSubClient.h>

// Configuração Wi-Fi (Access Point do Raspberry Pi)
const char* ssid = "IoT_Network";
const char* password = "SuaSenhaSegura123";
const char* mqtt_server = "10.0.0.1";  // IP do RPi

// Configuração MQTT
WiFiClient espClient;
PubSubClient client(espClient);

// Pinos
#define LED_PIN 2
#define PWM_CHANNEL 0

// Estado
int brightness = 0;

void setup() {
  Serial.begin(115200);
  
  // Configurar LED com PWM
  ledcSetup(PWM_CHANNEL, 5000, 8);  // 5kHz, 8 bits (0-255)
  ledcAttachPin(LED_PIN, PWM_CHANNEL);
  
  // Conectar Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi conectado!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());  // Deve ser 10.0.0.x
  
  // Conectar MQTT
  client.setServer(mqtt_server, 1883);
  client.setCallback(onMqttMessage);
  reconnectMqtt();

  // 🔥 AUTO-DISCOVERY: Anunciar presença (W3C WoT Style)
  // Nota: Em produção, use ArduinoJson para criar este payload
  String discoveryPayload = "{";
  discoveryPayload += "\"@context\": \"https://webthings.io/schemas\",";
  discoveryPayload += "\"@type\": [\"Light\", \"OnOffSwitch\"],";
  discoveryPayload += "\"id\": \"urn:dev:esp32:luz_sala\",";
  discoveryPayload += "\"title\": \"Luz da Sala\",";
  discoveryPayload += "\"properties\": {";
  discoveryPayload += "  \"on\": {\"@type\": \"OnOffProperty\", \"type\": \"boolean\"},";
  discoveryPayload += "  \"brightness\": {\"@type\": \"BrightnessProperty\", \"type\": \"integer\", \"minimum\": 0, \"maximum\": 100}";
  discoveryPayload += "}";
  discoveryPayload += "}";

  client.publish("iot/discovery", discoveryPayload.c_str(), true); // retain=true
  Serial.println("Auto-discovery (WoT) enviado!");  // Subscribe
  client.subscribe("luz/sala/set");
}

void reconnectMqtt() {
  while (!client.connected()) {
    Serial.print("Conectando MQTT...");
    if (client.connect("luz_sala_esp32")) {
      Serial.println(" OK!");
      client.publish("luz/sala/status", "online");
    } else {
      Serial.print(" FALHOU, rc=");
      Serial.println(client.state());
      delay(5000);
    }
  }
}

void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  String msg = "";
  for (int i = 0; i < length; i++) {
    msg += (char)payload[i];
  }
  
  Serial.print("MQTT recebido [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(msg);
  
  // Parse JSON simples (ou use ArduinoJson)
  if (msg.indexOf("\"state\":\"ON\"") > 0) {
    // Extrai brightness (default 255 se não informado)
    int idx = msg.indexOf("\"brightness\":");
    if (idx > 0) {
      brightness = msg.substring(idx + 13).toInt();
    } else {
      brightness = 255;
    }
    ledcWrite(PWM_CHANNEL, brightness);
    Serial.printf("LED ON (brightness: %d)\n", brightness);
    
    // Confirma estado
    char state[50];
    sprintf(state, "{\"state\":\"ON\",\"brightness\":%d}", brightness);
    client.publish("luz/sala/state", state);
    
  } else if (msg.indexOf("\"state\":\"OFF\"") > 0) {
    ledcWrite(PWM_CHANNEL, 0);
    brightness = 0;
    Serial.println("LED OFF");
    client.publish("luz/sala/state", "{\"state\":\"OFF\",\"brightness\":0}");
  }
}

void loop() {
  if (!client.connected()) {
    reconnectMqtt();
  }
  client.loop();
}
```

### Esquemático Hardware (Lâmpada LED Strip):
```
ESP32-DevKit
├─ GPIO 2 → Transistor TIP122 (Base, resistor 1kΩ)
├─ GND → Emissor TIP122
└─ 5V → VCC

TIP122 (NPN Darlington)
├─ Coletor → LED Strip 12V (-)
└─ LED Strip (+) → Fonte 12V/2A
```

---

## 🔐 Segurança IoT

### Segmentação de Rede (Access Point Isolado)
- **SSID Dedicado**: "IoT_Network" separado da rede principal
- **Subnet Própria**: 10.0.0.0/24 (não roteia para Internet)
- **Firewall**: iptables bloqueia acesso externo
- **Sem bridge**: wlan0 NÃO faz bridge com eth0

### Credenciais
- **WPA2**: Access Point com senha forte
- **MQTT ACL**: Cada ESP32 com credenciais únicas (opcional)
- **HTTPS OTA**: Updates ESP32 via HTTPS (TLS)
- **Rotação de senhas**: Semestral

### Atualizações
- **OTA ESP32**: Update via Wi-Fi sem USB
- **Docker auto-update**: Watchtower para containers
- **Watchdog**: Auto-restart ESP32 se offline > 5min

### Firewall (iptables):
```bash
# Bloquear roteamento Wi-Fi → Internet
sudo iptables -A FORWARD -i wlan0 -o eth0 -j DROP

# Permitir apenas MQTT local
sudo iptables -A INPUT -i wlan0 -p tcp --dport 1883 -j ACCEPT
sudo iptables -A INPUT -i wlan0 -j DROP
```

## 💡 Casos de Uso

### 1. **Chegada em Casa** (via BLE presence detection)
- BLE detecta smartphone → Publica `iot.presence.detected` (state: home)
- Mordomo recebe → Aciona cena "chegada": luzes ON + desliga alarme

### 2. **Economia de Energia** (automação horário)
- Mordomo: 23:00 → Publica `iot.scene.activate` (scene: sleep_mode)
- IoT: Apaga luzes + desliga TVs

### 3. **Segurança** (sensor + ausência)
- Sensor movimento detecta → Publica `iot.sensor.reading` (type: motion)
- Mordomo verifica: presence = away → Aciona Segurança + câmeras

### 4. **Conforto** (comando de voz)
- "Boa noite" → Mordomo: cena completa (luzes OFF, cortinas, portas, termostato)
- IoT executa cada ação via MQTT/Zigbee

### 5. **Presença Simulada** (anti-furto)
- Mordomo detecta: ausência > 2 dias
- Ativa automação: luzes aleatórias (hora variável)
- IoT executa comandos programados

---

## 📝 Resumo da Auditoria

### ✅ **Mudanças Aprovadas:**
1. **Hardware**: Raspberry Pi 3B+ 1GB ($35) + Antenas externas ($22) = **$57**
2. **Arquitetura**: Wi-Fi Access Point próprio (sem roteador extra, economia $30-50)
3. **Dispositivos**: 100% ESP32 DIY (~$3 cada) vs Zigbee prontos ($15+ cada)
4. **Containers**: 4 containers (460MB RAM) - **removido Zigbee2MQTT**
5. **Recursos**: 660MB / 1GB (**66% uso**, 340MB livre) ✅
6. **Economia Total**: ~$70 (sem dongle Zigbee $25, sem roteador extra $30-50, RPi 3B+ vs 4)

### ❌ **Removido (justificativa):**
- **Zigbee2MQTT**: ESP32 DIY usa Wi-Fi nativo (não precisa dongle/coordenador)
- **Dongle USB Zigbee**: $25 economizados
- **Roteador separado**: Access Point no próprio RPi (economia $30-50)
- **Dispositivos prontos**: Muito caros vs DIY ($15 vs $3)

### 🎯 **Resultado:**
- Arquitetura **totalmente customizável**
- Latência < 150ms (NATS → MQTT → ESP32)
- Redis local para **cache de estados** (< 5ms)
- PostgreSQL do Mordomo para **registro permanente**
- **Escalável**: ESP-MESH para grandes distâncias (> 100m)
- **Seguro**: Rede isolada, sem acesso Internet, firewall iptables

### 💰 **Custo Final:**
- Raspberry Pi 3B+: $35
- Periféricos: $48 (SD, fonte, case, antenas, cabo)
- **Total hardware**: $83
- **ESP32 (10 unidades)**: $30
- **Componentes (relés, sensores)**: $50
- **TOTAL SISTEMA**: **$163** (vs ~$400 com dispositivos Zigbee prontos)
