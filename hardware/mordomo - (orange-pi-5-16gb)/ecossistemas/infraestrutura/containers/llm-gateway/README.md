# 🤖 LLM Gateway (Infraestrutura)

**Container:** `llm-gateway`  
**Ecossistema:** Infraestrutura  
**Papel:** Proxy Centralizado de Inferência LLM  
**Porta:** 4000 (API OpenAI-compatible)  
**UI Admin:** 4001

---

## 📋 Propósito

Ponto único de entrada para **todas as chamadas de inferência LLM** do sistema. Todos os brains (`mordomo-brain`, `nas-brain`, `entretenimento-brain`, etc.) apontam exclusivamente para este container. A decisão de usar Cloud ou local é feita aqui — os containers consumidores não sabem nem precisam saber qual provedor está sendo usado.

Isso significa: **trocar o modelo de qualquer ecossistema é uma mudança de 1 linha no `config.yaml`**, sem tocar no código de nenhum container.

---

## 🎯 Responsabilidades

- ✅ Roteamento de requisições para Cloud (Anthropic, OpenAI, Google) ou local (Ollama no Jetson)
- ✅ "Virtual models" por ecossistema — cada brain tem seu alias configurável
- ✅ Fallback automático: cloud cai → tenta local; local cai → tenta cloud
- ✅ Logging centralizado de todas as chamadas (custo, latência, tokens)
- ✅ Rate limiting por virtual model
- ✅ Gestão centralizada de API keys (um único `.env` no Orange Pi)
- ✅ UI de administração para monitorar uso e trocar modelos sem restart

---

## 🔧 Tecnologias

**LiteLLM Proxy Server** (ghcr.io/berriai/litellm)
- compatível com OpenAI API (`/v1/chat/completions`)
- suporte nativo a 100+ provedores
- SQLite integrado para logs de uso
- UI admin em `/ui`

---

## 🗺️ Arquitetura de Roteamento

```
Qualquer Brain (qualquer hardware)
  POST http://llm-gateway:4000/v1/chat/completions
  { "model": "mordomo-brain", ... }
         │
         ▼
  ┌──────────────────────────────────────────────┐
  │         LiteLLM Proxy (config.yaml)          │
  │                                              │
  │  mordomo-brain      → claude-3-5-sonnet      │  ← Cloud
  │  entretenimento     → gemini/gemini-flash     │  ← Cloud
  │  nas-brain          → gemini/gemini-flash     │  ← Cloud
  │  investimentos-brain→ claude-3-5-sonnet      │  ← Cloud
  │  pagamentos-brain   → claude-3-5-sonnet      │  ← Cloud
  │  seguranca-brain    → ollama/qwen3b-vision    │  ← Local Jetson*
  │                                              │
  └──────────────────────────────────────────────┘
         │                          │
         ▼                          ▼
  api.anthropic.com         http://jetson-llm:11434
  api.openai.com            (Ollama no Jetson Orin)
  generativelanguage.google
```

> *Segurança usa local por necessidade de visão em tempo real. Todos os demais usam cloud por padrão.

---

## ⚙️ Configuração (`config.yaml`)

```yaml
model_list:
  # Virtual model: mordomo-brain
  - model_name: mordomo-brain
    litellm_params:
      model: claude/claude-3-5-sonnet-20241022
      api_key: os.environ/ANTHROPIC_API_KEY

  # Virtual model: entretenimento
  - model_name: entretenimento
    litellm_params:
      model: gemini/gemini-2.0-flash
      api_key: os.environ/GEMINI_API_KEY

  # Virtual model: nas-brain
  - model_name: nas-brain
    litellm_params:
      model: gemini/gemini-2.0-flash
      api_key: os.environ/GEMINI_API_KEY

  # Virtual model: investimentos-brain
  - model_name: investimentos-brain
    litellm_params:
      model: claude/claude-3-5-sonnet-20241022
      api_key: os.environ/ANTHROPIC_API_KEY

  # Virtual model: pagamentos-brain
  - model_name: pagamentos-brain
    litellm_params:
      model: claude/claude-3-5-sonnet-20241022
      api_key: os.environ/ANTHROPIC_API_KEY

  # Virtual model: seguranca-brain (local — latência crítica)
  - model_name: seguranca-brain
    litellm_params:
      model: ollama/qwen2.5-vl:3b
      api_base: http://jetson-llm:11434

litellm_settings:
  # Fallback automático: se cloud cair, tenta modelo de fallback
  fallbacks:
    - {"mordomo-brain": ["nas-brain-fallback"]}

  # Log de uso para análise de custo
  success_callback: ["langfuse"]
  failure_callback: ["langfuse"]

general_settings:
  master_key: os.environ/LLM_GATEWAY_MASTER_KEY
  database_url: "sqlite:///llm_gateway.db"
```

---

## 🐳 Docker Compose

```yaml
services:
  llm-gateway:
    image: ghcr.io/berriai/litellm:main-stable
    container_name: llm-gateway
    restart: unless-stopped
    ports:
      - "4000:4000"   # API (OpenAI-compatible)
      - "4001:4001"   # UI Admin
    volumes:
      - ./config.yaml:/app/config.yaml:ro
      - llm-gateway-data:/app/data
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - LLM_GATEWAY_MASTER_KEY=${LLM_GATEWAY_MASTER_KEY}
    command: ["--config", "/app/config.yaml", "--port", "4000", "--num_workers", "2"]
    deploy:
      resources:
        limits:
          memory: 200M
        reservations:
          memory: 100M

volumes:
  llm-gateway-data:
```

---

## 🔗 Como os Brains se Conectam

Todo container brain usa a mesma URL, independente de estar no Orange Pi, RPi ou Jetson:

```python
# Em qualquer *-brain, a única config necessária:
LLM_BASE_URL = "http://llm-gateway:4000"   # na mesma rede Docker (Orange Pi)
# ou
LLM_BASE_URL = "http://192.168.1.10:4000"  # acesso via IP local (outros hardwares)

# Chamada idêntica para qualquer provedor:
import litellm
response = litellm.completion(
    model="mordomo-brain",          # virtual model — gateway decide o real
    api_base=LLM_BASE_URL,
    messages=[{"role": "user", "content": "..."}]
)
```

Para trocar o modelo do `mordomo-brain` de Claude para Gemini, basta editar 1 linha no `config.yaml` e fazer `docker kill -s HUP llm-gateway` (reload sem downtime).

---

## 📊 Especificações

| Recurso | Valor |
|---------|-------|
| **RAM** | ~100MB idle / ~200MB pico |
| **CPU** | <2% (proxy leve, I/O bound) |
| **Porta API** | 4000 |
| **Porta Admin UI** | 4001 |
| **Protocolo** | OpenAI-compatible REST |
| **Restart** | `unless-stopped` |
| **Dependências** | Nenhuma infra (stateless exceto SQLite) |

---

## 🔑 Segurança

- API keys em `.env` no Orange Pi — **nunca** no `config.yaml` ou no código
- `LLM_GATEWAY_MASTER_KEY` proteção de acesso à UI admin e à API
- Container na rede Docker interna — porta 4000 **não exposta** externamente (apenas LAN)
- TLS opcional para comunicação entre hardwares distintos

---

## 🔄 Trocar LLM sem downtime

```bash
# Editar config.yaml:
# Trocar nas-brain de cloud para local (Jetson):
#   model: gemini/gemini-2.0-flash  →  model: ollama/llama3.1:8b
#                                       api_base: http://jetson-llm:11434

# Reload sem derrubar o container:
docker kill -s HUP llm-gateway
```

Todos os containers cliente (`nas-brain`, etc.) continuam rodando sem interrupção.
