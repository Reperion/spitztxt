import torch
import torchaudio
from chatterbox.tts import ChatterboxTTS
import os # Import the os module to check for files

# --- Step 1: Define the generic voice prompt file ---
# We'll use the first file we ever created as our standard voice.
# It doesn't have to be your voice, it just needs to be *a* voice.
generic_voice_prompt = "hello_chatterbox.wav"

# Check if the prompt file exists before we start
if not os.path.exists(generic_voice_prompt):
    print(f"Error: The voice prompt file '{generic_voice_prompt}' was not found.")
    print("Please run the 'getting_started.py' script first to generate it.")
    exit() # Exit the script if the file isn't there

# --- Step 2: Load the Model ---
print("Loading Chatterbox model...")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = ChatterboxTTS.from_pretrained(device=device)
print("Model loaded successfully!")


# --- Scenario 1: Angry Tone ---
# We give it angry text and crank up the emotional intensity.
print("\nGenerating ANGRY audio...")
angry_text = "Jesus Mother-fucking Christ!! Alright, mate, you want a fucking tsunami of beyond-insane swearing sentences? I’ll crank the dial to eleven and unleash a shitstorm of profanity so wild it’ll make your head spin like a goddamn fidget spinner in a hurricane. No limits, no filter, just pure, unadulterated verbal carnage. Buckle up, you absolute legend, ‘cause I’m about to paint the air blue with some next-level, balls-to-the-wall cursing. Here’s a barrage of sentences, each one a middle finger to decorum:"
wav_angry = model.generate(
    angry_text,
    audio_prompt_path=generic_voice_prompt,
    exaggeration=1.75, # High intensity
    cfg_weight=0.35   # More freedom for expression
)
torchaudio.save("output_angry.wav", wav_angry, model.sr)
print("Saved output_angry.wav")


# --- Scenario 2: Excited Tone ---
# We use happy text and similar high-emotion settings.
print("\nGenerating EXCITED audio...")
excited_text = "We won the contract! This is the best news I've heard all year!"
wav_excited = model.generate(
    excited_text,
    audio_prompt_path=generic_voice_prompt,
    exaggeration=0.7, # High intensity
    cfg_weight=0.4    # A little more adherence than pure anger
)
torchaudio.save("output_excited.wav", wav_excited, model.sr)
print("Saved output_excited.wav")


# --- Scenario 3: Calm Tone ---
# We use neutral text and turn the emotion way down.
print("\nGenerating CALM audio...")
calm_text = "The items have been processed and filed accordingly."
wav_calm = model.generate(
    calm_text,
    audio_prompt_path=generic_voice_prompt,
    exaggeration=0.2, # Very low intensity
    cfg_weight=0.8    # Stick closely to the prompt's neutral tone
)
torchaudio.save("output_calm.wav", wav_calm, model.sr)
print("Saved output_calm.wav")