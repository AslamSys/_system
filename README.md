# Aslam System - Central Orchestration

> **Repository central de orquestração** para o sistema distribuído Aslam

Este repositório contém docker-compose files, configurações e documentação para deploy completo do sistema Aslam em 7 hardwares ARM64.

---

## 📁 Estrutura

```
_system/
├── README.md                    # Este arquivo
├── hardware/
│   ├── aslam/                   # Orange Pi 5 16GB (16 containers)
│   │   ├── README.md            # Docs do ecossistema Aslam
│   │   └── docker-compose.yml   # (a criar)
│   │
│   ├── nas/                     # Raspberry Pi 5 8GB (8 containers)
│   │   ├── README.md
│   │   └── docker-compose.yml   # (a criar)
│   │
│   ├── seguranca/               # Jetson Orin Nano (7 containers)
│   ├── investimentos/           # Raspberry Pi 5 16GB (7 containers)
│   ├── entretenimento/          # Raspberry Pi 5 8GB (6 containers)
│   ├── pagamentos/              # Raspberry Pi 5 4GB (6 containers)
│   └── iot/                     # Raspberry Pi 3B (3 containers)
│
├── .env.example                 # Template de variáveis
└── docker-compose.yml           # Master compose (a criar)
```

---

## 🚀 Quick Start

### 1. Clone este repo
```bash
git clone https://github.com/AslamSys/_system
cd _system
```

### 2. Configure environment
```bash
cp .env.example .env
# Edite .env com suas credenciais (NATS, Azure, etc)
```

### 3. Deploy por hardware

#### Orange Pi 5 — Aslam (assistente de voz)
```bash
docker compose -f hardware/aslam/docker-compose.yml up -d
```

#### Raspberry Pi 5 — NAS
```bash
docker compose -f hardware/nas/docker-compose.yml up -d
```

#### Jetson Orin Nano — Segurança
```bash
docker compose -f hardware/seguranca/docker-compose.yml up -d
```

*E assim sucessivamente para cada hardware.*

---

## 📦 Sobre os Containers

Os **códigos-fonte** de cada container estão em **repositórios separados**:

- `aslam-*` — 16 containers do assistente de voz
- `nas-*` — 8 containers de storage
- `seguranca-*` — 7 containers de câmeras + AI
- `investimentos-*` — 7 containers de trading
- `entretenimento-*` — 6 containers de media
- `pagamentos-*` — 6 containers de PIX/banking
- `iot-*` — 3 containers de automação

**[Ver todos os repos →](https://github.com/orgs/AslamSys/repositories)**

---

## 🔗 Comunicação (NATS)

Todos os containers se comunicam via **NATS** (message broker). Ver configuração em cada `docker-compose.yml`.

---

## 📖 Documentação

- **Cada hardware:** Ver `hardware/{nome}/README.md`
- **Cada container:** Ver repositório individual
- **Organização:** https://github.com/AslamSys

---

## 🛠️ Status de Implementação

| Hardware | Containers | Repos criados | Código implementado | Deploy testado |
|----------|-----------|---------------|---------------------|----------------|
| **Aslam** | 16 | ✅ | ⏳ 6/16 | ❌ |
| **NAS** | 8 | ✅ | ❌ | ❌ |
| **Segurança** | 7 | ✅ | ❌ | ❌ |
| **Investimentos** | 7 | ✅ | ❌ | ❌ |
| **Entretenimento** | 6 | ✅ | ❌ | ❌ |
| **Pagamentos** | 6 | ✅ | ❌ | ❌ |
| **IoT** | 3 | ✅ | ❌ | ❌ |

---

## 🎯 Próximos Passos

1. ⏳ Criar docker-compose.yml para cada hardware
2. ⏳ Migrar código dos containers implementados para seus repos
3. ⏳ Setup CI/CD (GitHub Actions) em cada repo
4. ⏳ Publicar imagens Docker no ghcr.io
5. ⏳ Testar deploy em hardware real

---

**Maintainer:** [@renancaf](https://github.com/renancaf)  
**License:** MIT  
**Last Updated:** February 2026
