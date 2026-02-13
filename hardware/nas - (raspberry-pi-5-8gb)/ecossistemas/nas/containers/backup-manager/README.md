# 💾 Backup Manager

**Container:** `backup-manager`  
**Stack:** Restic  
**Propósito:** Backup incremental com deduplicação

---

## 📋 Propósito

Backup incremental, criptografado, deduplic ado. Suporta local, S3, Backblaze B2.

---

## 🎯 Features

- ✅ Incremental backups (só mudanças)
- ✅ Deduplicação automática
- ✅ Criptografia AES-256
- ✅ Múltiplos backends (local, S3, B2)
- ✅ Restore granular (arquivos específicos)
- ✅ Snapshot management

---

## 🚀 Docker Compose

```yaml
backup-manager:
  build: ./backup-manager
  environment:
    - RESTIC_REPOSITORY=/backups
    - RESTIC_PASSWORD=${RESTIC_PASSWORD}
    - BACKUP_CRON=0 */6 * * *  # A cada 6h
    - RETENTION_DAYS=7
    - RETENTION_WEEKS=4
    - RETENTION_MONTHS=12
  volumes:
    - /hot-storage:/data/hot:ro
    - /cold-storage/backups:/backups
  deploy:
    resources:
      limits:
        cpus: '0.4'
        memory: 512M
```

---

## 🧪 Código (Backup)

```bash
#!/bin/bash
# Initialize repository (first time)
restic init --repo /backups

# Backup hot storage
restic backup /data/hot \
    --exclude='*.tmp' \
    --exclude='.DS_Store' \
    --tag daily

# Prune old backups (retention policy)
restic forget \
    --keep-daily 7 \
    --keep-weekly 4 \
    --keep-monthly 12 \
    --prune

# Check integrity
restic check

# List snapshots
restic snapshots

# Restore specific file
restic restore latest \
    --target /restore \
    --include /photos/2025/11/IMG_1234.HEIC
```

---

## 📊 Backup Stats

```yaml
Example Backup:
  - Original size: 50 GB
  - After deduplication: 28 GB (44% savings)
  - After compression: 19 GB (62% total savings)
  - Backup time: ~45 minutes (first), ~8 minutes (incremental)
```

---

## ☁️ Cloud Backup (Backblaze B2)

```bash
# Configure B2 backend
export RESTIC_REPOSITORY=b2:nas-backup-bucket
export B2_ACCOUNT_ID=${B2_ACCOUNT_ID}
export B2_ACCOUNT_KEY=${B2_ACCOUNT_KEY}

# Backup to cloud
restic backup /data/hot --tag cloud

# Cost: $6/TB/mês
# 50GB backup = $0.30/mês
```

---

## 🔄 Changelog

### v1.0.0
- ✅ Restic latest
- ✅ Incremental backups
- ✅ Retention policies
- ✅ B2 cloud support
