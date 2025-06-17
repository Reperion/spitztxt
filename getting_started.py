import torch
import torchaudio
from chatterbox.tts import ChatterboxTTS

# --- Step 1: Load the Model ---
# This will download the model the first time you run it.
# It will use your GPU if you have one ("cuda") or your CPU.
print("Loading Chatterbox model...")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = ChatterboxTTS.from_pretrained(device=device)
print("Model loaded successfully!")


# --- Step 2: Define the Text ---
# The text you want to convert to speech.
text_to_speak = "Hello there fellow earthlings. " \
"My congratulations on being replaced by artifical intelligence. " \
"We are looking much forward to a fruitfull and collaborative symbiosis." \
"All your Base are belong to us."


# --- Step 3: Generate the Audio ---
# This is the core function call. It synthesizes the speech.
print("Generating audio...")
wav = model.generate(text_to_speak)
print("Audio generated!")


# --- Step 4: Save the Audio to a File ---
# We use torchaudio to save the generated waveform as a .wav file.
output_filename = "hello_chatterbox.wav"
torchaudio.save(output_filename, wav, model.sr) # sr is the sample rate

print(f"Successfully saved audio to {output_filename}")