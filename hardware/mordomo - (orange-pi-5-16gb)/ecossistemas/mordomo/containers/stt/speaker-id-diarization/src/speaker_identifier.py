"""
Speaker Identification and Diarization core logic.
Combines pyannote.audio diarization with speaker recognition using embeddings.
"""

import os
import time
import hashlib
import numpy as np
import torch
import structlog
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Pyannote for diarization
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding

# Resemblyzer for embeddings (compatible with Speaker Verification)
from resemblyzer import VoiceEncoder

from .config import DiarizationConfig, RecognitionConfig, OverlapConfig
from .metrics import MetricsCollector

logger = structlog.get_logger(__name__)


@dataclass
class SpeakerSegment:
    """Individual speaker segment result."""
    speaker_id: str
    recognized: bool
    confidence: float
    text: str
    start_time: float
    end_time: float


@dataclass
class DiarizationResult:
    """Complete diarization result."""
    segments: List[SpeakerSegment]
    overlap_detected: bool
    processing_time: float


class SpeakerIdentifier:
    """
    Hybrid Speaker Identification:
    1. Diarization: Separate voices into segments
    2. Recognition: Identify each segment with enrolled embeddings
    """
    
    def __init__(
        self,
        diarization_config: DiarizationConfig,
        recognition_config: RecognitionConfig,
        overlap_config: OverlapConfig
    ):
        self.diarization_config = diarization_config
        self.recognition_config = recognition_config
        self.overlap_config = overlap_config
        
        # Initialize encoder (same as Speaker Verification for compatibility)
        self.encoder = VoiceEncoder()
        logger.info("voice_encoder_initialized", device="cpu")
        
        # Load diarization pipeline
        self._load_diarization_pipeline()
        
        # Load enrolled embeddings from database
        self.enrolled_embeddings: Dict[str, np.ndarray] = {}
        self._load_enrolled_embeddings()
        
        # Update metrics
        MetricsCollector.set_enrolled_speakers(len(self.enrolled_embeddings))
    
    def _load_diarization_pipeline(self):
        """Load pyannote diarization pipeline."""
        try:
            # Note: Requires HuggingFace token for pyannote models
            # Set via: export HUGGINGFACE_TOKEN=your_token
            self.diarization_pipeline = Pipeline.from_pretrained(
                self.diarization_config.model,
                use_auth_token=os.getenv("HUGGINGFACE_TOKEN")
            )
            
            logger.info(
                "diarization_pipeline_loaded",
                model=self.diarization_config.model
            )
            
        except Exception as e:
            logger.error("failed_to_load_diarization_pipeline", error=str(e))
            # Fallback: disable diarization, use only recognition
            self.diarization_pipeline = None
    
    def _load_enrolled_embeddings(self):
        """Load all enrolled speaker embeddings from database."""
        embeddings_path = Path(self.recognition_config.embeddings_path)
        
        if not embeddings_path.exists():
            logger.warning(
                "embeddings_directory_not_found",
                path=str(embeddings_path)
            )
            return
        
        # Load all .npy files
        for embedding_file in embeddings_path.glob("*.npy"):
            try:
                user_id = embedding_file.stem  # e.g., "user_1" from "user_1.npy"
                embedding = np.load(embedding_file)
                
                self.enrolled_embeddings[user_id] = embedding
                
                logger.info(
                    "embedding_loaded",
                    user_id=user_id,
                    shape=embedding.shape
                )
                
            except Exception as e:
                logger.error(
                    "failed_to_load_embedding",
                    file=str(embedding_file),
                    error=str(e)
                )
        
        logger.info(
            "enrolled_embeddings_loaded",
            total=len(self.enrolled_embeddings),
            users=list(self.enrolled_embeddings.keys())
        )
    
    def reload_embeddings(self):
        """Hot reload embeddings (called by watchdog)."""
        logger.info("reloading_embeddings")
        self.enrolled_embeddings.clear()
        self._load_enrolled_embeddings()
        MetricsCollector.set_enrolled_speakers(len(self.enrolled_embeddings))
    
    async def identify_and_diarize(
        self,
        audio: np.ndarray,
        transcript: str,
        conversation_id: str
    ) -> DiarizationResult:
        """
        Main processing pipeline:
        1. Diarize audio (separate speakers)
        2. Recognize each speaker (compare with enrolled embeddings)
        3. Return identified segments
        """
        start_time = time.time()
        
        try:
            # If no diarization pipeline, treat as single speaker
            if self.diarization_pipeline is None:
                return await self._recognize_single_speaker(
                    audio, transcript, conversation_id
                )
            
            # 1. DIARIZATION: Separate voices
            diarization_output = self.diarization_pipeline({
                "waveform": torch.from_numpy(audio).unsqueeze(0),
                "sample_rate": 16000
            })
            
            # 2. RECOGNITION: Identify each segment
            segments = []
            overlap_detected = False
            
            for turn, _, speaker_label in diarization_output.itertracks(yield_label=True):
                start = turn.start
                end = turn.end
                
                # Extract audio segment
                start_sample = int(start * 16000)
                end_sample = int(end * 16000)
                audio_segment = audio[start_sample:end_sample]
                
                # Skip segments too short
                if end - start < self.diarization_config.min_speaker_duration:
                    continue
                
                # Create embedding for this segment
                segment_embedding = self.encoder.embed_utterance(audio_segment)
                
                # Compare with enrolled embeddings
                speaker_id, confidence, recognized = self._recognize_speaker(
                    segment_embedding
                )
                
                # Extract corresponding text (simple time-based split)
                segment_text = self._extract_text_segment(transcript, start, end)
                
                segment = SpeakerSegment(
                    speaker_id=speaker_id,
                    recognized=recognized,
                    confidence=confidence,
                    text=segment_text,
                    start_time=start,
                    end_time=end
                )
                segments.append(segment)
                
                # Record metrics
                MetricsCollector.record_identification(
                    speaker_id, recognized, confidence
                )
            
            # Check for overlap
            if self.overlap_config.detection_enabled:
                overlap_detected = self._detect_overlap(segments)
                if overlap_detected:
                    MetricsCollector.record_overlap()
            
            processing_time = time.time() - start_time
            
            logger.info(
                "diarization_completed",
                conversation_id=conversation_id,
                segments=len(segments),
                overlap=overlap_detected,
                processing_time=f"{processing_time:.3f}s"
            )
            
            return DiarizationResult(
                segments=segments,
                overlap_detected=overlap_detected,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(
                "diarization_failed",
                error=str(e),
                conversation_id=conversation_id
            )
            
            # Fallback: single speaker recognition
            return await self._recognize_single_speaker(
                audio, transcript, conversation_id
            )
    
    async def _recognize_single_speaker(
        self,
        audio: np.ndarray,
        transcript: str,
        conversation_id: str
    ) -> DiarizationResult:
        """Fallback: Recognize single speaker without diarization."""
        start_time = time.time()
        
        try:
            # Create embedding for entire audio
            embedding = self.encoder.embed_utterance(audio)
            
            # Recognize speaker
            speaker_id, confidence, recognized = self._recognize_speaker(embedding)
            
            segment = SpeakerSegment(
                speaker_id=speaker_id,
                recognized=recognized,
                confidence=confidence,
                text=transcript,
                start_time=0.0,
                end_time=len(audio) / 16000.0
            )
            
            processing_time = time.time() - start_time
            
            MetricsCollector.record_identification(speaker_id, recognized, confidence)
            
            logger.info(
                "single_speaker_recognized",
                conversation_id=conversation_id,
                speaker_id=speaker_id,
                confidence=confidence,
                recognized=recognized
            )
            
            return DiarizationResult(
                segments=[segment],
                overlap_detected=False,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error("single_speaker_recognition_failed", error=str(e))
            raise
    
    def _recognize_speaker(
        self,
        embedding: np.ndarray
    ) -> Tuple[str, float, bool]:
        """
        Compare embedding with enrolled speakers.
        Returns: (speaker_id, confidence, recognized)
        """
        if not self.enrolled_embeddings:
            # No enrolled speakers
            unknown_id = self._generate_unknown_id(embedding)
            return unknown_id, 0.0, False
        
        # Calculate cosine similarity with all enrolled embeddings
        similarities = {}
        for user_id, enrolled_embedding in self.enrolled_embeddings.items():
            similarity = self._cosine_similarity(embedding, enrolled_embedding)
            similarities[user_id] = similarity
        
        # Find best match
        best_user_id = max(similarities, key=similarities.get)
        best_confidence = similarities[best_user_id]
        
        # Check threshold
        if best_confidence >= self.recognition_config.threshold:
            # Recognized
            return best_user_id, best_confidence, True
        else:
            # Unknown (below threshold)
            unknown_id = self._generate_unknown_id(embedding)
            return unknown_id, best_confidence, False
    
    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings."""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    @staticmethod
    def _generate_unknown_id(embedding: np.ndarray) -> str:
        """Generate unique ID for unknown speaker based on embedding hash."""
        embedding_bytes = embedding.tobytes()
        hash_obj = hashlib.sha256(embedding_bytes)
        hash_hex = hash_obj.hexdigest()[:8]
        return f"unknown_{hash_hex}"
    
    @staticmethod
    def _extract_text_segment(transcript: str, start: float, end: float) -> str:
        """
        Simple text extraction based on time proportions.
        TODO: Improve with word-level timestamps from Whisper ASR.
        """
        # Placeholder: return full transcript for now
        # In production, use word timestamps from Whisper
        return transcript
    
    def _detect_overlap(self, segments: List[SpeakerSegment]) -> bool:
        """Detect if any segments overlap in time."""
        for i, seg1 in enumerate(segments):
            for seg2 in segments[i+1:]:
                # Check temporal overlap
                overlap_start = max(seg1.start_time, seg2.start_time)
                overlap_end = min(seg1.end_time, seg2.end_time)
                overlap_duration = overlap_end - overlap_start
                
                if overlap_duration > self.overlap_config.min_duration:
                    logger.info(
                        "overlap_detected",
                        speaker1=seg1.speaker_id,
                        speaker2=seg2.speaker_id,
                        duration=f"{overlap_duration:.2f}s"
                    )
                    return True
        
        return False
