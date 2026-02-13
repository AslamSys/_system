# 📸 Photo Backup & Gallery

**Container:** `photo-backup`  
**Stack:** PhotoPrism + pyicloud  
**Propósito:** Backup automático iPhone + galeria AI

---

## 📋 Propósito

Sincronizar fotos do iCloud, indexar com AI (faces, tags, localização), galeria web responsiva.

---

## 🎯 Features

- ✅ Sync automático iCloud Photos (pyicloud)
- ✅ AI tagging (objetos, cenas, cores)
- ✅ Reconhecimento facial (agrupamento)
- ✅ Geolocalização (mapas)
- ✅ Busca por data, local, pessoa, tag
- ✅ Albums inteligentes

---

## 🔌 NATS Topics

### Publish
```javascript
Topic: "nas.photo.backed_up"
Payload: {
  "filename": "IMG_1234.HEIC",
  "size_mb": 3.2,
  "date": "2025-11-27T14:30:00Z",
  "location": {
    "latitude": -23.550520,
    "longitude": -46.633308,
    "city": "São Paulo"
  },
  "faces": ["Renan", "Maria"],
  "tags": ["praia", "sunset", "família"],
  "camera": "iPhone 15 Pro"
}
```

---

## 🚀 Docker Compose

```yaml
photo-backup:
  image: photoprism/photoprism:latest
  ports:
    - "2342:2342"
  environment:
    - PHOTOPRISM_ADMIN_PASSWORD=${ADMIN_PASSWORD}
    - PHOTOPRISM_ORIGINALS_PATH=/photos
    - PHOTOPRISM_IMPORT_PATH=/import
    - PHOTOPRISM_DATABASE_DRIVER=mysql
    - PHOTOPRISM_DATABASE_SERVER=mariadb:3306
  volumes:
    - /hot-storage/photos:/photos
    - /cold-storage/archive/photos:/archive:ro
    - ./import:/import
  deploy:
    resources:
      limits:
        cpus: '0.8'
        memory: 1536M

icloud-sync:
  build: ./icloud-sync
  environment:
    - APPLE_ID=${APPLE_ID}
    - APPLE_PASSWORD=${APPLE_PASSWORD}
    - DOWNLOAD_PATH=/import
    - SYNC_INTERVAL=300  # 5 min
  volumes:
    - ./import:/import
  deploy:
    resources:
      limits:
        cpus: '0.4'
        memory: 512M
```

---

## 🧪 Código (iCloud Sync)

```python
from pyicloud import PyiCloudService
import os, time

api = PyiCloudService(os.getenv('APPLE_ID'), os.getenv('APPLE_PASSWORD'))

# 2FA code (primeira vez)
if api.requires_2fa:
    code = input("Enter 2FA code: ")
    api.validate_2fa_code(code)

while True:
    photos = api.photos.all
    
    for photo in photos:
        # Check if already downloaded
        if not os.path.exists(f"/import/{photo.filename}"):
            download = photo.download()
            
            with open(f"/import/{photo.filename}", 'wb') as f:
                f.write(download.raw.read())
            
            # Publish to NATS
            await nc.publish('nas.photo.backed_up', json.dumps({
                'filename': photo.filename,
                'size_mb': photo.size / 1024 / 1024,
                'date': photo.created.isoformat(),
                'camera': photo.asset_type
            }).encode())
    
    time.sleep(300)  # 5 minutes
```

---

## 📱 Acesso Mobile

```yaml
PhotoPrism App:
  - iOS/Android app oficial
  - URL: https://nas.local:2342
  - Progressive Web App (PWA)

Features:
  - Upload de fotos do celular
  - Download de originais
  - Compartilhamento de álbuns
  - Favoritos e archive
```

---

## 🔄 Changelog

### v1.0.0
- ✅ PhotoPrism latest
- ✅ pyicloud sync
- ✅ AI tagging
- ✅ Face recognition
