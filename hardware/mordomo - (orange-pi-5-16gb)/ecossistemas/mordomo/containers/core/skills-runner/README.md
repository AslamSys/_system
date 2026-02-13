# Mordomo Skills Runner (Nível 1)

> **Status:** Especificação Técnica (Em Planejamento)  
> **Responsabilidade:** Execução tática de scripts Python efêmeros.

O **Skills Runner** é um microserviço projetado para dar "braços" ao Mordomo. Ele permite que o Orquestrador (ou a IA) gere código Python dinâmico para resolver tarefas imediatas (ex: consultar uma API desconhecida, processar um texto, fazer um cálculo matemático complexo) e execute esse código em um ambiente seguro e isolado.

---

## 1. Arquitetura e Responsabilidades

Este container atua como um **Worker** passivo. Ele não toma decisões; apenas executa o que lhe é mandado e devolve o resultado.

### Diferenciação de Níveis
*   **Nível 1 (Este Módulo):** Execuções rápidas (< 30s), scripts simples, bibliotecas padrão ou populares (requests, pandas). Foco em agilidade para o assistente de voz.
*   **Nível 2 (Módulo RPA - Futuro):** Projetos complexos, scraping pesado, automação de browser, longa duração. (Fora do escopo deste documento).

### Componentes Internos
1.  **NATS Listener:** Escuta pedidos de execução.
2.  **Environment Manager:** Gerencia ambientes virtuais (venvs) sob demanda.
3.  **Execution Sandbox:** Roda o código em subprocessos isolados com timeout.
4.  **Garbage Collector:** Limpa ambientes virtuais não utilizados para economizar disco.

---

## 2. Protocolo de Comunicação (NATS)

O serviço deve se inscrever no tópico: `mordomo.skills.exec` (Queue Group: `skills_workers`).

### 2.1. Payload de Requisição (Request)

```json
{
  "request_id": "uuid-v4-unico",
  "code": "import requests\nresp = requests.get('https://api.exemplo.com')\nprint(resp.json()['valor'])",
  "requirements": [
    "requests==2.31.0",
    "pandas"
  ],
  "timeout": 30,
  "env_vars": {
    "API_KEY": "opcional-para-o-script"
  }
}
```

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `code` | string | O código Python completo a ser executado. |
| `requirements` | list | Lista de bibliotecas necessárias (formato `pip`). |
| `timeout` | int | Tempo máximo em segundos (Default: 10s, Max: 60s). |
| `env_vars` | dict | Variáveis de ambiente injetadas apenas para essa execução. |

### 2.2. Payload de Resposta (Response)

```json
{
  "request_id": "uuid-v4-unico",
  "success": true,
  "exit_code": 0,
  "stdout": "150.50\n",
  "stderr": "",
  "execution_time": 1.24,
  "error": null
}
```

---

## 3. Estratégia de Ambientes (Venv Cache)

Para evitar a latência de rodar `pip install` a cada execução, utilizaremos um sistema de cache baseado em hash.

### Algoritmo de Gestão de Venvs
1.  **Normalização:** Recebe a lista `requirements`, ordena alfabeticamente e remove espaços.
2.  **Hashing:** Gera um hash MD5/SHA256 da string normalizada. Ex: `requests==2.31.0|pandas` -> `a1b2c3d4...`.
3.  **Verificação:**
    *   Checa se o diretório `/app/envs/a1b2c3d4...` existe e tem um arquivo marcador `READY`.
4.  **Criação (Cache Miss):**
    *   Se não existir, cria o venv: `python -m venv /app/envs/a1b2c3d4...`.
    *   Instala libs: `/app/envs/.../bin/pip install requests pandas`.
    *   Cria o arquivo `READY`.
5.  **Execução (Cache Hit):**
    *   Usa o interpretador `/app/envs/a1b2c3d4.../bin/python` para rodar o script.

### "Batteries Included" (Base Image)
Para maximizar a performance, a imagem Docker base deve vir com as bibliotecas mais comuns pré-instaladas no ambiente **global** ou em um venv padrão. Se o `requirements` estiver vazio, usa-se o ambiente global.
*   **Libs Sugeridas:** `requests`, `numpy`, `pandas`, `beautifulsoup4`, `pytz`, `python-dateutil`.

---

## 4. Segurança e Isolamento

Como estaremos executando código gerado por IA (que pode alucinar) ou externo, a segurança é crítica.

1.  **Subprocessos:** Nunca usar `exec()` ou `eval()` dentro do processo principal do Runner. Sempre spawnar um novo processo.
2.  **Timeouts Rígidos:** O `subprocess.run` deve ter o parâmetro `timeout` configurado. Se estourar, o processo deve ser morto (`SIGKILL`).
3.  **Usuário sem Privilégios:** O container deve rodar com um usuário não-root (ex: `appuser`).
4.  **Rede:**
    *   O container precisa de internet para instalar pacotes e acessar APIs externas.
    *   **Risco:** O script pode tentar acessar a rede interna (ex: atacar o banco de dados).
    *   **Mitigação:** Se possível, usar regras de firewall do Docker para permitir saída apenas para a internet (0.0.0.0/0) e bloquear faixas de IP locais (192.168.x.x), exceto o NATS.
5.  **Sistema de Arquivos:** O script deve rodar em um diretório temporário (`/tmp/exec_xyz`) que é apagado após a execução.

---

## 5. Guia de Implementação

### Estrutura de Pastas Sugerida
```
skills-runner/
├── Dockerfile            # Python 3.11-slim, user non-root
├── requirements.txt      # Libs do Runner (nats-py) + Libs "Batteries Included"
├── src/
│   ├── main.py           # Entrypoint, conexão NATS
│   ├── executor.py       # Lógica de subprocess e timeout
│   └── venv_manager.py   # Lógica de hash e criação de venvs
└── envs/                 # Volume montado para persistir venvs criados
```

### Pseudocódigo: `venv_manager.py`
```python
def get_python_path(requirements):
    if not requirements:
        return "/usr/local/bin/python" # Global
    
    req_hash = calculate_hash(requirements)
    venv_path = f"/app/envs/{req_hash}"
    
    if not is_ready(venv_path):
        create_venv(venv_path)
        install_packages(venv_path, requirements)
        mark_ready(venv_path)
        
    return f"{venv_path}/bin/python"
```

### Pseudocódigo: `executor.py`
```python
def run_script(code, python_path, timeout):
    # Escreve código em arquivo temporário
    filename = f"/tmp/{uuid.uuid4()}.py"
    with open(filename, 'w') as f:
        f.write(code)
        
    try:
        result = subprocess.run(
            [python_path, filename],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return "", "Timeout Exceeded"
    finally:
        os.remove(filename)
```

---

## 6. Manutenção (Garbage Collection)
Um script cron ou thread secundária deve rodar periodicamente (ex: a cada 24h) para deletar pastas em `/app/envs/` que não foram acessadas nos últimos 7 dias, evitando que o disco do Orange Pi encha com bibliotecas obsoletas.
