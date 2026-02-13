# Raspberry Pi 5 8GB - Módulo de Entretenimento

> 📍 **Navegação:** [🏠 Início](../../README.md) > [🔧 Hardware](../README.md) > [🎬 Entretenimento (RPi 5 8GB)](README.md)

## 📋 Especificações do Hardware

### Raspberry Pi 5 8GB
- **SoC**: Broadcom BCM2712 (Cortex-A76 quad-core 2.4GHz)
- **RAM**: 8GB LPDDR4X-4267
- **GPU**: VideoCore VII (suporte H.265 4K60)
- **Armazenamento**: MicroSD 128GB + **HD Externo 2TB USB 3.0**
- **Rede**: Gigabit Ethernet + Wi-Fi 5
- **Alimentação**: 5V/5A USB-C (27W)
- **Preço**: **$80** + periféricos $20 + HD 2TB $65 = **$165 TOTAL**

## 🎯 Função no Sistema

Módulo responsável por:
- Media server (Plex/Jellyfin)
- Streaming (Netflix, YouTube, Spotify)
- Download automático (torrents, Usenet)
- Organização de biblioteca (Sonarr, Radarr)
- Controle de TV/Som (HDMI-CEC, IR blaster)
- Recomendações personalizadas (ML)

## 🧠 LLM - Qwen 1.5B Q4_K_M

- **Modelo**: 1.5B parâmetros, 0.9GB VRAM
- **Função**: Entender comandos ("coloca aquele filme do Tom Hanks no deserto"), recomendar conteúdo
- **Recursos**: 2.5GB RAM necessária / 8GB disponível = **31% uso** ✅

## 📦 Containers e Repositórios

Este hardware executa **6 containers** especializados em entretenimento:

### 🎬 Ecossistema Entretenimento (6 containers)

| Container | Função | Status | Repositório |
|-----------|--------|--------|-------------|
| **entretenimento-brain** | LLM para mídia (Qwen 1.5B) | 📋 | [AslamSys/entretenimento-brain](https://github.com/AslamSys/entretenimento-brain) |
| **media-server** | Servidor Jellyfin | 📋 | [AslamSys/entretenimento-media-server](https://github.com/AslamSys/entretenimento-media-server) |
| **download-manager** | qBittorrent + Jackett | 📋 | [AslamSys/entretenimento-download-manager](https://github.com/AslamSys/entretenimento-download-manager) |
| **media-organizer** | Radarr + Sonarr | 📋 | [AslamSys/entretenimento-radarr-movies](https://github.com/AslamSys/entretenimento-radarr-movies) |
| **subtitle-fetcher** | Bazarr legendas | 📋 | [AslamSys/entretenimento-bazarr-subtitles](https://github.com/AslamSys/entretenimento-bazarr-subtitles) |
| **streaming-aggregator** | APIs Netflix, Spotify | 📋 | [AslamSys/entretenimento-streaming-aggregator](https://github.com/AslamSys/entretenimento-streaming-aggregator) |

**💡 Status:**
- ✅ **Implementado** - Container funcionando em produção
- ⏳ **Em desenvolvimento** - Código em progresso ativo
- 📋 **Especificado** - Documentado, repositório criado, aguardando implementação

**📊 Fase atual:** Todos os containers estão em **fase de estudo/planejamento** (📋)

**📊 Recursos do Hardware:**
- **RAM Total**: 6GB / 8GB = **75% uso** ✅ (2GB livres)
- **CPU Total**: 360% / 400% = **90% uso** ✅
- **LLM**: Qwen 1.5B Q4_K_M (2.5GB RAM, 120% CPU)

---

## 🔌 Integração NATS

### Comandos Recebidos
```
entretenimento.play.movie         # Reproduzir filme
entretenimento.play.series        # Reproduzir série
entretenimento.play.music         # Tocar música
entretenimento.search.content     # Buscar conteúdo
entretenimento.download.request   # Baixar filme/série
entretenimento.tv.control         # Controlar TV (ligar, volume, canal)
```

### Eventos Publicados
```
entretenimento.now_playing        # O que está tocando agora
entretenimento.download.complete  # Download finalizado
entretenimento.recommendation     # Recomendação de conteúdo
```

## 🎬 Fluxo de Uso

```
Usuário: "Coloca aquele filme do Tom Hanks na ilha deserta"
    ↓
Mordomo Brain: Identifica filme ("Náufrago / Cast Away")
    ↓
NATS → entretenimento.search.content
    {
      "query": "Cast Away Tom Hanks",
      "type": "movie"
    }
    ↓
entretenimento-brain: Busca no Jellyfin
    → Encontrado: /media/movies/Cast Away (2000).mkv
    ↓
NATS → entretenimento.play.movie
    {
      "file": "Cast Away (2000).mkv",
      "device": "tv_sala"  # HDMI-CEC ou Chromecast
    }
    ↓
Jellyfin inicia reprodução na TV
    ↓
NATS → entretenimento.now_playing
    {
      "title": "Cast Away",
      "progress": "00:05:32",
      "device": "tv_sala"
    }
    ↓
Mordomo: "Reproduzindo 'Náufrago' na TV da sala"
```

## 📚 Organização de Biblioteca

### Estrutura de Pastas (HD 2TB)
```
/media/
├── movies/
│   ├── Action/
│   │   └── Mad Max Fury Road (2015) [1080p].mkv
│   ├── Drama/
│   │   └── Cast Away (2000) [1080p].mkv
│   └── Comedy/
│       └── The Big Lebowski (1998) [720p].mkv
│
├── series/
│   ├── Breaking Bad/
│   │   ├── Season 01/
│   │   │   ├── S01E01 - Pilot.mkv
│   │   │   └── S01E02 - Cat's in the Bag.mkv
│   │   └── Season 02/
│   └── Game of Thrones/
│
├── music/
│   ├── Rock/
│   │   └── Pink Floyd - Dark Side of the Moon/
│   └── Jazz/
│       └── Miles Davis - Kind of Blue/
│
└── downloads/
    ├── incomplete/
    └── complete/
```

### Automação com Sonarr/Radarr
```
1. Usuário: "Quero assistir Succession"
2. Brain busca série → Não encontrada na biblioteca
3. Radarr/Sonarr: Busca em indexers (RARBG, 1337x)
4. Download automático via qBittorrent
5. Pós-processamento: Move para /media/series/, renomeia, busca legendas
6. Notifica Mordomo: "Succession S01 disponível!"
```

## 🎵 Integração Streaming

### Spotify (via API)
```python
# Controlar Spotify via comandos de voz
spotify.start_playback(
  device_id='tv_sala',
  context_uri='spotify:playlist:37i9dQZF1DXcBWIGoYBM5M'  # Top 50 Brasil
)
```

### YouTube (via yt-dlp)
```bash
# Baixar e reproduzir vídeo
yt-dlp -f best "https://youtube.com/watch?v=..."
mpv output.mp4
```

### Netflix (via API não-oficial)
```python
# Buscar conteúdo (scraping + Selenium)
results = netflix_search("Stranger Things")
# Não reproduz diretamente (DRM), apenas recommendations
```

## 🗄️ Banco de Dados

### Tabela: `media_library`
```sql
CREATE TABLE media_library (
  id UUID PRIMARY KEY,
  title VARCHAR(255),
  type VARCHAR(20), -- movie, series, music, podcast
  genre VARCHAR(100),
  release_year INTEGER,
  rating DECIMAL(2,1), -- IMDb/TMDb rating
  file_path TEXT,
  file_size BIGINT,
  duration INTEGER, -- segundos
  watched BOOLEAN DEFAULT FALSE,
  watch_count INTEGER DEFAULT 0,
  last_watched TIMESTAMP,
  added_at TIMESTAMP DEFAULT NOW()
);
```

### Tabela: `watch_history`
```sql
CREATE TABLE watch_history (
  id UUID PRIMARY KEY,
  media_id UUID REFERENCES media_library(id),
  user_id UUID,
  started_at TIMESTAMP,
  stopped_at TIMESTAMP,
  progress INTEGER, -- segundos assistidos
  completed BOOLEAN,
  device VARCHAR(50)
);
```

### Tabela: `recommendations`
```sql
CREATE TABLE recommendations (
  id UUID PRIMARY KEY,
  user_id UUID,
  media_id UUID REFERENCES media_library(id),
  score DECIMAL(3,2), -- 0.00 a 1.00
  reason TEXT, -- "Baseado em Breaking Bad que você assistiu"
  shown BOOLEAN DEFAULT FALSE,
  clicked BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## 🐳 Docker Compose

```yaml
version: '3.8'

services:
  entretenimento-brain:
    image: ollama/ollama:latest
    container_name: entretenimento-brain
    volumes:
      - ./models:/root/.ollama
    networks:
      - entretenimento-net
    deploy:
      resources:
        limits:
          memory: 2.5G
          cpus: '1.2'
    restart: unless-stopped

  media-server:
    image: jellyfin/jellyfin:latest
    container_name: jellyfin
    ports:
      - "8096:8096"  # WebUI
      - "8920:8920"  # HTTPS
    volumes:
      - ./config/jellyfin:/config
      - ./cache:/cache
      - /mnt/hd2tb/media:/media:ro  # HD externo montado
    environment:
      - TZ=America/Sao_Paulo
    networks:
      - entretenimento-net
    devices:
      - /dev/dri:/dev/dri  # Hardware acceleration
    deploy:
      resources:
        limits:
          memory: 1.5G
    restart: unless-stopped

  qbittorrent:
    image: linuxserver/qbittorrent:latest
    container_name: qbittorrent
    ports:
      - "8080:8080"  # WebUI
      - "6881:6881"  # Torrent port
      - "6881:6881/udp"
    volumes:
      - ./config/qbittorrent:/config
      - /mnt/hd2tb/media/downloads:/downloads
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/Sao_Paulo
      - WEBUI_PORT=8080
    networks:
      - entretenimento-net
    deploy:
      resources:
        limits:
          memory: 512M
    restart: unless-stopped

  radarr:
    image: linuxserver/radarr:latest
    container_name: radarr
    ports:
      - "7878:7878"
    volumes:
      - ./config/radarr:/config
      - /mnt/hd2tb/media/movies:/movies
      - /mnt/hd2tb/media/downloads:/downloads
    environment:
      - PUID=1000
      - PGID=1000
    depends_on:
      - qbittorrent
    networks:
      - entretenimento-net
    deploy:
      resources:
        limits:
          memory: 384M
    restart: unless-stopped

  sonarr:
    image: linuxserver/sonarr:latest
    container_name: sonarr
    ports:
      - "8989:8989"
    volumes:
      - ./config/sonarr:/config
      - /mnt/hd2tb/media/series:/tv
      - /mnt/hd2tb/media/downloads:/downloads
    environment:
      - PUID=1000
      - PGID=1000
    depends_on:
      - qbittorrent
    networks:
      - entretenimento-net
    deploy:
      resources:
        limits:
          memory: 384M
    restart: unless-stopped

  bazarr:
    image: linuxserver/bazarr:latest
    container_name: bazarr
    ports:
      - "6767:6767"
    volumes:
      - ./config/bazarr:/config
      - /mnt/hd2tb/media/movies:/movies
      - /mnt/hd2tb/media/series:/tv
    environment:
      - PUID=1000
      - PGID=1000
    depends_on:
      - radarr
      - sonarr
    networks:
      - entretenimento-net
    deploy:
      resources:
        limits:
          memory: 256M
    restart: unless-stopped

networks:
  entretenimento-net:
    driver: bridge
```

## 📺 Controle de TV (HDMI-CEC)

### Comandos Suportados
```python
# Ligar/desligar TV
cec-client -s -d 1 << EOF
on 0
EOF

# Ajustar volume
cec-client -s -d 1 << EOF
volup
EOF

# Mudar fonte HDMI
cec-client -s -d 1 << EOF
as 1  # Active Source HDMI 1
EOF
```

### Integração com Mordomo
```
Usuário: "Liga a TV e coloca Netflix"
    ↓
NATS → entretenimento.tv.control {"action": "power_on"}
    ↓
NATS → entretenimento.play.app {"app": "netflix"}
```

## 🎨 Recomendações com ML

### Collaborative Filtering
```python
# Baseado no histórico de usuários similares
similar_users = find_similar_users(user_id, min_similarity=0.7)
recommended_movies = get_their_favorites(similar_users)

# Filtrar já assistidos
new_recommendations = [m for m in recommended_movies 
                       if m not in user_watched]
```

### Content-Based
```python
# Baseado em gênero/atores/diretor de filmes que o usuário gostou
favorite_genres = get_user_favorite_genres(user_id)
# ["Action", "Sci-Fi"]

similar_movies = search_by_genres(favorite_genres, min_rating=7.0)
```

## 💡 Casos de Uso

1. **Maratona Automática**: 
   - "Quero assistir Breaking Bad do início" → Radarr baixa S01-S05 → Jellyfin cria playlist

2. **Descoberta de Música**:
   - "Toca algo parecido com Pink Floyd" → Spotify recommendations API

3. **Cinema em Casa**:
   - "Modo cinema" → Apaga luzes (IoT) + Liga projetor + Abre Jellyfin

4. **Download Inteligente**:
   - "Baixa os episódios novos de Succession toda sexta" → Sonarr monitora

5. **Legendas Automáticas**:
   - Filme baixado → Bazarr busca legenda PT-BR → Renomeia corretamente
