import os
import time
import colorama
from colorama import Fore, Style
import logging
from datetime import datetime

import torch
import torchaudio
from chatterbox.tts import ChatterboxTTS

# Initialize colorama for cross-platform colored output
colorama.init(autoreset=True)

# --- Logging Setup ---
LOG_DIR = "errors"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"spitztxt_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.info("spitztxt CLI started.")

# --- Output Directory Setup ---
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_EMOTION_DIR = "output-emotion"
os.makedirs(OUTPUT_EMOTION_DIR, exist_ok=True)

# Global model instance
model = None
device = "cpu" # Default device

def load_chatterbox_model():
    global model, device
    print(f"{Fore.BLUE}Loading Chatterbox model...{Style.RESET_ALL}")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    try:
        model = ChatterboxTTS.from_pretrained(device=device)
        print(f"{Fore.GREEN}Model loaded successfully on {device}!{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error loading model: {e}{Style.RESET_ALL}")
        print(f"{Fore.RED}Please ensure 'chatterbox' is installed and accessible.{Style.RESET_ALL}")
        model = None # Ensure model is None if loading fails
    time.sleep(2) # Give user time to read message

# --- CLI Presentation Functions ---

def print_header_and_clear():
    """
    Clears the terminal and prints a stylized header for spitztxt.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    # ASCII art for "spitztxt"
    ascii_art = """
 
███████╗██████╗ ██╗████████╗███████╗████████╗██╗  ██╗████████╗
██╔════╝██╔══██╗██║╚══██╔══╝╚══███╔╝╚══██╔══╝╚██╗██╔╝╚══██╔══╝
███████╗██████╔╝██║   ██║     ███╔╝    ██║    ╚███╔╝    ██║   
╚════██║██╔═══╝ ██║   ██║    ███╔╝     ██║    ██╔██╗    ██║   
███████║██║     ██║   ██║   ███████╗   ██║   ██╔╝ ██╗   ██║   
╚══════╝╚═╝     ╚═╝   ╚═╝   ╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   

     ### Your Awesome Text-to-Speech Tool ###
"""
    print(f"{Fore.GREEN + Style.BRIGHT}{ascii_art}{Style.RESET_ALL}")

def print_subtext():
    """
    Prints a descriptive subtext below the header for spitztxt.
    """
    subtext = f"""
{Fore.GREEN}This is the spitztxt CLI tool for Text-to-Speech, Voice Cloning, and Emotional Tone Control.

Choose an option to proceed:
{Style.RESET_ALL}"""
    print(subtext)

def ensure_wav_extension(filename):
    """Ensures the filename has a .wav extension."""
    if not filename.lower().endswith(".wav"):
        return filename + ".wav"
    return filename

def speak_text():
    """
    Handles basic Text-to-Speech functionality.
    Returns True to go back to the main menu, False to exit.
    """
    while True:
        print_header_and_clear()
        print(f"{Fore.BLUE}--- Basic Text-to-Speech ---{Style.RESET_ALL}")
        text_to_speak = input(f"{Fore.CYAN}Enter the text you want to convert to speech (or 'b' to go back): {Style.RESET_ALL}")
        if text_to_speak.lower() == 'b':
            return True

        if model is None:
            print(f"{Fore.RED}Model not loaded. Please restart the application.{Style.RESET_ALL}")
            time.sleep(3)
            return True

        output_filename = input(f"{Fore.CYAN}Enter output filename (e.g., my_audio, default: basic_tts): {Style.RESET_ALL}").strip()
        if not output_filename:
            output_filename = "basic_tts"
        output_filename = ensure_wav_extension(output_filename)
        full_output_path = os.path.join(OUTPUT_DIR, output_filename)

        logging.info(f"Attempting basic TTS for text: '{text_to_speak[:50]}...' to '{full_output_path}'")
        try:
            wav = model.generate(text_to_speak)
            torchaudio.save(full_output_path, wav, model.sr)
            print(f"{Fore.GREEN}Successfully saved audio to '{full_output_path}'!{Style.RESET_ALL}")
            logging.info(f"Successfully generated and saved audio to '{full_output_path}'")
        except Exception as e:
            print(f"{Fore.RED}Error generating audio: {e}{Style.RESET_ALL}")
            logging.error(f"Error generating audio for basic TTS: {e}", exc_info=True)
        time.sleep(3)

def clone_voice():
    """
    Handles voice cloning functionality.
    Returns True to go back to the main menu, False to exit.
    """
    VOICE_TEMPLATES_DIR = "voice-templates"
    os.makedirs(VOICE_TEMPLATES_DIR, exist_ok=True)
    
    while True:
        print_header_and_clear()
        print(f"{Fore.BLUE}--- Voice Cloning ---{Style.RESET_ALL}")
        
        available_templates = [f for f in os.listdir(VOICE_TEMPLATES_DIR) if f.lower().endswith(('.mp3', '.wav'))]
        
        if available_templates:
            print(f"{Fore.WHITE}Available Voice Templates:{Style.RESET_ALL}")
            for i, template in enumerate(available_templates):
                print(f"{Fore.WHITE}{i+1}. {template}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}------------------------{Style.RESET_ALL}")

        voice_prompt_input = input(f"{Fore.CYAN}Enter path to voice prompt audio file, select a number from above, or 'b' to go back: {Style.RESET_ALL}").strip()
        
        if voice_prompt_input.lower() == 'b':
            return True

        voice_prompt_file = ""
        if voice_prompt_input.isdigit():
            idx = int(voice_prompt_input) - 1
            if 0 <= idx < len(available_templates):
                voice_prompt_file = os.path.join(VOICE_TEMPLATES_DIR, available_templates[idx])
            else:
                print(f"{Fore.RED}Invalid selection. Please enter a valid number or path.{Style.RESET_ALL}")
                time.sleep(2)
                continue
        else:
            voice_prompt_file = voice_prompt_input

        if model is None:
            print(f"{Fore.RED}Model not loaded. Please restart the application.{Style.RESET_ALL}")
            time.sleep(3)
            return True

        if not os.path.exists(voice_prompt_file):
            print(f"{Fore.RED}Error: Voice prompt file '{voice_prompt_file}' not found.{Style.RESET_ALL}")
            time.sleep(3)
            continue # Loop again for valid input

        text_to_speak = input(f"{Fore.CYAN}Enter the text you want the cloned voice to speak: {Style.RESET_ALL}")
        output_filename = input(f"{Fore.CYAN}Enter output filename (e.g., my_cloned_audio, default: cloned_tts): {Style.RESET_ALL}").strip()
        if not output_filename:
            output_filename = "cloned_tts"
        output_filename = ensure_wav_extension(output_filename)
        full_output_path = os.path.join(OUTPUT_DIR, output_filename)

        logging.info(f"Attempting voice cloning for text: '{text_to_speak[:50]}...' with prompt '{voice_prompt_file}' to '{full_output_path}'")
        try:
            wav = model.generate(text_to_speak, audio_prompt_path=voice_prompt_file)
            torchaudio.save(full_output_path, wav, model.sr)
            print(f"{Fore.GREEN}Successfully saved cloned audio to '{full_output_path}'!{Style.RESET_ALL}")
            logging.info(f"Successfully generated and saved cloned audio to '{full_output_path}'")
        except Exception as e:
            print(f"{Fore.RED}Error generating cloned audio: {e}{Style.RESET_ALL}")
            logging.error(f"Error generating cloned audio: {e}", exc_info=True)
        time.sleep(3)

def control_emotion():
    """
    Handles emotional tone control functionality.
    Returns True to go back to the main menu, False to exit.
    """
    VOICE_TEMPLATES_DIR = "voice-templates"
    os.makedirs(VOICE_TEMPLATES_DIR, exist_ok=True)

    while True:
        print_header_and_clear()
        print(f"{Fore.BLUE}--- Emotional Tone Control ---{Style.RESET_ALL}")
        text_to_speak = input(f"{Fore.CYAN}Enter the text (or 'b' to go back): {Style.RESET_ALL}")
        if text_to_speak.lower() == 'b':
            return True

        if model is None:
            print(f"{Fore.RED}Model not loaded. Please restart the application.{Style.RESET_ALL}")
            time.sleep(3)
            return True

        available_templates = [f for f in os.listdir(VOICE_TEMPLATES_DIR) if f.lower().endswith(('.mp3', '.wav'))]
        
        voice_prompt_file = None # Initialize to None
        
        if available_templates:
            print(f"{Fore.WHITE}Available Voice Templates:{Style.RESET_ALL}")
            for i, template in enumerate(available_templates):
                print(f"{Fore.WHITE}{i+1}. {template}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}------------------------{Style.RESET_ALL}")

        voice_prompt_input = input(f"{Fore.CYAN}Enter path to voice prompt audio file, select a number from above, or leave blank to skip: {Style.RESET_ALL}").strip()

        if voice_prompt_input: # If user provided input
            if voice_prompt_input.lower() == 'b': # Allow 'b' to go back from this sub-prompt
                return True
            if voice_prompt_input.isdigit():
                idx = int(voice_prompt_input) - 1
                if 0 <= idx < len(available_templates):
                    voice_prompt_file = os.path.join(VOICE_TEMPLATES_DIR, available_templates[idx])
                else:
                    print(f"{Fore.RED}Invalid selection. Please enter a valid number or path.{Style.RESET_ALL}")
                    time.sleep(2)
                    continue # Loop again for valid input
            else:
                voice_prompt_file = voice_prompt_input
                if not os.path.exists(voice_prompt_file):
                    print(f"{Fore.RED}Error: Voice prompt file '{voice_prompt_file}' not found. Please try again.{Style.RESET_ALL}")
                    time.sleep(3)
                    continue # Loop again for valid input

        print(f"{Fore.YELLOW}\n--- Emotional Control Tips ---{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}General Use (TTS and Voice Agents):{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  - Default settings (exaggeration=0.5, cfg_weight=0.5) work well for most prompts.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  - If the reference speaker has a fast speaking style, lowering cfg_weight to around 0.3 can improve pacing.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Expressive or Dramatic Speech:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  - Try lower cfg_weight values (e.g. ~0.3) and increase exaggeration to around 0.7 or higher.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  - Higher exaggeration tends to speed up speech; reducing cfg_weight helps compensate with slower, more deliberate pacing.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}------------------------------{Style.RESET_ALL}")

        exaggeration = 1.0
        cfg_weight = 0.0

        while True:
            exaggeration_str = input(f"{Fore.CYAN}Enter exaggeration (float, e.g., 0.5, 1.0, 1.5; default: 1.0): {Style.RESET_ALL}").strip()
            if not exaggeration_str:
                break
            try:
                exaggeration = float(exaggeration_str)
                break
            except ValueError:
                print(f"{Fore.RED}Invalid input. Please enter a valid float for exaggeration.{Style.RESET_ALL}")

        while True:
            cfg_weight_str = input(f"{Fore.CYAN}Enter cfg_weight (float, e.g., 0.0, 0.5, 1.0; default: 0.0): {Style.RESET_ALL}").strip()
            if not cfg_weight_str:
                break
            try:
                cfg_weight = float(cfg_weight_str)
                break
            except ValueError:
                print(f"{Fore.RED}Invalid input. Please enter a valid float for cfg_weight.{Style.RESET_ALL}")

        output_filename = input(f"{Fore.CYAN}Enter output filename (e.g., my_emotional_audio, default: emotional_tts): {Style.RESET_ALL}").strip()
        if not output_filename:
            output_filename = "emotional_tts"
        output_filename = ensure_wav_extension(output_filename)
        full_output_path = os.path.join(OUTPUT_EMOTION_DIR, output_filename) # Save to output-emotion directory

        logging.info(f"Attempting emotional TTS for text: '{text_to_speak[:50]}...' with prompt '{voice_prompt_file}', exaggeration={exaggeration}, cfg_weight={cfg_weight} to '{full_output_path}'")
        try:
            if voice_prompt_file:
                wav = model.generate(text_to_speak, audio_prompt_path=voice_prompt_file, exaggeration=exaggeration, cfg_weight=cfg_weight)
            else:
                wav = model.generate(text_to_speak, exaggeration=exaggeration, cfg_weight=cfg_weight)
            torchaudio.save(full_output_path, wav, model.sr)
            print(f"{Fore.GREEN}Successfully saved emotional audio to '{full_output_path}'!{Style.RESET_ALL}")
            logging.info(f"Successfully generated and saved emotional audio to '{full_output_path}'")
        except Exception as e:
            print(f"{Fore.RED}Error generating emotional audio: {e}{Style.RESET_ALL}")
            logging.error(f"Error generating emotional audio: {e}", exc_info=True)
        time.sleep(3)

# --- Main Application Loop ---

def main():
    """
    The main function that runs the spitztxt CLI application loop.
    """
    load_chatterbox_model() # Load model once at startup

    while True:
        print_header_and_clear()
        print_subtext()

        print(f"{Fore.WHITE + Style.BRIGHT}1. Basic Text-to-Speech{Style.RESET_ALL}")
        print(f"{Fore.WHITE + Style.BRIGHT}2. Voice Cloning{Style.RESET_ALL}")
        print(f"{Fore.WHITE + Style.BRIGHT}3. Emotional Tone Control{Style.RESET_ALL}")
        print(f"{Fore.WHITE + Style.BRIGHT}0. Exit{Style.RESET_ALL}")

        choice = input(f"{Fore.CYAN}Choose an option (0, 1, 2, or 3): {Style.RESET_ALL}").strip()

        if choice == "1":
            speak_text()
        elif choice == "2":
            clone_voice()
        elif choice == "3":
            control_emotion()
        elif choice == "0":
            print(f"{Fore.GREEN}Exiting spitztxt CLI. Goodbye!{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED + Style.BRIGHT}Invalid choice. Please try again.{Style.RESET_ALL}")
            time.sleep(2)

if __name__ == "__main__":
    main()
