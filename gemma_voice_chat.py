# Simple Voice Chat with Gemma using Pipecat

import asyncio
import os
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.ollama.llm import OLLamaLLMService
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams

async def main():
    # Local audio (microphone + speakers)
    transport = LocalAudioTransport(
        LocalAudioTransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.3)),
        )
    )

    # Speech-to-text (requires Deepgram API key)
    # Get free key: https://deepgram.com
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY", "YOUR_KEY_HERE"))

    # Your Gemma model via Ollama
    llm = OLLamaLLMService(model="gemma-arabic")

    # Text-to-speech (requires Cartesia API key)
    # Get free key: https://cartesia.ai
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY", "YOUR_KEY_HERE"),
        voice_id="71a7ad14-091c-4e8e-a314-022ece01c121",  # British Lady
    )

    # Context for conversation
    context = LLMContext([
        {"role": "system", "content": "You are a helpful assistant that can speak multiple languages."}
    ])
    context_aggregator = LLMContextAggregatorPair(context)

    # Build pipeline
    pipeline = Pipeline([
        transport.input(),
        stt,
        context_aggregator.user(),
        llm,
        tts,
        transport.output(),
        context_aggregator.assistant(),
    ])

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
            enable_metrics=False,
        ),
    )

    # Run
    runner = PipelineRunner()
    await runner.run(task)

if __name__ == "__main__":
    print("🎤 Starting voice chat with Gemma...")
    print("🔑 Make sure to set DEEPGRAM_API_KEY and CARTESIA_API_KEY environment variables")
    print("💬 Speak into your microphone!")
    asyncio.run(main())
