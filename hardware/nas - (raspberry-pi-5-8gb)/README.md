# Raspberry Pi 5 8GB - Módulo NAS (Network Attached Storage)

> 🗂️ **Navegação:** [🏠 Início](../../README.md) > [🔧 Hardware](../README.md) > [💾 NAS (RPi 5 8GB)](README.md)

## 📋 Especificações do Hardware

### Raspberry Pi 5 8GB
- **SoC**: Broadcom BCM2712 (Cortex-A76 quad-core 2.4GHz)
- **RAM**: 8GB LPDDR4X-4267
- **Armazenamento**: 
  - MicroSD 64GB (sistema operacional)
  - **2x HDD 4TB USB 3.0** (8TB total em RAID 1 espelhado)
  - **1x SSD 1TB NVMe via HAT** (cache/hot storage)
- **Rede**: Gigabit Ethernet (1000 Mbps)
- **USB**: 2x USB 3.0 (5 Gbps) + 2x USB 2.0
- **Alimentação**: 5V/5A USB-C (27W)
- **Preço**: **$80** + 2x HDD 4TB $180 + SSD 1TB NVMe $70 + HAT NVMe $25 = **$355 TOTAL**

## 🎯 Função no Sistema

Módulo responsável por:
- **Backup automático** de fotos/vídeos do iPhone (iCloud sync)
- Armazenamento centralizado de arquivos
- Sincronização multiplataforma (Windows, macOS, Linux, mobile)
- Versionamento de arquivos (histórico de alterações)
- Compartilhamento de pastas (SMB, NFS, WebDAV)
- Deduplicação de dados (economizar espaço)
- Backup incremental automático
- Galeria de fotos com AI (reconhecimento facial, tags)

## 🧠 LLM — Cloud API via LiteLLM

- **Estratégia**: Cloud API exclusivamente (Claude, Gemini Flash)
- **Framework**: LiteLLM
- **Função**: Organizar arquivos, busca semântica ("encontre fotos da praia em 2024")
- **Recursos**: ~150MB RAM — nenhum modelo rodando localmente

> LLM local futura, se necessário: Jetson Orin Nano Super dedicado ($249), compartilhado por todos os módulos via API.

## 📦 Containers e Repositórios

Este hardware executa **9 containers** especializados em armazenamento e mídia:

### 💾 Ecossistema NAS + Entretenimento (9 containers)

| Container | Função | Status | Repositório |
|-----------|--------|--------|-------------|
| **nas-brain** | LLM para organização (Cloud API) | 📋 | [AslamSys/nas-brain](https://github.com/AslamSys/nas-brain) |
| **file-sync** | Sincronização Syncthing | 📋 | [AslamSys/nas-file-sync](https://github.com/AslamSys/nas-file-sync) |
| **photo-backup** | Backup fotos PhotoPrism + iCloud | 📋 | [AslamSys/nas-photo-backup](https://github.com/AslamSys/nas-photo-backup) |
| **object-storage** | MinIO S3-compatible | 📋 | [AslamSys/nas-object-storage](https://github.com/AslamSys/nas-object-storage) |
| **deduplication** | Deduplicação Btrfs + rmlint | 📋 | [AslamSys/nas-deduplication](https://github.com/AslamSys/nas-deduplication) |
| **smb-server** | Compartilhamentos Samba | 📋 | [AslamSys/nas-smb-server](https://github.com/AslamSys/nas-smb-server) |
| **backup-manager** | Backup incremental Restic | 📋 | [AslamSys/nas-backup-manager](https://github.com/AslamSys/nas-backup-manager) |
| **media-indexer** | AI tagging + reconhecimento facial | 📋 | [AslamSys/nas-media-indexer](https://github.com/AslamSys/nas-media-indexer) |
| **media-server** | Jellyfin — streaming de mídia | 📋 | [AslamSys/entretenimento-media-server](https://github.com/AslamSys/entretenimento-media-server) |

**💡 Status:**
- ✅ **Implementado** - Container funcionando em produção
- ⏳ **Em desenvolvimento** - Código em progresso ativo
- 📋 **Especificado** - Documentado, repositório criado, aguardando implementação

**📊 Fase atual:** Todos os containers estão em **fase de estudo/planejamento** (📋)

**📊 Recursos do Hardware (recalculado):**
- **RAM Total**: ~2.6GB / 8GB = **32% uso** ✅✅ (5.4GB livres — benefício direto de remover Ollama local)
- **CPU Total**: 200% / 400% = **50% uso** ✅
- **LLM**: Cloud API via LiteLLM (zero RAM local para modelo)

## 📊 Análise de Recursos

```yaml
nas-brain:               CPU: 3-8%    | RAM: 150MB   (LiteLLM client)
file-sync (Syncthing):   CPU: 5-15%   | RAM: 200MB
photo-backup (PhotoPrism): CPU: 20-40% | RAM: 800MB  (AI indexing, face rec)
object-storage (MinIO):  CPU: 3-8%    | RAM: 300MB
deduplication:           CPU: 5-15%   | RAM: 200MB
smb-server (Samba):      CPU: 2-5%    | RAM: 150MB
backup-manager (Restic): CPU: 5-20%   | RAM: 200MB
media-indexer:           CPU: 10-25%  | RAM: 400MB   (CV/ML para tags e faces)

Total:                   CPU: ~55-135% (0.5-1.3 cores) | RAM: ~2.4GB
OS + Docker runtime:     RAM: ~500MB
TOTAL:                   ~2.9GB / 8GB = 36% ✅
MARGEM LIVRE:            ~5.1GB (64%)
```

> **Comparativo anterior (com Ollama):** 8.2GB / 8GB = 103% ⚠️ (precisava de swap).  
> Remover o modelo local libertou **2.5GB** e eliminou a necessidade de swap completamente.

---

## 🔌 Integração NATS

### Comandos Recebidos
```
nas.file.upload               # Upload de arquivo
nas.photo.backup              # Backup de fotos do iPhone
nas.file.search               # Buscar arquivo
nas.file.share                # Compartilhar arquivo/pasta
nas.backup.create             # Criar backup incremental
nas.storage.status            # Verificar espaço disponível
```

### Eventos Publicados
```
nas.file.uploaded             # Arquivo enviado
nas.photo.backed_up           # Foto salva
nas.backup.completed          # Backup concluído
nas.storage.low               # Espaço < 10%
nas.file.duplicated           # Duplicata detectada
```

## 💾 Arquitetura de Storage

### RAID 1 (Espelhamento)
```yaml
Configuração:
  - HDD1 4TB: /dev/sda
  - HDD2 4TB: /dev/sdb
  - RAID 1 (mirror): 4TB úteis
  - Redundância: 100% (tolerância a 1 disco falhar)

Performance:
  - Leitura: ~180 MB/s (USB 3.0 limit)
  - Escrita: ~150 MB/s
  - Latência: ~15ms (HDD spinning disk)

Vantagens:
  - Proteção contra falha de disco
  - Recuperação automática
  - Leitura paralela (2x velocidade)
```

### Tiering (Cache SSD)
```yaml
Hot Storage (SSD NVMe 1TB):
  - Arquivos acessados < 30 dias
  - Fotos recentes (último ano)
  - Velocidade: 1500 MB/s read, 1000 MB/s write

Cold Storage (RAID 1 HDD 4TB):
  - Arquivos > 30 dias sem acesso
  - Backup histórico
  - Velocidade: 180 MB/s read

Auto-Tiering:
  - Move automaticamente arquivos antigos para HDD
  - Cron job diário
```

## 📸 Backup de Fotos do iPhone

### Integração iCloud
```yaml
Método 1: iCloud Photos API
  - pyicloud library
  - Download automático de novas fotos
  - Preserva metadados EXIF (localização, data)
  - Sync bidirecional opcional

Método 2: SMB Share direto
  - iPhone → Arquivos → Conectar ao Servidor
  - smb://nas.local/photos
  - Upload manual ou automático (Shortcuts app)

Método 3: PhotoSync App (iOS)
  - App pago ($2.99)
  - Backup automático via WiFi
  - Suporta WebDAV, SMB, FTP
```

### Fluxo Automático
```
iPhone tira foto
    ↓
iCloud sincroniza (nuvem Apple)
    ↓
nas-brain detecta nova foto (pyicloud polling a cada 5 min)
    ↓
Download foto para /hot-storage/photos/2025/11/
    ↓
PhotoPrism indexa (AI tags, faces, geolocalização)
    ↓
Deduplicação (rmlint verifica hash SHA-256)
    ↓
Backup incremental para RAID 1 (Restic)
    ↓
NATS → nas.photo.backed_up
    {
      "filename": "IMG_1234.HEIC",
      "size_mb": 3.2,
      "date": "2025-11-27",
      "location": "São Paulo, Brasil",
      "faces": ["Renan", "Maria"],
      "tags": ["praia", "sunset", "família"]
    }
    ↓
Mordomo: "Foto da praia salva! 1.234 fotos no total."
```

## 🗂️ Estrutura de Pastas

### Hot Storage (SSD 1TB)
```
/hot-storage/
├── photos/
│   ├── 2025/
│   │   ├── 11/
│   │   │   ├── IMG_1234.HEIC
│   │   │   └── IMG_1235.HEIC
│   └── albums/
│       ├── Família/
│       └── Viagens/
├── videos/
│   ├── 2025/
│   └── projects/
├── documents/
│   ├── Trabalho/
│   ├── Pessoal/
│   └── Impostos/
└── temp/
    └── uploads/
```

### Cold Storage (RAID 1 4TB)
```
/cold-storage/
├── backups/
│   ├── incremental/
│   │   ├── 2025-11-27.restic
│   │   └── 2025-11-26.restic
│   └── snapshots/
├── archive/
│   ├── photos_2020-2023/
│   ├── videos_old/
│   └── documents_archive/
└── media/
    ├── movies/  # Link simbólico para Entretenimento
    └── music/
```

## 🔍 Busca Inteligente com LLM

### Comandos Naturais
```python
Usuário: "Encontra as fotos da praia do ano passado"
    ↓
nas-brain: 
  - Interpreta: location=praia, year=2024
  - Busca no PhotoPrism: tags:beach AND date:2024
  - Retorna: 47 fotos encontradas
    ↓
Mordomo: "Encontrei 47 fotos da praia em 2024. Quer que eu mostre?"

Usuário: "Mostra os documentos de imposto de 2024"
    ↓
nas-brain:
  - Busca: /documents/Impostos/*2024*
  - Retorna: IR_2024.pdf, IPTU_2024.pdf
    ↓
Mordomo: "Encontrei 2 documentos: IR 2024 e IPTU 2024."
```

## 🔒 Segurança e Backup

### Criptografia
```yaml
At-Rest:
  - LUKS encryption nos HDDs
  - AES-256-XTS
  - Key armazenada no Mordomo (KMS)

In-Transit:
  - TLS 1.3 para SMB
  - HTTPS para MinIO/PhotoPrism
  - Syncthing encrypted sync
```

### Estratégia 3-2-1
```yaml
3 cópias:
  1. Original (SSD hot storage)
  2. RAID 1 (cold storage)
  3. Cloud backup (opcional: Backblaze B2)

2 mídias diferentes:
  - SSD NVMe
  - HDD spinning disk

1 offsite:
  - Cloud backup (Backblaze B2: $6/TB/mês)
  - Ou HDD externo em local físico diferente
```

### Backup Incremental (Restic)
```yaml
Frequência:
  - Hot storage → RAID 1: A cada 6 horas
  - RAID 1 → Cloud: Diário às 3h

Retenção:
  - Últimos 7 dias: Todos os backups
  - Último mês: 1 backup/dia
  - Último ano: 1 backup/semana
  - Histórico: 1 backup/mês

Espaço economizado:
  - Deduplicação: ~60% (arquivos repetidos)
  - Compressão: ~30% (zstd)
  - Total: ~18% do espaço original
```

## 📊 Monitoramento de Storage

### Alertas Automáticos
```yaml
Espaço < 10%:
  - NATS → nas.storage.low
  - Mordomo notifica: "Espaço no NAS crítico! 350GB restantes."

Disco com erro SMART:
  - smartctl monitora saúde dos HDDs
  - NATS → nas.disk.failing
  - Mordomo: "URGENTE: Disco 1 com setores ruins! Substituir ASAP."

Temperatura alta:
  - HDD > 50°C
  - NATS → nas.temperature.high
  - Mordomo: "Discos quentes! Verificar ventilação."
```

## 🌐 Acesso Remoto Seguro

### VPN (WireGuard)
```yaml
Setup:
  - WireGuard VPN no Mordomo
  - Acesso seguro fora de casa
  - IP fixo via DDNS (DuckDNS)

Velocidade:
  - Upload residencial: ~20 Mbps (típico Brasil)
  - Backup de 1GB de fotos: ~7 minutos
```

### WebDAV (Acesso Web)
```yaml
URL: https://nas.mordomo.local/webdav
Cliente iOS: Files app (conectar servidor)
Cliente Android: Solid Explorer
Desktop: Rclone, Cyberduck
```

## 💡 Casos de Uso

### 1. Backup Automático iPhone
```
iPhone conecta ao WiFi de casa → PhotoSync detecta → Upload automático para /photos/
```

### 2. Compartilhar Álbum de Família
```
Usuário: "Compartilha as fotos do Natal com a vó"
→ nas-brain cria link público no PhotoPrism
→ Envia link via WhatsApp (módulo Comunicação)
```

### 3. Versionamento de Documentos
```
Edita contrato.docx → Salva no NAS → Versão anterior preservada
→ Restic mantém histórico de 30 dias
→ Restauração: restic restore --target 2025-11-20
```

### 4. Busca Semântica
```
"Encontra aquele PDF sobre investimentos que baixei mês passado"
→ nas-brain busca: type:pdf, topic:investimentos, date:outubro-2024
→ Retorna: Guia_Investimentos_2024.pdf
```

## 📈 Performance

### Benchmarks
```yaml
Upload 1000 fotos (5GB):
  - Via WiFi 5 (866 Mbps): ~8 minutos
  - Via Gigabit Ethernet: ~4 minutos

Busca de arquivo (PhotoPrism):
  - Index de 100.000 fotos: < 200ms
  - Reconhecimento facial: ~1s por foto

Backup incremental (Restic):
  - 10GB de mudanças: ~12 minutos
  - Snapshot completo: ~3 horas (primeira vez)
```

## 🔧 Manutenção

### Health Checks
```bash
# SMART disk health
smartctl -a /dev/sda

# RAID status
cat /proc/mdstat

# Espaço disponível
df -h /hot-storage /cold-storage

# Temperatura dos discos
hddtemp /dev/sda /dev/sdb

# Restic integrity check
restic check
```

## 💰 Custo Total do NAS

```yaml
Hardware:
  - Raspberry Pi 5 8GB: $80
  - 2x HDD 4TB (WD Red): $180
  - SSD NVMe 1TB: $70
  - NVMe HAT: $25
  - Case com ventilação: $15
  - Cabos USB 3.0: $10
  SUBTOTAL: $380

Cloud Backup (opcional):
  - Backblaze B2: $6/TB/mês
  - 4TB backup: $24/mês = $288/ano

Total Ano 1: $380 + $288 = $668
Custo/GB: $668 / 4000GB = $0.17/GB/ano

Comparação iCloud:
  - 2TB iCloud: $9.99/mês = $120/ano
  - 4TB NAS equivalente: $24/mês = $288/ano
  - Vantagem NAS: Controle total, sem limite, RAID
```

## 🎯 Vantagens vs Cloud

```yaml
✅ Privacidade total (dados em casa)
✅ Sem limite de espaço (expandível)
✅ Velocidade LAN (1 Gbps vs 20 Mbps upload cloud)
✅ Custo fixo (sem mensalidade infinita)
✅ Acesso offline
✅ Integração com Mordomo

❌ Requer manutenção (discos, updates)
❌ Consumo elétrico (~15W contínuo)
❌ Risco de perda (incêndio, roubo) - mitigado com cloud backup
```
