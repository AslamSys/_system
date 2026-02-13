# 🔄 File Sync

**Container:** `file-sync`  
**Stack:** Syncthing  
**Propósito:** Sincronização multiplataforma

---

## 📋 Propósito

Sync bidirecional de pastas entre NAS, PC, laptop, mobile. Peer-to-peer, sem cloud.

---

## 🎯 Features

- ✅ Sync P2P (sem servidor central)
- ✅ Versionamento de arquivos (histórico)
- ✅ Detecção de conflitos
- ✅ Criptografia TLS
- ✅ Selective sync (pastas específicas)
- ✅ Ignore patterns (.stignore)

---

## 🚀 Docker Compose

```yaml
file-sync:
  image: syncthing/syncthing:latest
  ports:
    - "8384:8384"  # WebUI
    - "22000:22000/tcp"  # Sync protocol
    - "22000:22000/udp"
    - "21027:21027/udp"  # Discovery
  volumes:
    - /hot-storage:/sync
    - ./config:/config
  environment:
    - PUID=1000
    - PGID=1000
  deploy:
    resources:
      limits:
        cpus: '0.4'
        memory: 512M
```

---

## ⚙️ Folders

```yaml
Documents:
  Path: /sync/documents
  Devices: PC, Laptop, NAS
  Versioning: Simple (30 days)

Photos:
  Path: /sync/photos
  Devices: NAS only (receive-only)
  Versioning: Staggered (90 days)

Work:
  Path: /sync/work
  Devices: Laptop, NAS
  Ignore: *.tmp, .git/
```

---

## 🔄 Changelog

### v1.0.0
- ✅ Syncthing latest
- ✅ Multi-device sync
- ✅ File versioning
