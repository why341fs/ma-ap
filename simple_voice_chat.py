# Simple Real-Time Voice Chat with Gemma

import asyncio
import requests
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_response import (
    LLMAssistantResponseAggregator,
    LLMUserResponseAggregator,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.frames.frames import Frame, LLMMessagesFrame, TextFrame
from pipecat.services.elevenlabs import ElevenLabsTTSService
from pipecat.services.deepgram import DeepgramSTTService
from pipecat.transports.local.audio import LocalAudioTransport

import os
import json

# Ollama Integration
class OllamaProcessor(FrameProcessor):
    def __init__(self, model="gemma-arabic"):
        super().__init__()
        self.model = model
        self.messages = []
        
    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        
        if isinstance(frame, LLMMessagesFrame):
            self.messages = frame.messages
            
            # Stream response from Ollama
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": self.model,
                    "messages": self.messages,
                    "stream": True
                },
                stream=True
            )
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "message" in data:
                        content = data["message"]["content"]
                        if content:
                            # Send text to TTS
                            await self.push_frame(TextFrame(content))
        else:
            await self.push_frame(frame, direction)

async def main():
    # Setup services
    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY", "your-key-here")
    )
    
    llm = OllamaProcessor(model="gemma-arabic")
    
    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY", "your-key-here"),
        voice_id="21m00Tcm4TlvDq8ikWAM"  # Default voice
    )
    
    # Local audio transport (mic + speaker)
    transport = LocalAudioTransport(
        sample_rate=16000,
        channels=1
    )
    
    # Build pipeline
    pipeline = Pipeline([
        transport.input(),
        stt,
        LLMUserResponseAggregator(),
        llm,
        tts,
        transport.output(),
    ])
    
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
            enable_metrics=True,
        ),
    )
    
    # Run
    runner = PipelineRunner()
    await runner.run(task)

if __name__ == "__main__":
    print("🎤 Starting voice chat with Gemma...")
    print("Speak into your microphone!")
    asyncio.run(main())
