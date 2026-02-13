from litellm import completion
import os
from typing import Optional, Dict, Any

class LLMService:
    def __init__(self):
        # Configuração padrão: Tenta API primeiro, cai para local se falhar
        self.primary_model = os.getenv("LLM_PRIMARY_MODEL", "gpt-3.5-turbo")
        self.fallback_model = os.getenv("LLM_FALLBACK_MODEL", "ollama/qwen2.5:1.5b")
        self.api_key = os.getenv("OPENAI_API_KEY") # LiteLLM usa env vars padrão

    async def generate_response(self, messages: list[Dict[str, str]], context: Optional[Dict] = None) -> str:
        """
        Gera resposta usando LiteLLM com estratégia de fallback.
        """
        try:
            # Tenta modelo primário (Cloud)
            response = await self._call_model(self.primary_model, messages)
            return response
        except Exception as e:
            print(f"Erro no modelo primário ({self.primary_model}): {e}. Tentando fallback...")
            try:
                # Fallback para modelo local (Ollama)
                # LiteLLM suporta 'ollama/model-name' e conecta no localhost:11434 por padrão
                response = await self._call_model(self.fallback_model, messages)
                return response
            except Exception as fallback_error:
                print(f"Erro crítico no fallback ({self.fallback_model}): {fallback_error}")
                return "Desculpe, meus sistemas de inteligência estão indisponíveis no momento."

    async def _call_model(self, model: str, messages: list[Dict[str, str]]) -> str:
        # LiteLLM completion é síncrono por padrão, mas pode ser usado com async se configurado
        # Aqui estamos simplificando, num cenário real usaríamos a versão async do litellm ou run_in_executor
        response = completion(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
