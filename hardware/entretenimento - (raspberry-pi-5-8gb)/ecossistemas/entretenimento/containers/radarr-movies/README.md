# 🎥 Radarr (Movies)

**Container:** `radarr-movies`  
**Stack:** Radarr + qBittorrent  
**Propósito:** Download automático de filmes

---

## 📋 Propósito

Gerenciador de downloads de filmes. Integra com Jackett (torrents) e qBittorrent. Organiza automaticamente em /media/movies.

---

## 🎯 Features

- ✅ Download automático de filmes
- ✅ Quality profiles (1080p, 4K)
- ✅ Integração com Jackett (100+ trackers)
- ✅ Rename automático (padrão Jellyfin)
- ✅ Monitora lançamentos

---

## 🚀 Docker Compose

```yaml
radarr-movies:
  image: linuxserver/radarr:latest
  ports:
    - "7878:7878"
  volumes:
    - ./config:/config
    - /media/movies:/movies
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
  - 1080p Bluray (6-10GB)
  - 4K HDR (15-25GB)

Indexers (via Jackett):
  - The Pirate Bay
  - 1337x
  - RARBG

Download Client:
  - qBittorrent (port 8080)
```

---

## 🔄 Changelog

### v1.0.0
- ✅ Radarr v5
- ✅ Jackett integration
- ✅ Auto organize
