# 📹 Video Recorder

**Container:** `video-recorder`  
**Ecossistema:** Segurança  
**Hardware:** Jetson Orin Nano  
**Tecnologias:** FFmpeg + NVENC + Minio

---

## 📋 Propósito

Gravação contínua 24/7 com buffer circular, snapshots sob demanda, clips de eventos e armazenamento otimizado com NVENC hardware encoding.

---

## 🎯 Responsabilidades

- ✅ Gravação contínua 24/7 (4 câmeras)
- ✅ Buffer circular (sobrescreve após 7 dias)
- ✅ Snapshots em alta resolução
- ✅ Clips de eventos (10s antes + 30s depois)
- ✅ Upload para Minio (object storage)

---

## 📊 Storage

```yaml
Resolution: 1080p @ 30 FPS
Codec: H.264 (NVENC)
Bitrate: 2 Mbps per camera
Storage per camera: 21.6 GB/day
Total 4 cameras: 86.4 GB/day
Retention: 7 days = 605 GB
SSD: 1 TB NVMe recommended
```

---

## 🔌 NATS Topics

### Subscribe
- `seguranca.camera.frame` - Frames para snapshots
- `seguranca.event.*` - Eventos para clips
- `seguranca.record.snapshot` - Request snapshot manual

### Publish
- `seguranca.record.snapshot.ready` - Snapshot salvo
- `seguranca.record.clip.ready` - Clip de evento pronto

---

## 🚀 Docker

```yaml
video-recorder:
  image: jrottenberg/ffmpeg:nvidia
  runtime: nvidia
  environment:
    - NVENC_PRESET=p4  # Balanced quality/speed
    - BITRATE=2M
    - GOP_SIZE=60  # 2 seconds @ 30 FPS
    - MINIO_ENDPOINT=mordomo-minio:9000
    - RETENTION_DAYS=7
  volumes:
    - /mnt/ssd/recordings:/recordings
    - /mnt/ssd/snapshots:/snapshots
  devices:
    - /dev/nvidia0:/dev/nvidia0
  deploy:
    resources:
      limits:
        memory: 1G
      reservations:
        devices:
          - driver: nvidia
            capabilities: [video]
```

---

## 🎬 FFmpeg Command

```bash
# Continuous recording with NVENC
ffmpeg -rtsp_transport tcp \
  -i rtsp://192.168.1.101:554/stream \
  -c:v h264_nvenc \
  -preset p4 \
  -b:v 2M \
  -g 60 \
  -f segment \
  -segment_time 3600 \
  -segment_format mp4 \
  -segment_wrap 168 \
  -reset_timestamps 1 \
  -strftime 1 \
  "/recordings/cam1_%Y%m%d_%H%M%S.mp4"
```

---

## 📸 Snapshot Generation

```python
import cv2
import boto3
from datetime import datetime

async def capture_snapshot(camera_id, reason="manual"):
    # Capture frame
    frame = await get_latest_frame(camera_id)
    
    # Save high-quality JPEG
    filename = f"{camera_id}_{datetime.now().isoformat()}.jpg"
    cv2.imwrite(f"/snapshots/{filename}", frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
    
    # Upload to Minio
    s3 = boto3.client('s3', endpoint_url='http://mordomo-minio:9000')
    s3.upload_file(f"/snapshots/{filename}", 'snapshots', filename)
    
    # Publish
    await nc.publish("seguranca.record.snapshot.ready", json.dumps({
        "camera_id": camera_id,
        "url": f"http://minio/snapshots/{filename}",
        "timestamp": time.time(),
        "reason": reason
    }))
```

---

## 🎥 Event Clip Generation

```python
async def generate_clip(camera_id, event_timestamp, duration=40):
    # 10s before + 30s after event
    start_time = event_timestamp - 10
    end_time = event_timestamp + 30
    
    # Find recording segments
    segments = find_segments(camera_id, start_time, end_time)
    
    # Concatenate and extract clip
    clip_file = f"/clips/event_{camera_id}_{event_timestamp}.mp4"
    
    ffmpeg_concat(segments, clip_file, start_time, duration)
    
    # Upload to Minio
    s3.upload_file(clip_file, 'clips', os.path.basename(clip_file))
    
    return f"http://minio/clips/{os.path.basename(clip_file)}"
```

---

## 🗑️ Cleanup Policy

```bash
#!/bin/bash
# Cron job: 0 2 * * * (02:00 daily)

# Delete recordings older than 7 days
find /recordings -name "*.mp4" -mtime +7 -delete

# Delete snapshots older than 30 days
find /snapshots -name "*.jpg" -mtime +30 -delete

# Delete event clips older than 90 days
find /clips -name "*.mp4" -mtime +90 -delete
```

---

## 📊 Monitoring

```yaml
Metrics:
  - recording_disk_usage_gb
  - recording_oldest_file_age_hours
  - snapshots_generated_total
  - clips_generated_total
  - minio_upload_failures_total
```

---

## 🔄 Changelog

### v1.0.0
- ✅ 24/7 recording com NVENC
- ✅ Buffer circular 7 dias
- ✅ Snapshots sob demanda
- ✅ Event clips automáticos
- ✅ Minio object storage
