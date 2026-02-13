"""
Audio Capture + VAD - Core Implementation
"""

import logging
import time
import numpy as np
import sounddevice as sd
import webrtcvad
import zmq
from threading import Event

logger = logging.getLogger(__name__)


class AudioCaptureVAD:
    """
    Captura áudio do microfone continuamente, aplica VAD e publica via ZeroMQ.
    """
    
    def __init__(self, config):
        """
        Inicializa o capturador de áudio.
        
        Args:
            config: Dicionário com configurações
        """
        self.config = config
        self.running = Event()
        
        # Configurações de áudio
        audio_cfg = config['audio']
        self.sample_rate = audio_cfg['capture']['sample_rate']
        self.channels = audio_cfg['capture']['channels']
        self.frames_per_buffer = audio_cfg['capture']['frames_per_buffer']
        self.device_index = audio_cfg['device']['index']
        
        # Configurações de VAD
        vad_cfg = audio_cfg['vad']
        self.vad_mode = vad_cfg['mode']
        self.frame_duration_ms = vad_cfg['frame_duration_ms']
        
        # AGC (Auto Gain Control) - amplificação de software
        self.agc_enabled = config.get('processing', {}).get('agc', {}).get('enabled', True)
        self.agc_target = config.get('processing', {}).get('agc', {}).get('target_level', 3.0)
        self.current_gain = 1.0  # Ganho inicial
        
        # Inicializar VAD
        self.vad = webrtcvad.Vad(self.vad_mode)
        logger.info(f"VAD inicializado com modo {self.vad_mode}")
        if self.agc_enabled:
            logger.info(f"AGC habilitado (target: {self.agc_target}x)")
        
        # Configurações de output
        output_cfg = config['output']
        self.console_enabled = output_cfg.get('console', {}).get('enabled', False)
        self.zmq_enabled = output_cfg.get('zeromq', {}).get('enabled', False)
        
        # Inicializar ZeroMQ (se habilitado)
        self.zmq_publisher = None
        if self.zmq_enabled:
            self._init_zeromq(output_cfg['zeromq'])
        
        # Estatísticas
        self.stats = {
            'frames_total': 0,
            'frames_voice': 0,
            'frames_silence': 0,
            'start_time': None
        }
        
        logger.info(f"Audio Capture configurado:")
        logger.info(f"  Sample Rate: {self.sample_rate} Hz")
        logger.info(f"  Channels: {self.channels}")
        logger.info(f"  Frame Size: {self.frames_per_buffer} samples ({self.frame_duration_ms}ms)")
        logger.info(f"  Device Index: {self.device_index if self.device_index is not None else 'default'}")
    
    def _init_zeromq(self, zmq_cfg):
        """Inicializa publisher ZeroMQ"""
        context = zmq.Context()
        self.zmq_publisher = context.socket(zmq.PUB)
        endpoint = zmq_cfg['endpoint']
        self.zmq_publisher.bind(endpoint)
        self.zmq_topic = zmq_cfg['topic'].encode('utf-8')
        logger.info(f"ZeroMQ Publisher iniciado em {endpoint}")
    
    def _audio_callback(self, indata, frames, time_info, status):
        """
        Callback chamado quando há dados de áudio disponíveis.
        
        Args:
            indata: Array numpy com os dados de áudio
            frames: Número de frames
            time_info: Informações de timing
            status: Status flags
        """
        if status:
            logger.warning(f"Status do callback: {status}")
        
        # Aplicar AGC (Auto Gain Control) se habilitado
        if self.agc_enabled:
            # Calcular RMS do áudio original
            rms_original = np.sqrt(np.mean((indata * 32767) ** 2))
            
            # Ajustar ganho automaticamente (suavizado)
            if rms_original > 50:  # Só ajustar se houver sinal
                target_rms = 1000 * self.agc_target  # Target RMS para boa detecção
                desired_gain = target_rms / (rms_original + 1e-6)
                # Limitar ganho entre 1x e 10x
                desired_gain = np.clip(desired_gain, 1.0, 10.0)
                # Suavizar mudanças de ganho (evitar saltos)
                self.current_gain = 0.9 * self.current_gain + 0.1 * desired_gain
            
            # Aplicar ganho
            indata = indata * self.current_gain
            # Clipar para evitar distorção
            indata = np.clip(indata, -1.0, 1.0)
        
        # Converter para int16 (formato esperado pelo VAD)
        audio_data = (indata * 32767).astype(np.int16)
        
        # Calcular energia RMS DEPOIS do AGC (para mostrar o nível processado)
        rms = np.sqrt(np.mean(audio_data.astype(float) ** 2))
        energy_normalized = rms / 32767.0
        
        audio_bytes = audio_data.tobytes()
        
        # Aplicar VAD
        try:
            is_speech = self.vad.is_speech(audio_bytes, self.sample_rate)
        except Exception as e:
            logger.error(f"Erro no VAD: {e}")
            is_speech = False
            
        # Se energia muito baixa, forçar como silêncio (threshold adicional)
        if energy_normalized < 0.01:  # < 1% de energia
            is_speech = False
        
        # Atualizar estatísticas
        self.stats['frames_total'] += 1
        if is_speech:
            self.stats['frames_voice'] += 1
        else:
            self.stats['frames_silence'] += 1
        
        # Publicar apenas se detectou voz
        if is_speech:
            # Console output (se habilitado)
            if self.console_enabled:
                bars = int(energy_normalized * 50)
                bar_str = '█' * bars + '░' * (50 - bars)
                gain_indicator = f" 🔊x{self.current_gain:.1f}" if self.agc_enabled and self.current_gain > 1.5 else ""
                print(f"\r🎤 VOZ: [{bar_str}] {energy_normalized:.3f} (RMS: {rms:.0f}){gain_indicator}", end='', flush=True)
            
            # ZeroMQ output (se habilitado)
            if self.zmq_enabled and self.zmq_publisher:
                # Criar payload
                payload = {
                    'timestamp': time.time(),
                    'sample_rate': self.sample_rate,
                    'channels': self.channels,
                    'format': 'int16',
                    'energy': float(energy_normalized),
                    'sequence': self.stats['frames_voice']
                }
                
                # Enviar (topic + metadata + audio data)
                try:
                    self.zmq_publisher.send_multipart([
                        self.zmq_topic,
                        str(payload).encode('utf-8'),
                        audio_bytes
                    ])
                except Exception as e:
                    logger.error(f"Erro ao publicar no ZeroMQ: {e}")
        else:
            # Mostrar silêncio no console (se habilitado)
            if self.console_enabled:
                # Atualizar a cada 10 frames para não poluir
                if self.stats['frames_total'] % 10 == 0:
                    # Mostrar energia mesmo em silêncio para debug
                    print(f"\r🔇 Silêncio... (energia: {energy_normalized:.4f}, RMS: {rms:.0f}) - {self.stats['frames_silence']} frames", end='', flush=True)
    
    def start(self):
        """Inicia a captura de áudio"""
        self.running.set()
        self.stats['start_time'] = time.time()
        
        logger.info("Iniciando stream de áudio...")
        
        try:
            with sd.InputStream(
                device=self.device_index,
                channels=self.channels,
                samplerate=self.sample_rate,
                blocksize=self.frames_per_buffer,
                callback=self._audio_callback,
                dtype=np.float32
            ):
                logger.info("✅ Stream de áudio ativo. Capturando...")
                
                # Manter rodando até Ctrl+C
                while self.running.is_set():
                    time.sleep(0.1)
                    
                    # Mostrar estatísticas a cada 10 segundos
                    if int(time.time()) % 10 == 0:
                        self._print_stats()
        
        except Exception as e:
            logger.error(f"Erro no stream de áudio: {e}", exc_info=True)
            raise
        finally:
            self.stop()
    
    def stop(self):
        """Para a captura de áudio"""
        logger.info("Parando captura de áudio...")
        self.running.clear()
        
        if self.zmq_publisher:
            self.zmq_publisher.close()
        
        self._print_stats()
    
    def _print_stats(self):
        """Imprime estatísticas de captura"""
        if self.stats['start_time'] is None:
            return
        
        elapsed = time.time() - self.stats['start_time']
        total = self.stats['frames_total']
        voice = self.stats['frames_voice']
        silence = self.stats['frames_silence']
        
        if total > 0:
            voice_pct = (voice / total) * 100
            silence_pct = (silence / total) * 100
            
            logger.info("")
            logger.info(f"📊 Estatísticas ({elapsed:.1f}s):")
            logger.info(f"   Total frames: {total}")
            logger.info(f"   Voz: {voice} ({voice_pct:.1f}%)")
            logger.info(f"   Silêncio: {silence} ({silence_pct:.1f}%)")
