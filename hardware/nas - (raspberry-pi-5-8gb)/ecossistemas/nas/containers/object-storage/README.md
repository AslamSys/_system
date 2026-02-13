# 🗄️ Object Storage (MinIO)

**Container:** `object-storage`  
**Stack:** MinIO (S3-compatible)  
**Propósito:** API S3 para upload/download

---

## 📋 Propósito

Storage S3-compatible. APIs REST para apps, CLI (mc), integração com ferramentas que suportam S3.

---

## 🎯 Features

- ✅ S3-compatible API
- ✅ Buckets e policies
- ✅ Presigned URLs (compartilhamento temporário)
- ✅ Versioning de objetos
- ✅ Lifecycle policies (auto-delete antigos)

---

## 🚀 Docker Compose

```yaml
object-storage:
  image: minio/minio:latest
  command: server /data --console-address ":9001"
  ports:
    - "9000:9000"  # S3 API
    - "9001:9001"  # Web Console
  environment:
    - MINIO_ROOT_USER=minioadmin
    - MINIO_ROOT_PASSWORD=${MINIO_PASSWORD}
  volumes:
    - /cold-storage:/data
  deploy:
    resources:
      limits:
        cpus: '0.6'
        memory: 1024M
```

---

## 🧪 Código (Upload)

```python
from minio import Minio

client = Minio(
    "nas.local:9000",
    access_key="minioadmin",
    secret_key=os.getenv("MINIO_PASSWORD"),
    secure=False
)

# Upload file
client.fput_object(
    "photos",
    "2025/11/IMG_1234.HEIC",
    "/tmp/IMG_1234.HEIC"
)

# Generate presigned URL (7 days)
url = client.presigned_get_object("photos", "2025/11/IMG_1234.HEIC", expires=timedelta(days=7))
```

---

## 🔄 Changelog

### v1.0.0
- ✅ MinIO latest
- ✅ S3 API
- ✅ Presigned URLs
