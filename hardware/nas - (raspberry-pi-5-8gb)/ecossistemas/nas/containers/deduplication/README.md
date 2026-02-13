# 🧹 Deduplication Engine

**Container:** `deduplication`  
**Stack:** rmlint + Btrfs  
**Propósito:** Detectar e remover duplicatas

---

## 📋 Propósito

Economizar espaço removendo arquivos duplicados. Hash SHA-256, preserva original, remove cópias.

---

## 🎯 Features

- ✅ Hash-based deduplication (SHA-256)
- ✅ Detecta duplicatas exatas
- ✅ Preserva arquivo mais antigo
- ✅ Cria hardlinks (economiza espaço)
- ✅ Scan agendado (semanal)

---

## 🚀 Docker Compose

```yaml
deduplication:
  build: ./deduplication
  environment:
    - SCAN_PATH=/storage
    - SCAN_CRON=0 3 * * 0  # Domingo 3h
  volumes:
    - /hot-storage:/storage/hot
    - /cold-storage:/storage/cold
  deploy:
    resources:
      limits:
        cpus: '0.5'
        memory: 768M
```

---

## 🧪 Código (rmlint)

```bash
#!/bin/bash
# Scan for duplicates
rmlint /storage/hot /storage/cold \
    --size 1M \
    --algorithm sha256 \
    --output=sh:dedup.sh \
    --output=json:dedup.json

# Review duplicates
cat dedup.json | jq '.[] | select(.type=="duplicate_file")'

# Execute (remove duplicates, create hardlinks)
./dedup.sh --dry-run  # Test first
./dedup.sh            # Execute

# Publish stats
curl -X POST http://mordomo-nats:4222/nas.dedup.completed \
  -d "{\"files_removed\": 150, \"space_saved_gb\": 8.5}"
```

---

## 📊 Stats

```yaml
Scan Results:
  - Total files: 50,000
  - Duplicates: 1,200 (2.4%)
  - Space saved: 8.5 GB
  - Time: ~25 minutes
```

---

## 🔄 Changelog

### v1.0.0
- ✅ rmlint integration
- ✅ SHA-256 hashing
- ✅ Weekly cron
