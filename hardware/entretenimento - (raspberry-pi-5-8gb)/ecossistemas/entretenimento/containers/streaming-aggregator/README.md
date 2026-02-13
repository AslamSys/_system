# 🌐 Streaming Aggregator

**Container:** `streaming-aggregator`  
**Stack:** Node.js + APIs (Netflix, Spotify)  
**Propósito:** Agregador de streaming services

---

## 📋 Propósito

Integração com serviços de streaming (Netflix, Spotify, YouTube). Controle via NATS, busca unificada.

---

## 🎯 Features

- ✅ Spotify API (play, pause, skip)
- ✅ YouTube API (search, play)
- ✅ Netflix (via scraping, sem API oficial)
- ✅ Busca unificada em múltiplos serviços

---

## 🔌 NATS Topics

### Subscribe
```javascript
Topic: "entretenimento.play.music"
Payload: {
  "service": "spotify",
  "query": "Imagine Dragons",
  "type": "artist"
}

Topic: "entretenimento.youtube.play"
Payload: {
  "query": "trailer Dune 2",
  "device": "chromecast_sala"
}
```

---

## 🚀 Docker Compose

```yaml
streaming-aggregator:
  build: ./streaming-aggregator
  environment:
    - SPOTIFY_CLIENT_ID=${SPOTIFY_CLIENT_ID}
    - SPOTIFY_CLIENT_SECRET=${SPOTIFY_CLIENT_SECRET}
    - YOUTUBE_API_KEY=${YOUTUBE_API_KEY}
  deploy:
    resources:
      limits:
        cpus: '0.3'
        memory: 512M
```

---

## 🧪 Código (Spotify)

```javascript
const SpotifyWebApi = require('spotify-web-api-node');

const spotify = new SpotifyWebApi({
    clientId: process.env.SPOTIFY_CLIENT_ID,
    clientSecret: process.env.SPOTIFY_CLIENT_SECRET,
    redirectUri: 'http://localhost:8888/callback'
});

async function playSpotify(query, type = 'artist') {
    // Search
    const results = await spotify.search(query, [type]);
    const uri = results.body[type + 's'].items[0].uri;
    
    // Play on active device
    await spotify.play({ context_uri: uri });
    
    return {
        playing: results.body[type + 's'].items[0].name,
        uri
    };
}
```

---

## 🔄 Changelog

### v1.0.0
- ✅ Spotify integration
- ✅ YouTube API
- ✅ Unified search
