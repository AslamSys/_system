# 🎙️ Vozes Azure TTS - Português Brasil

Lista completa das **18 vozes** Azure Cognitive Services disponíveis para português brasileiro.

---

## 🎯 Vozes Recomendadas (Baixa Latência)

### 🔵 Masculinas Rápidas
| Voz | ID Azure | Latência Média | Qualidade |
|-----|----------|----------------|-----------|
| **Donato** ⭐ | `pt-BR-DonatoNeural` | 291ms | Excelente |
| **Valerio** | `pt-BR-ValerioNeural` | 297ms | Boa |
| **Humberto** | `pt-BR-HumbertoNeural` | 305ms | Boa |

### 🔴 Femininas Rápidas  
| Voz | ID Azure | Latência Média | Qualidade |
|-----|----------|----------------|-----------|
| **Francisca** ⭐ | `pt-BR-FranciscaNeural` | 556ms | Excelente |
| **Thalita** | `pt-BR-ThalitaNeural` | 270ms | Excelente |
| **Camila** | `pt-BR-CamilaNeural` | 329ms | Boa |

---

## 📋 Lista Completa por Gênero

### 👨 Masculinas (8 vozes)

```yaml
Rápidas (< 350ms):
  - donato: pt-BR-DonatoNeural          # 291ms ⭐ PADRÃO MASCULINO
  - valerio: pt-BR-ValerioNeural        # 297ms
  - humberto: pt-BR-HumbertoNeural      # 305ms

Variáveis (250-1800ms):
  - antonio: pt-BR-AntonioNeural        # 255-1512ms
  - fabio: pt-BR-FabioNeural            # 287-1870ms

Lentas (> 2s):
  - julio: pt-BR-JulioNeural            # 2331ms
  - leandro: pt-BR-LeandroNeural        # 1347ms
  - nicolau: pt-BR-NicolauNeural        # 1641ms
```

### 👩 Femininas (10 vozes)

```yaml
Rápidas (< 600ms):
  - thalita: pt-BR-ThalitaNeural        # 270ms ⭐ PADRÃO FEMININO  
  - camila: pt-BR-CamilaNeural          # 329ms
  - giovanna: pt-BR-GiovannaNeural      # 384ms
  - elza: pt-BR-ElzaNeural              # 441ms
  - manuela: pt-BR-ManuelaNeural        # 451ms
  - francisca: pt-BR-FranciscaNeural    # 556ms

Lentas (> 800ms):
  - thalita_multi: pt-BR-ThalitaMultilingualNeural    # 898ms (multilíngue)
  - brenda: pt-BR-BrendaNeural                        # 1619ms
  - lara: pt-BR-LaraNeural                           # 1173ms
  - yara: pt-BR-YaraNeural                           # 1982ms
```

---

## ⚙️ Configuração no TTS Engine

### Usando Voz Padrão
```python
# Não especificar nada = usar padrões
{
  "text": "Olá, como está?"
  # Vai usar: pt-BR-DonatoNeural (masculino padrão)
}
```

### Usando Gênero
```python
{
  "text": "Olá, como está?",
  "gender": "feminino"
  # Vai usar: pt-BR-ThalitaNeural (feminino padrão)
}
```

### Usando Voz Específica
```python
{
  "text": "Olá, como está?",
  "voice": "francisca"
  # Vai usar: pt-BR-FranciscaNeural
}
```

### Configuração .env
```bash
# Voz padrão Azure (masculina)
AZURE_VOICE_NAME=pt-BR-DonatoNeural

# Ou feminina
AZURE_VOICE_NAME=pt-BR-ThalitaNeural
```

---

## 🎵 Características das Vozes

### 🔵 Masculinas

**Donato (Recomendada):**
- ✅ Latência consistente (291ms)
- ✅ Tom natural e amigável
- ✅ Boa pronúncia de tecnologia

**Valerio:**
- ✅ Voz mais jovem
- ⚠️ Menos consistente em palavras técnicas

**Antonio/Fabio:**
- ⚠️ Latência muito variável (250ms-1800ms)
- 💡 Use apenas se aceitável esperar até 2s

### 🔴 Femininas

**Thalita (Recomendada):**
- ✅ Latência excelente (270ms)
- ✅ Tom profissional
- ✅ Melhor para assistente doméstico

**Francisca:**
- ✅ Voz calorosa e amigável
- ⚠️ Latência um pouco maior (556ms)

**ThalitaMultilingual:**
- ✅ Pronuncia bem palavras estrangeiras
- ⚠️ Latência alta (898ms)

---

## 💡 Recomendações de Uso

### Para Casa (Assistente Pessoal)
```yaml
Primária: pt-BR-ThalitaNeural      # Feminina, 270ms
Secundária: pt-BR-DonatoNeural     # Masculina, 291ms
```

### Para Negócios (Profissional)
```yaml
Primária: pt-BR-DonatoNeural       # Masculina formal, 291ms
Secundária: pt-BR-FranciscaNeural  # Feminina calorosa, 556ms
```

### Para Baixa Latência (< 350ms)
```yaml
Opção 1: pt-BR-ThalitaNeural       # 270ms
Opção 2: pt-BR-DonatoNeural        # 291ms
Opção 3: pt-BR-ValerioNeural       # 297ms
```

---

## 🔧 Implementação no TTS Engine

O arquivo `tts_engines/azure_engine.py` contém toda a lógica:

```python
# Padrões definidos
VOZ_PADRAO = "pt-BR-DonatoNeural"
VOZ_FEMININA_PADRAO = "pt-BR-ThalitaNeural"

# Mapeamento completo
VOZES_DISPONIVEIS = {
    "masculino": {...},
    "feminino": {...}
}
```

---

## 📊 Teste de Latência

Para testar todas as vozes:

```bash
curl -X POST "http://localhost:8007/test-latency" \
  -H "Content-Type: application/json" \
  -d '{"engine": "azure", "test_all_voices": true}'
```

**Resultado esperado:**
- Donato, Valerio, Humberto, Thalita: < 350ms ✅
- Francisca, Camila: 350-600ms ⚠️
- Demais: > 800ms ❌

---

**Atualizado:** 12/02/2026  
**Fonte:** Azure Cognitive Services PT-BR