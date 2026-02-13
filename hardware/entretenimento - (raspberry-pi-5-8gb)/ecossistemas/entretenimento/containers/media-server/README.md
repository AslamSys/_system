# 📺 Jellyfin Media Server

**Container:** `media-server`  
**Stack:** Jellyfin  
**Storage:** HD 2TB USB 3.0

---

## 📋 Propósito

Media server open-source. Organiza e transmite filmes, séries, música. Transcodificação H.265 4K.

---

## 🎯 Features

- ✅ Transcoding H.265 → H.264 (VideoCore VII)
- ✅ 4K 60fps playback
- ✅ Metadata automático (IMDb, TMDb)
- ✅ Multi-user profiles
- ✅ Chromecast support

---

## 🚀 Docker Compose

```yaml
media-server:
  image: jellyfin/jellyfin:latest
  ports:
    - "8096:8096"  # WebUI
    - "1900:1900/udp"  # DLNA
  volumes:
    - /media:/media  # HD 2TB
    - ./config:/config
    - ./cache:/cache
  devices:
    - /dev/dri:/dev/dri  # Hardware transcoding
  environment:
    - TZ=America/Sao_Paulo
  deploy:
    resources:
      limits:
        cpus: '1.0'
        memory: 1536M
```

---

## 📁 Library Structure

```yaml
/media/
  movies/
    - Cast Away (2000).mkv
    - The Terminal (2004).mkv
  series/
    - Breaking Bad/
      - Season 01/
        - S01E01.mkv
  music/
    - Artist/
      - Album/
        - Track.mp3
```

---

## 🔄 Changelog

### v1.0.0
- ✅ Jellyfin latest
- ✅ HW transcoding
- ✅ 2TB storage
