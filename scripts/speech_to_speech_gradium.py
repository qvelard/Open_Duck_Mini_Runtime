# speech_to_speech_gradium.py
# Pipeline speech-to-speech avec API Gradium.ai : STT + TTS streaming/low-latency.
# Intègre pyannote-audio pour diarization si multi-speaker.
# Adaptation pour RPi5 : Input .wav de micro MEMS (ex. enregistrez avec 'arecord' sur RPi).
# Pour test sur PC : Uploadez un fichier .wav comme OSR_us_000_0010_8k.wav.
# Remarque utilisateur : Input est .wav de micro MEMS sur RPi5 ; test séparé sur PC avec fichier exemple.
# Nécessite pip install gradium et clé API Gradium.

import asyncio
import gradio as gr
from gradium import GradiumClient
from pyannote.audio import Pipeline  # Pour diarization
from torchaudio import load
from dotenv import load_dotenv
import os 
# Charger clé API depuis .env
load_dotenv()
GRADIUM_API_KEY = os.getenv("GRADIUM_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")    
# Configuration (remplacez par votre clé API Gradium)
client = GradiumClient(api_key=GRADIUM_API_KEY)

# Diarization pyannote (optionnel ; token HF)
HF_TOKEN = os.getenv("HF_TOKEN")
diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=HF_TOKEN)
    
async def stt_full(audio_data):
    # STT non-streaming (simulé via stream pour compatibilité)
    stream = await client.stt_stream(
        {"model_name": "default", "input_format": "pcm"},
        audio_gen(audio_data, chunk_size=1920)
    )
    full_text = ""
    async for msg in stream.iter_text():
        full_text += msg["text"]
    return full_text

def audio_gen(data, chunk_size):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

async def speech_to_speech(audio_path, use_diarization=False, voice_id="YTpq7expH9539ERJ", output_format="wav"):
    # Chargement audio (.wav de MEMS sur RPi ou test PC)
    waveform, sample_rate = load(audio_path)
    audio_data = waveform.squeeze().numpy().tobytes()
    
    if use_diarization:
        diarization = diarization_pipeline(audio_path)
        transcribed_text = ""
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            # Placeholder : STT sur segments (ajoutez extraction pour précision)
            segment_text = await stt_full(audio_data)  # Améliorez pour segments
            transcribed_text += f"{speaker}: {segment_text}\n"
    else:
        transcribed_text = await stt_full(audio_data)
    
    # Processing text (ex. ajoutez prefix ou traduction)
    processed_text = f"Processed: {transcribed_text}"
    
    # TTS via Gradium
    result = await client.tts(
        setup={"voice_id": voice_id, "output_format": output_format},
        text=processed_text
    )
    return result.raw_data  # Bytes pour output Gradio

# Interface Gradio
async def gradio_fn(audio):
    output_bytes = await speech_to_speech(audio)
    return output_bytes

demo = gr.Interface(
    fn=lambda audio: asyncio.run(gradio_fn(audio)),
    inputs=gr.Audio(sources=["microphone", "upload"], type="filepath"),  # Micro pour RPi, upload pour test PC
    outputs=gr.Audio(label="Output Speech", type="numpy")
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0")  # Accessible réseau local