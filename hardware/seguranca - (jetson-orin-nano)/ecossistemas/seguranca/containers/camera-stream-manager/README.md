# 📹 Camera Stream Manager

**Container:** `camera-stream-manager`  
**Ecossistema:** Segurança  
**Hardware:** Jetson Orin Nano 8GB  
**Posição no Fluxo:** Gerenciamento de streams RTSP

---

## 📋 Propósito

Gerencia 4 streams RTSP simultâneos de câmeras IP, re-encoding com NVENC (hardware H.264), buffer circular de 24h e distribuição para containers de análise.

---

## 🎯 Responsabilidades

### Primárias
- ✅ Conectar a 4 câmeras IP via RTSP
- ✅ Re-encode H.264 com NVENC (hardware acceleration)
- ✅ Distribuir frames para YOLO e Brain
- ✅ Buffer circular 24h em SSD
- ✅ Snapshots sob demanda

### Secundárias
- ✅ Health check de câmeras
- ✅ Reconexão automática
- ✅ Ajuste dinâmico de bitrate
- ✅ Multiplexação de streams (4 câmeras → 1 grid)

---

## 🔧 Tecnologias

### Core
- **mediamtx** - RTSP server Go
- **FFmpeg** - NVENC encoding
- **GStreamer** - Pipeline otimizado NVIDIA
- **DeepStream** - Framework NVIDIA para múltiplas câmeras

---

## 📊 Especificações Técnicas

### Performance
```yaml
Cameras: 4x 1080p @ 30 FPS
Codec: H.264 (NVENC)
Bitrate: 2 Mbps por câmera
Total Bandwidth: 8 Mbps
Latency: < 100 ms
CPU Usage: 20% (encoding offloaded to GPU)
GPU Usage: 256 MB VRAM
```

### Storage
```yaml
Recording: 24h continuous
Bitrate: 2 Mbps per camera
Storage per camera: 21.6 GB/day
Total 4 cameras: 86.4 GB/day
SSD Required: 256 GB NVMe
```

---

## 🔌 Interfaces de Comunicação

### Input (Câmeras RTSP)
```yaml
Camera 1: rtsp://192.168.1.101:554/stream
Camera 2: rtsp://192.168.1.102:554/stream
Camera 3: rtsp://192.168.1.103:554/stream
Camera 4: rtsp://192.168.1.104:554/stream

Auth: admin:password (configurável)
```

### Output (NATS Publish)
```javascript
// Novo frame disponível
Topic: "seguranca.camera.frame"
Payload: {
  "camera_id": "cam_1",
  "timestamp": 1732723200.123,
  "frame_number": 12345,
  "resolution": "1920x1080",
  "fps": 30,
  "url": "http://stream-manager:8080/cam1/frame.jpg"
}

// Status da câmera
Topic: "seguranca.camera.status"
Payload: {
  "camera_id": "cam_1",
  "online": true,
  "fps": 30,
  "bitrate_kbps": 2048,
  "dropped_frames": 5,
  "uptime_seconds": 86400
}
```

---

## 🚀 Docker Compose

```yaml
camera-stream-manager:
  image: bluenviron/mediamtx:latest
  container_name: camera-stream-manager
  restart: unless-stopped
  
  runtime: nvidia
  
  environment:
    - MTX_PROTOCOLS=tcp
    - MTX_RTSPADDRESS=:8554
    - MTX_HLSADDRESS=:8888
    - MTX_WEBRTCADDRESS=:8889
  
  ports:
    - "8554:8554"  # RTSP
    - "8888:8888"  # HLS
    - "8889:8889"  # WebRTC
  
  volumes:
    - ./mediamtx.yml:/mediamtx.yml
    - /mnt/ssd/recordings:/recordings
  
  networks:
    - seguranca-net
    - shared-nats
  
  deploy:
    resources:
      limits:
        memory: 1.5G
      reservations:
        devices:
          - driver: nvidia
            capabilities: [video]
```

---

## 📚 Referências

- [mediamtx](https://github.com/bluenviron/mediamtx)
- [NVIDIA NVENC](https://developer.nvidia.com/nvidia-video-codec-sdk)

---

## 🔄 Changelog

### v1.0.0 (2024-11-27)
- ✅ mediamtx para 4 câmeras RTSP
- ✅ NVENC hardware encoding
- ✅ Buffer circular 24h
