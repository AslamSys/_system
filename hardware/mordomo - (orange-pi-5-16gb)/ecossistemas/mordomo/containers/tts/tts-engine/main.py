import asyncio
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Literal
import logging

from config import settings
from tts_engines.piper_engine import PiperTTSEngine
from tts_engines.azure_engine import AzureTTSEngine
from tts_engines.openai_engine import OpenAITTSEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TTS Engine", version="1.0.0")


class TTSRequest(BaseModel):
    text: str
    engine: Optional[Literal["piper", "coqui", "azure", "openai", "edge"]] = None
    streaming: bool = True


class LatencyTestResult(BaseModel):
    engine: str
    text_length: int
    total_time_ms: float
    first_chunk_time_ms: float
    audio_duration_ms: float
    realtime_factor: float
    success: bool
    error: Optional[str] = None


# Initialize TTS engines
tts_engines = {}


@app.on_event("startup")
async def startup_event():
    """Initialize TTS engines on startup"""
    logger.info("Initializing TTS engines...")
    
    # Initialize Piper (local)
    try:
        tts_engines["piper"] = PiperTTSEngine()
        logger.info("✅ Piper TTS initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Piper: {e}")
    
    # Initialize Azure (API)
    try:
        if settings.azure_speech_key1:
            tts_engines["azure"] = AzureTTSEngine()
            logger.info("✅ Azure TTS initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Azure: {e}")
    
    # Initialize OpenAI (API)
    try:
        if settings.openai_api_key:
            tts_engines["openai"] = OpenAITTSEngine()
            logger.info("✅ OpenAI TTS initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize OpenAI: {e}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "available_engines": list(tts_engines.keys()),
        "default_engine": settings.tts_engine
    }


@app.post("/synthesize")
async def synthesize(request: TTSRequest):
    """Synthesize text to speech"""
    engine_name = request.engine or settings.tts_engine
    
    if engine_name not in tts_engines:
        raise HTTPException(
            status_code=400,
            detail=f"Engine '{engine_name}' not available. Available: {list(tts_engines.keys())}"
        )
    
    engine = tts_engines[engine_name]
    
    try:
        if request.streaming:
            return StreamingResponse(
                engine.synthesize_stream(request.text),
                media_type="audio/pcm"
            )
        else:
            audio_data = await engine.synthesize(request.text)
            return StreamingResponse(
                iter([audio_data]),
                media_type="audio/pcm"
            )
    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/test-latency", response_model=LatencyTestResult)
async def test_latency(request: TTSRequest):
    """Test latency of a specific TTS engine"""
    engine_name = request.engine or settings.tts_engine
    
    if engine_name not in tts_engines:
        raise HTTPException(
            status_code=400,
            detail=f"Engine '{engine_name}' not available"
        )
    
    engine = tts_engines[engine_name]
    
    start_time = time.perf_counter()
    first_chunk_time = None
    total_bytes = 0
    
    try:
        async for chunk in engine.synthesize_stream(request.text):
            if first_chunk_time is None:
                first_chunk_time = time.perf_counter()
            total_bytes += len(chunk)
        
        end_time = time.perf_counter()
        
        # Calculate metrics
        total_time_ms = (end_time - start_time) * 1000
        first_chunk_ms = (first_chunk_time - start_time) * 1000 if first_chunk_time else total_time_ms
        
        # Calculate audio duration
        bytes_per_sample = settings.bit_depth // 8
        samples_per_channel = total_bytes // (bytes_per_sample * settings.channels)
        audio_duration_ms = (samples_per_channel / settings.sample_rate) * 1000
        
        # Realtime factor (lower is better, <1.0 means faster than realtime)
        realtime_factor = total_time_ms / audio_duration_ms if audio_duration_ms > 0 else 0
        
        return LatencyTestResult(
            engine=engine_name,
            text_length=len(request.text),
            total_time_ms=round(total_time_ms, 2),
            first_chunk_time_ms=round(first_chunk_ms, 2),
            audio_duration_ms=round(audio_duration_ms, 2),
            realtime_factor=round(realtime_factor, 3),
            success=True
        )
    
    except Exception as e:
        logger.error(f"Latency test failed: {e}")
        return LatencyTestResult(
            engine=engine_name,
            text_length=len(request.text),
            total_time_ms=0,
            first_chunk_time_ms=0,
            audio_duration_ms=0,
            realtime_factor=0,
            success=False,
            error=str(e)
        )


@app.post("/test-all-engines")
async def test_all_engines(text: str = "Olá, eu sou o assistente Aslam. Como posso ajudar você hoje?"):
    """Test latency of all available engines"""
    results = []
    
    for engine_name in tts_engines.keys():
        result = await test_latency(TTSRequest(text=text, engine=engine_name))
        results.append(result)
    
    return {
        "test_text": text,
        "results": results,
        "summary": {
            "fastest_engine": min(
                (r for r in results if r.success),
                key=lambda x: x.first_chunk_time_ms,
                default=None
            ).engine if any(r.success for r in results) else None,
            "best_realtime_factor": min(
                (r for r in results if r.success),
                key=lambda x: x.realtime_factor,
                default=None
            ).engine if any(r.success for r in results) else None
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
