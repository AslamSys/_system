"""
Azure TTS Engine com todas as vozes PT-BR disponíveis
"""
import io
from typing import Optional
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, ResultReason
from config import settings

class AzureTTSEngine:
    """Azure Cognitive Services TTS Engine"""
    
    # Todas as vozes PT-BR disponíveis (18 vozes)
    VOZES_DISPONIVEIS = {
        # Masculinas (8 vozes)
        "masculino": {
            "donato": "pt-BR-DonatoNeural",          # PADRÃO MASCULINO (291ms)
            "valerio": "pt-BR-ValerioNeural",        # 297ms
            "humberto": "pt-BR-HumbertoNeural",      # 305ms
            "antonio": "pt-BR-AntonioNeural",        # 255-1512ms (variável)
            "fabio": "pt-BR-FabioNeural",            # 287-1870ms (variável)
            "julio": "pt-BR-JulioNeural",            # 2331ms (lento)
            "nicolau": "pt-BR-NicolauNeural",        # 1076ms
            "macerio": "pt-BR-MacerioMultilingualNeural",  # 1056ms (multilíngue)
        },
        # Femininas (10 vozes)
        "feminino": {
            "thalita": "pt-BR-ThalitaNeural",        # PADRÃO FEMININO (788ms)
            "francisca": "pt-BR-FranciscaNeural",    # 212ms (mais rápida)
            "yara": "pt-BR-YaraNeural",              # 253ms
            "leticia": "pt-BR-LeticiaNeural",        # 353ms
            "leila": "pt-BR-LeilaNeural",            # 354ms
            "giovanna": "pt-BR-GiovannaNeural",      # 384ms
            "elza": "pt-BR-ElzaNeural",              # 441ms
            "manuela": "pt-BR-ManuelaNeural",        # 451ms
            "brenda": "pt-BR-BrendaNeural",          # 1619ms
            "thalita_multi": "pt-BR-ThalitaMultilingualNeural",  # 898ms (multilíngue)
        }
    }
    
    # Padrões
    VOZ_PADRAO = "pt-BR-DonatoNeural"  # Masculino Donato
    VOZ_FEMININA_PADRAO = "pt-BR-ThalitaNeural"
    
    def __init__(self):
        """Inicializa Azure TTS Engine"""
        if not settings.azure_speech_key1:
            raise ValueError("azure_speech_key1 não configurada no .env")
        
        self.speech_config = SpeechConfig(
            subscription=settings.azure_speech_key1,
            region=settings.azure_speech_region
        )
        self.speech_config.speech_synthesis_voice_name = self.VOZ_PADRAO
    
    def get_voz(self, genero: Optional[str] = None, nome_voz: Optional[str] = None) -> str:
        """
        Retorna o identificador da voz Azure
        
        Args:
            genero: "masculino" ou "feminino" (opcional)
            nome_voz: nome específico da voz como "donato", "francisca" (opcional)
        
        Returns:
            Identificador Azure da voz (ex: "pt-BR-DonatoNeural")
        """
        if nome_voz:
            # Buscar voz específica
            for gen, vozes in self.VOZES_DISPONIVEIS.items():
                if nome_voz.lower() in vozes:
                    return vozes[nome_voz.lower()]
        
        if genero == "feminino":
            return self.VOZ_FEMININA_PADRAO
        
        return self.VOZ_PADRAO
    
    async def synthesize_stream(
        self, 
        text: str, 
        genero: Optional[str] = None,
        nome_voz: Optional[str] = None
    ):
        """
        Sintetiza texto para áudio em streaming (memória)
        
        Args:
            text: Texto para sintetizar
            genero: "masculino" ou "feminino"
            nome_voz: Nome específico da voz
            
        Yields:
            Chunks de áudio em bytes
        """
        # Configurar voz
        voz = self.get_voz(genero, nome_voz)
        self.speech_config.speech_synthesis_voice_name = voz
        
        # Sintetizar em memória
        synthesizer = SpeechSynthesizer(
            speech_config=self.speech_config,
            audio_config=None
        )
        
        result = synthesizer.speak_text_async(text).get()
        
        if result.reason == ResultReason.SynthesizingAudioCompleted:
            # Retornar áudio como stream
            audio_data = result.audio_data
            chunk_size = 4096
            
            for i in range(0, len(audio_data), chunk_size):
                yield audio_data[i:i + chunk_size]
        else:
            raise Exception(f"Falha na síntese: {result.reason}")
    
    async def synthesize(
        self,
        text: str,
        genero: Optional[str] = None,
        nome_voz: Optional[str] = None
    ) -> bytes:
        """
        Sintetiza texto completo e retorna áudio
        
        Args:
            text: Texto para sintetizar
            genero: "masculino" ou "feminino"
            nome_voz: Nome específico da voz
            
        Returns:
            Áudio completo em bytes
        """
        chunks = []
        async for chunk in self.synthesize_stream(text, genero, nome_voz):
            chunks.append(chunk)
        return b''.join(chunks)
