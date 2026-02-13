"""Source separation service using Demucs."""

import base64
import io
import logging
from typing import List, Dict, Tuple, Optional
import time

import numpy as np
import soundfile as sf
import torch
from demucs.pretrained import get_model
from demucs.apply import apply_model

from .config import DemucsConfig, ProcessingConfig

logger = logging.getLogger(__name__)


class SeparatedChannel:
    """Represents a separated audio channel."""
    
    def __init__(self, audio: np.ndarray, speaker_id: str, confidence: float):
        self.audio = audio
        self.speaker_id = speaker_id
        self.confidence = confidence


class SourceSeparationService:
    """Service for separating overlapping voices using Demucs."""
    
    def __init__(self, demucs_config: DemucsConfig, processing_config: ProcessingConfig):
        """
        Initialize the source separation service.
        
        Args:
            demucs_config: Demucs model configuration
            processing_config: Audio processing configuration
        """
        self.demucs_config = demucs_config
        self.processing_config = processing_config
        self.model = None
        self._initialized = False
        
    def initialize(self):
        """Load Demucs model (lazy initialization for faster startup)."""
        if self._initialized:
            return
            
        logger.info(f"Loading Demucs model: {self.demucs_config.model}")
        start_time = time.time()
        
        try:
            self.model = get_model(self.demucs_config.model)
            
            # Move model to specified device
            device = torch.device(self.demucs_config.device)
            self.model.to(device)
            self.model.eval()
            
            self._initialized = True
            elapsed = time.time() - start_time
            logger.info(f"Demucs model loaded successfully in {elapsed:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to load Demucs model: {e}")
            raise
    
    def separate_audio(
        self, 
        audio_data: bytes, 
        sample_rate: int,
        speakers: List[str],
        duration: float
    ) -> List[SeparatedChannel]:
        """
        Separate overlapping voices from audio data.
        
        Args:
            audio_data: Raw audio bytes (PCM)
            sample_rate: Audio sample rate (Hz)
            speakers: List of speaker IDs detected in the audio
            duration: Audio duration in seconds
            
        Returns:
            List of SeparatedChannel objects, one per speaker
        """
        # Ensure model is loaded
        self.initialize()
        
        # Validate duration
        if duration > self.processing_config.max_duration:
            logger.warning(
                f"Audio duration {duration}s exceeds max {self.processing_config.max_duration}s"
            )
            raise ValueError(f"Audio too long: {duration}s")
        
        logger.info(f"Separating {duration}s audio with {len(speakers)} speakers")
        start_time = time.time()
        
        try:
            # Convert bytes to numpy array
            audio_array = self._decode_audio(audio_data, sample_rate)
            
            # Separate sources using Demucs
            separated = self._apply_demucs(audio_array, sample_rate)
            
            # Extract vocal tracks and assign to speakers
            channels = self._assign_speakers(separated, speakers, sample_rate)
            
            elapsed = time.time() - start_time
            logger.info(f"Separation completed in {elapsed:.2f}s")
            
            return channels
            
        except Exception as e:
            logger.error(f"Source separation failed: {e}")
            raise
    
    def _decode_audio(self, audio_data: bytes, sample_rate: int) -> np.ndarray:
        """
        Decode audio bytes to numpy array.
        
        Args:
            audio_data: Raw PCM audio bytes
            sample_rate: Sample rate in Hz
            
        Returns:
            Numpy array with shape (samples,) or (samples, channels)
        """
        # Assuming 16-bit PCM mono
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Normalize to [-1.0, 1.0]
        audio_array = audio_array.astype(np.float32) / 32768.0
        
        return audio_array
    
    def _apply_demucs(self, audio: np.ndarray, sample_rate: int) -> torch.Tensor:
        """
        Apply Demucs separation model to audio.
        
        Args:
            audio: Audio array
            sample_rate: Sample rate
            
        Returns:
            Separated sources tensor with shape (sources, channels, samples)
        """
        # Convert to torch tensor
        if len(audio.shape) == 1:
            # Mono to stereo (Demucs expects stereo)
            audio = np.stack([audio, audio], axis=0)
        else:
            audio = audio.T  # (channels, samples)
        
        wav = torch.from_numpy(audio).float().unsqueeze(0)  # (1, channels, samples)
        
        # Move to device
        device = torch.device(self.demucs_config.device)
        wav = wav.to(device)
        
        # Apply model
        with torch.no_grad():
            sources = apply_model(
                self.model,
                wav,
                shifts=self.demucs_config.shifts,
                overlap=self.demucs_config.overlap,
                split=True,
                device=device
            )
        
        # sources shape: (1, sources, channels, samples)
        # Remove batch dimension
        sources = sources[0]  # (sources, channels, samples)
        
        return sources
    
    def _assign_speakers(
        self, 
        separated: torch.Tensor, 
        speakers: List[str],
        sample_rate: int
    ) -> List[SeparatedChannel]:
        """
        Assign separated sources to speaker IDs.
        
        The htdemucs_ft model typically outputs 4 sources:
        - vocals
        - drums
        - bass
        - other
        
        We take the vocals source and separate it by energy/amplitude.
        
        Args:
            separated: Separated sources tensor (sources, channels, samples)
            speakers: List of speaker IDs
            sample_rate: Sample rate
            
        Returns:
            List of SeparatedChannel objects
        """
        # Extract vocals (usually index 0 for htdemucs_ft)
        vocals = separated[0].cpu().numpy()  # (channels, samples)
        
        # Convert stereo to mono
        if vocals.shape[0] == 2:
            vocals_mono = vocals.mean(axis=0)
        else:
            vocals_mono = vocals[0]
        
        # Simple separation: split audio in temporal chunks and assign by energy
        num_speakers = min(len(speakers), 3)  # Max 3 speakers as per spec
        channels = []
        
        if num_speakers == 1:
            # Single speaker - return all vocals
            confidence = 0.95
            channels.append(
                SeparatedChannel(
                    audio=vocals_mono,
                    speaker_id=speakers[0],
                    confidence=confidence
                )
            )
        else:
            # Multiple speakers - use energy-based separation
            # This is a simplified approach; more sophisticated methods could use:
            # - Clustering (k-means on MFCC features)
            # - Voice activity detection
            # - Directional audio analysis
            
            # Split into overlapping windows
            window_size = int(0.5 * sample_rate)  # 500ms windows
            hop_size = int(0.25 * sample_rate)  # 250ms hop
            
            segments = []
            energies = []
            
            for i in range(0, len(vocals_mono) - window_size, hop_size):
                segment = vocals_mono[i:i + window_size]
                energy = np.sqrt(np.mean(segment ** 2))  # RMS energy
                segments.append((i, segment))
                energies.append(energy)
            
            # Assign segments to speakers based on energy clusters
            if len(energies) > 0:
                energies_array = np.array(energies)
                # Simple threshold-based separation
                sorted_energies = np.sort(energies_array)
                
                # Assign top energy segments to first speaker, rest to second
                threshold = np.median(sorted_energies)
                
                speaker_audios = [np.zeros_like(vocals_mono) for _ in range(num_speakers)]
                
                for (start_idx, segment), energy in zip(segments, energies):
                    if num_speakers == 2:
                        speaker_idx = 0 if energy > threshold else 1
                    else:  # 3 speakers
                        if energy > sorted_energies[int(len(sorted_energies) * 0.67)]:
                            speaker_idx = 0
                        elif energy > sorted_energies[int(len(sorted_energies) * 0.33)]:
                            speaker_idx = 1
                        else:
                            speaker_idx = 2
                    
                    speaker_audios[speaker_idx][start_idx:start_idx + len(segment)] += segment
                
                # Create channels
                for i in range(num_speakers):
                    confidence = 0.75 - (i * 0.1)  # Decreasing confidence
                    channels.append(
                        SeparatedChannel(
                            audio=speaker_audios[i],
                            speaker_id=speakers[i] if i < len(speakers) else f"unknown_{i}",
                            confidence=confidence
                        )
                    )
        
        return channels
    
    def encode_audio(self, audio: np.ndarray, sample_rate: int = 16000) -> str:
        """
        Encode numpy audio array to base64 PCM.
        
        Args:
            audio: Audio array
            sample_rate: Sample rate
            
        Returns:
            Base64 encoded PCM string
        """
        # Convert to int16
        audio_int16 = (audio * 32768.0).astype(np.int16)
        
        # Convert to bytes
        audio_bytes = audio_int16.tobytes()
        
        # Encode to base64
        return base64.b64encode(audio_bytes).decode('utf-8')
