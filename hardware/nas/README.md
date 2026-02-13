# Raspberry Pi 5 8GB - Módulo NAS (Network Attached Storage)

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

## 🧠 LLM - Qwen 1.5B Q4_K_M

- **Modelo**: 1.5B parâmetros, 0.9GB VRAM
- **Função**: Organizar arquivos, sugerir categorias, busca semântica ("encontre fotos da praia em 2024")
- **Recursos**: 2.5GB RAM necessária / 8GB disponível = **31% uso** ✅

## 📦 Containers (8 total)

1. **nas-brain** (Ollama Qwen 1.5B) - 2.5GB RAM, 120% CPU
2. **file-sync** (Syncthing) - 512MB RAM, 40% CPU
3. **photo-backup** (PhotoPrism + iCloud sync) - 1.5GB RAM, 80% CPU
4. **object-storage** (MinIO S3-compatible) - 1GB RAM, 60% CPU
5. **deduplication** (Btrfs + rmlint) - 768MB RAM, 50% CPU
6. **smb-server** (Samba shares) - 384MB RAM, 30% CPU
7. **backup-manager** (Restic incremental) - 512MB RAM, 40% CPU
8. **media-indexer** (AI tagging, face recognition) - 1GB RAM, 80% CPU

**Total**: 8.2GB RAM / 8GB = **103% uso** ⚠️ (swap 1GB resolve)  
**CPU**: 500% / 400% = **125% uso** ⚠️ (picos tolerados)

### Repositórios
- [nas-brain](https://github.com/AslamSys/nas-brain)
- [nas-file-sync](https://github.com/AslamSys/nas-file-sync)
- [nas-photo-backup](https://github.com/AslamSys/nas-photo-backup)
- [nas-object-storage](https://github.com/AslamSys/nas-object-storage)
- [nas-deduplication](https://github.com/AslamSys/nas-deduplication)
- [nas-smb-server](https://github.com/AslamSys/nas-smb-server)
- [nas-backup-manager](https://github.com/AslamSys/nas-backup-manager)
- [nas-media-indexer](https://github.com/AslamSys/nas-media-indexer)

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
