# 📊 Dashboard UI

**Container:** `dashboard-ui`  
**Ecossistema:** Mordomo  
**Tipo:** Frontend Web Application

---

## 📋 Propósito

Interface web para monitoramento em tempo real, gerenciamento de conversas e configuração do assistente Mordomo.

---

## 🎯 Responsabilidades

- ✅ Visualização de conversas em tempo real
- ✅ Histórico de interações
- ✅ Gerenciamento de usuários (enrollment de vozes)
- ✅ Configurações do sistema
- ✅ Monitoramento de status dos containers
- ✅ Logs e eventos em tempo real
- ✅ Controle manual (pause/resume pipeline)

---

## 🔧 Tecnologias

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- TailwindCSS (styling)
- shadcn/ui (components)

**State Management:**
- Zustand (global state)
- React Query (server state)

**Real-time:**
- WebSocket (eventos NATS)
- SSE (Server-Sent Events para logs)

**Visualização:**
- Recharts (gráficos)
- React-Audio-Player (playback)
- Waveform-react (visualização de áudio)

---

## 📊 Funcionalidades

### 1. Home / Dashboard
```
┌─────────────────────────────────────────┐
│ 🏠 Aslam Dashboard                      │
├─────────────────────────────────────────┤
│                                         │
│  📊 Status dos Serviços                 │
│  ✅ Audio Capture      [99% uptime]     │
│  ✅ Wake Word          [Active]         │
│  ✅ Whisper ASR        [2.5s latency]   │
│  ✅ Brain              [Qwen 2.5 3B]    │
│  ✅ TTS Engine         [Playing]        │
│                                         │
│  📈 Métricas Hoje                       │
│  • 47 conversas                         │
│  • 3 usuários ativos                    │
│  • 156 interações                       │
│  • 94.3% taxa de sucesso                │
│                                         │
│  🔊 Última Conversa (2 min atrás)       │
│  User: "Qual a temperatura?"            │
│  Aslam: "A temperatura atual é 23°C"   │
└─────────────────────────────────────────┘
```

### 2. Conversas em Tempo Real
```
┌─────────────────────────────────────────┐
│ 💬 Conversas                            │
├─────────────────────────────────────────┤
│                                         │
│  [Renan] 14:35:22                       │
│  🎤 "Aslam, acenda a luz da sala"       │
│  🔊 "Luz da sala acesa com sucesso"     │
│                                         │
│  [Maria] 14:32:10                       │
│  🎤 "Que horas são?"                    │
│  🔊 "São quatorze horas e trinta e      │
│      dois minutos"                      │
│                                         │
│  [Filipe] 14:28:45                      │
│  🎤 "Lembrete para reunião às 3"        │
│  🔊 "Ok, criei um lembrete para 15h"   │
│                                         │
│  📊 Detalhes da Conversa                │
│  • Latência STT: 1.2s                   │
│  • Latência Brain: 0.8s                 │
│  • Latência TTS: 0.5s                   │
│  • Total: 2.5s                          │
└─────────────────────────────────────────┘
```

### 3. Gerenciamento de Usuários
```
┌─────────────────────────────────────────┐
│ 👥 Usuários                             │
├─────────────────────────────────────────┤
│                                         │
│  Renan              [Autorizado]        │
│  📊 247 interações                      │
│  🎤 Voice enrolled: ✅                  │
│  🔑 Confidence: 0.94                    │
│  [Editar] [Remover]                     │
│                                         │
│  Maria              [Autorizado]        │
│  📊 128 interações                      │
│  🎤 Voice enrolled: ✅                  │
│  🔑 Confidence: 0.91                    │
│  [Editar] [Remover]                     │
│                                         │
│  [+ Adicionar Novo Usuário]             │
│                                         │
│  ➕ Enrollment de Voz                   │
│  1. Diga: "Aslam, cadastrar minha voz" │
│  2. Repita 5 frases diferentes          │
│  3. Sistema cria embedding              │
└─────────────────────────────────────────┘
```

### 4. Configurações
```
┌─────────────────────────────────────────┐
│ ⚙️ Configurações                        │
├─────────────────────────────────────────┤
│                                         │
│  🔊 Audio                               │
│  • VAD Threshold: [======] 0.5          │
│  • Sample Rate: 16000 Hz                │
│  • Channels: Mono                       │
│                                         │
│  🎤 Wake Word                           │
│  • Palavra: "Aslam"                     │
│  • Sensitivity: [=====] 0.7             │
│                                         │
│  🧠 Brain                               │
│  • Modelo Local: Qwen 2.5 3B            │
│  • Cloud Fallback: ✅ Habilitado        │
│  • Temperature: [===] 0.7               │
│  • Max Tokens: 200                      │
│                                         │
│  🔊 TTS                                 │
│  • Voz: pt_BR-faber-medium              │
│  • Velocidade: [====] 1.0x              │
│  • Volume: [======] 0.8                 │
│                                         │
│  [Salvar Alterações]                    │
└─────────────────────────────────────────┘
```

### 5. Logs & Eventos
```
┌─────────────────────────────────────────┐
│ 📝 Logs (tempo real)                    │
├─────────────────────────────────────────┤
│                                         │
│  [14:35:22] [audio-capture] Audio chunk │
│             received (320ms)            │
│  [14:35:22] [wake-word] Wake word       │
│             detected (confidence: 0.89) │
│  [14:35:23] [speaker-verify] Speaker    │
│             verified: Renan (0.94)      │
│  [14:35:24] [whisper-asr] Transcription:│
│             "Aslam acenda a luz..."     │
│  [14:35:24] [brain] Intent detected:    │
│             IOT_CONTROL                 │
│  [14:35:25] [brain] Action executed:    │
│             turn_on(light, sala)        │
│  [14:35:25] [tts] Synthesizing response │
│                                         │
│  Filtros: [INFO] [WARN] [ERROR]         │
│  Containers: [Todos ▼]                  │
└─────────────────────────────────────────┘
```

### 6. Monitoramento
```
┌─────────────────────────────────────────┐
│ 📈 Métricas                             │
├─────────────────────────────────────────┤
│                                         │
│  Latência End-to-End (últimas 24h)      │
│  📊 [Gráfico de linhas]                 │
│     Média: 2.3s | P95: 3.8s | P99: 5.2s │
│                                         │
│  Taxa de Sucesso                        │
│  📊 [Gráfico de pizza]                  │
│     ✅ Sucesso: 94.3%                   │
│     ⚠️  Parcial: 4.2%                   │
│     ❌ Falha: 1.5%                      │
│                                         │
│  Uso de Recursos                        │
│  📊 CPU: [====    ] 45%                 │
│  📊 RAM: [======  ] 68%                 │
│  📊 Disk: [==     ] 23%                 │
└─────────────────────────────────────────┘
```

---

## 🔌 API Integration

### REST API (Core API)
```typescript
// api/client.ts
const API_BASE = 'http://mordomo-core-api:8000/api'

export const api = {
  // Conversas
  getConversations: () => 
    fetch(`${API_BASE}/conversations`).then(r => r.json()),
  
  getConversation: (id: string) =>
    fetch(`${API_BASE}/conversations/${id}`).then(r => r.json()),
  
  // Usuários
  getUsers: () =>
    fetch(`${API_BASE}/users`).then(r => r.json()),
  
  createUser: (data: UserData) =>
    fetch(`${API_BASE}/users`, {
      method: 'POST',
      body: JSON.stringify(data)
    }).then(r => r.json()),
  
  // Configurações
  getConfig: () =>
    fetch(`${API_BASE}/config`).then(r => r.json()),
  
  updateConfig: (config: Config) =>
    fetch(`${API_BASE}/config`, {
      method: 'PUT',
      body: JSON.stringify(config)
    }).then(r => r.json()),
  
  // Métricas
  getMetrics: () =>
    fetch(`${API_BASE}/metrics`).then(r => r.json())
}
```

### WebSocket (Real-time Events)
```typescript
// hooks/useRealtimeEvents.ts
export function useRealtimeEvents() {
  const [events, setEvents] = useState<Event[]>([])
  
  useEffect(() => {
    const ws = new WebSocket('ws://mordomo-core-api:8000/ws/events')
    
    ws.onmessage = (msg) => {
      const event = JSON.parse(msg.data)
      setEvents(prev => [event, ...prev].slice(0, 100))
    }
    
    return () => ws.close()
  }, [])
  
  return events
}

// Uso:
function LogsPanel() {
  const events = useRealtimeEvents()
  
  return (
    <div>
      {events.map(e => (
        <div key={e.id}>
          [{e.timestamp}] [{e.source}] {e.message}
        </div>
      ))}
    </div>
  )
}
```

---

## ⚙️ Configuração

### Vite Config
```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://mordomo-core-api:8000',
        changeOrigin: true
      },
      '/ws': {
        target: 'ws://mordomo-core-api:8000',
        ws: true
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
})
```

### Environment Variables
```bash
# .env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_APP_NAME=Aslam Dashboard
```

---

## 📁 Estrutura de Projeto

```
dashboard-ui/
├── public/
│   └── logo.svg
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   ├── Dashboard.tsx
│   │   ├── Conversations.tsx
│   │   ├── Users.tsx
│   │   ├── Settings.tsx
│   │   ├── Logs.tsx
│   │   └── Metrics.tsx
│   ├── hooks/
│   │   ├── useRealtimeEvents.ts
│   │   ├── useConversations.ts
│   │   └── useMetrics.ts
│   ├── lib/
│   │   ├── api.ts
│   │   └── utils.ts
│   ├── store/
│   │   └── useStore.ts      # Zustand
│   ├── types/
│   │   └── index.ts
│   ├── App.tsx
│   └── main.tsx
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── vite.config.ts
```

---

## 🐳 Docker

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Nginx Config
```nginx
# nginx.conf
server {
    listen 80;
    server_name _;
    
    root /usr/share/nginx/html;
    index index.html;
    
    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API proxy
    location /api {
        proxy_pass http://mordomo-core-api:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
    
    # WebSocket proxy
    location /ws {
        proxy_pass http://mordomo-core-api:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 📦 Dependencies

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "zustand": "^4.4.7",
    "@tanstack/react-query": "^5.12.0",
    "recharts": "^2.10.0",
    "date-fns": "^2.30.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.1.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.8",
    "tailwindcss": "^3.3.6",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32"
  }
}
```

---

## 🎨 Theme (Dark Mode)

```typescript
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Aslam brand colors
        primary: {
          50: '#f0f9ff',
          500: '#0ea5e9',
          900: '#0c4a6e'
        },
        dark: {
          bg: '#0a0e27',
          surface: '#1a1f3a',
          border: '#2d3454'
        }
      }
    }
  }
}
```

---

## 📈 Métricas

```typescript
// Métricas do próprio Dashboard
dashboard_page_views_total{page}
dashboard_api_requests_total{endpoint,status}
dashboard_websocket_messages_total{type}
dashboard_user_actions_total{action}
```

---

## 🧪 Testes

```typescript
// __tests__/Dashboard.test.tsx
import { render, screen } from '@testing-library/react'
import Dashboard from '@/components/Dashboard'

test('renders dashboard with stats', async () => {
  render(<Dashboard />)
  
  expect(screen.getByText(/Status dos Serviços/i)).toBeInTheDocument()
  
  // Verifica serviços listados
  await screen.findByText(/Audio Capture/i)
  await screen.findByText(/Whisper ASR/i)
})

test('shows real-time conversations', async () => {
  const mockConversations = [
    { id: 1, user: 'Renan', text: 'Olá', timestamp: Date.now() }
  ]
  
  render(<Conversations data={mockConversations} />)
  
  expect(screen.getByText('Renan')).toBeInTheDocument()
  expect(screen.getByText('Olá')).toBeInTheDocument()
})
```

---

## 🔧 Troubleshooting

### WebSocket não conecta
```typescript
// Verificar URL
console.log('WebSocket URL:', import.meta.env.VITE_WS_URL)

// Testar manualmente
const ws = new WebSocket('ws://localhost:8000/ws/events')
ws.onopen = () => console.log('Connected!')
```

### API CORS error
```python
# No Core API (FastAPI)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🔗 Integração

**Consome:**
- Core API (REST - conversas, usuários, configurações)
- Core API (WebSocket - eventos em tempo real)
- Prometheus (métricas via API)
- Consul (lista de serviços da Infraestrutura)

**Acesso:**
- Web Browser: http://localhost:3000
- Mobile: Responsivo

---

## 🚀 Build & Deploy

```bash
# Desenvolvimento
npm run dev

# Build produção
npm run build

# Preview build
npm run preview

# Docker
docker build -t dashboard-ui .
docker run -p 3000:80 dashboard-ui
```

---

**Versão:** 1.0  
**Última atualização:** 27/11/2025  
**Designer:** Interface moderna dark mode inspirada no Aslam
