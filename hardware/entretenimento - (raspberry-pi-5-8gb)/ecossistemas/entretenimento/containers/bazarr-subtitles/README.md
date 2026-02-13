# 💬 Bazarr (Subtitles)

**Container:** `bazarr-subtitles`  
**Stack:** Bazarr  
**Propósito:** Download automático de legendas

---

## 📋 Propósito

Gerenciador de legendas. Baixa automaticamente legendas em português para filmes e séries do Jellyfin.

---

## 🎯 Features

- ✅ Download automático de legendas PT-BR
- ✅ Integra com Radarr + Sonarr
- ✅ Sync com Jellyfin
- ✅ Múltiplos providers (OpenSubtitles, Legendas.tv)

---

## 🚀 Docker Compose

```yaml
bazarr-subtitles:
  image: linuxserver/bazarr:latest
  ports:
    - "6767:6767"
  volumes:
    - ./config:/config
    - /media:/media
  environment:
    - TZ=America/Sao_Paulo
  deploy:
    resources:
      limits:
        cpus: '0.2'
        memory: 256M
```

---

## ⚙️ Providers

```yaml
- OpenSubtitles.org
- Legendas.tv (Brazilian)
- Subscene
- Podnapisi
```

---

## 🔄 Changelog

### v1.0.0
- ✅ Bazarr v1.4
- ✅ PT-BR priority
- ✅ Radarr/Sonarr sync
