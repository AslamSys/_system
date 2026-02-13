# 📺 Sonarr (Series)

**Container:** `sonarr-series`  
**Stack:** Sonarr + qBittorrent  
**Propósito:** Download automático de séries

---

## 📋 Propósito

Gerenciador de downloads de séries. Monitora novos episódios, baixa automaticamente, organiza em /media/series.

---

## 🎯 Features

- ✅ Download automático de episódios novos
- ✅ Monitora calendário de lançamentos
- ✅ Integração com Jackett
- ✅ Rename automático (S01E01 format)
- ✅ Atualização diária

---

## 🚀 Docker Compose

```yaml
sonarr-series:
  image: linuxserver/sonarr:latest
  ports:
    - "8989:8989"
  volumes:
    - ./config:/config
    - /media/series:/tv
    - /downloads:/downloads
  environment:
    - TZ=America/Sao_Paulo
  deploy:
    resources:
      limits:
        cpus: '0.3'
        memory: 384M
```

---

## ⚙️ Configuration

```yaml
Quality Profile:
  - 1080p WEB-DL (2-4GB/episode)

Series Monitoring:
  - All Episodes (download past + future)
  - Future Only (only new releases)

Renaming:
  - Pattern: "{Series Title} - S{season:00}E{episode:00} - {Episode Title}"
```

---

## 🔄 Changelog

### v1.0.0
- ✅ Sonarr v4
- ✅ Calendar monitoring
- ✅ Auto download
