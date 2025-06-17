# Project Plan: spitztxt CLI Tool

## Current Status

The "Chatterbox" project appears to be a Text-to-Speech (TTS) system built around the `chatterbox.tts.ChatterboxTTS` model. Based on the analysis of `getting_started.py`, `clone.py`, and `emotions.py`, the core functionalities include:

- [x] **Basic Text-to-Speech (TTS):** Convert input text into spoken audio.
- [x] **Voice Cloning:** Generate speech in a voice cloned from a provided audio prompt.
- [x] **Emotional Tone Control:** Adjust the emotional expression of the generated speech using parameters like `exaggeration` and `cfg_weight`.

The system leverages `torch` and `torchaudio` for model loading, audio generation, and saving. The primary interaction point with the TTS model is the `generate` method, which accepts text, an optional audio prompt path, and emotional control parameters.

## Next Logical Steps: Developing a CLI-Based Layer

The goal is to create a command-line interface (CLI) tool that allows users to easily interact with the Chatterbox TTS model without modifying Python scripts directly. This CLI will expose the core functionalities identified above, adhering to the look, feel, and logic demonstrated in `example_CLI.py`. The project will be named "spitztxt", and its ASCII art will reflect this name.

### Phase 1: Initial CLI Setup and Main Menu

- [x] **Adopt `example_CLI.py` Structure:** Use `example_CLI.py` as the foundational template for the CLI. This includes its use of `colorama` for styling, `os.system` for clearing the terminal, and the main menu loop structure.
- [x] **Create `spitztxt-CLI.py`:** Develop a central Python script named `spitztxt-CLI.py` that will serve as the entry point for the CLI.
- [x] **Adapt Presentation Functions:** Modify `print_header_and_clear()` and `print_subtext()` to reflect the "spitztxt" branding and purpose, including the "spitztxt" ASCII art.
- [x] **Define Main Menu Options:** Structure the main menu to include options for:
    - [x] Basic Text-to-Speech
    - [x] Voice Cloning
    - [x] Emotional Tone Control
    - [x] Exit

### Phase 2: Implement Basic Text-to-Speech (TTS) Functionality

- [x] **Create `speak_text()` Function:** Implement a function (e.g., `speak_text()`) that will be called when the user selects the basic TTS option from the main menu.
- [x] **Load Chatterbox Model:** Integrate the model loading logic from `getting_started.py` within this function or a shared utility.
- [x] **Get User Input:** Prompt the user for the text they want to convert to speech.
- [x] **Generate and Save Audio:** Use `model.generate()` to create the audio and `torchaudio.save()` to save it to a user-specified or default WAV file.
- [x] **Handle Device Selection:** Automatically determine and use `cuda` or `cpu` for the model.

### Phase 3: Implement Voice Cloning Functionality

- [x] **Create `clone_voice()` Function:** Implement a function (e.g., `clone_voice()`) for the voice cloning option.
- [x] **Get User Input for Prompt:** Prompt the user for the path to the audio prompt file.
- [x] **Get User Input for Text:** Prompt the user for the text to be spoken in the cloned voice.
- [x] **Integrate Cloning Logic:** Use `model.generate()` with the `audio_prompt_path` parameter, similar to `clone.py`.
- [x] **Error Handling for Prompt File:** Ensure the provided audio prompt file exists before proceeding.
- [x] **Present Voice Templates:** Modify the `clone_voice` function to list available audio files from the `voice-templates` directory as options for voice prompts.

### Phase 4: Implement Emotional Tone Control Functionality

- [x] **Create `control_emotion()` Function:** Implement a function (e.g., `control_emotion()`) for the emotional tone control option.
- [x] **Get User Input for Text and Prompt:** Prompt the user for the text and an optional audio prompt file (can reuse the basic TTS or cloning logic as a base).
- [x] **Get User Input for `exaggeration` and `cfg_weight`:** Prompt the user for these float values.
- [x] **Parameter Validation:** Add basic validation to ensure these inputs are valid numbers within a reasonable range.
- [x] **Integrate Parameters:** Pass `exaggeration` and `cfg_weight` to the `model.generate()` method, similar to `emotions.py`.
- [x] **Present Voice Templates (Emotional Control):** Modify the `control_emotion` function to list available audio files from the `voice-templates` directory as options for voice prompts, or allow the user to skip providing a prompt.
- [x] **Add Emotional Control Tips:** Include descriptive tips for `exaggeration` and `cfg_weight` within the `control_emotion` function's prompt.
- [x] **Output Emotional Audio to Dedicated Folder:** Ensure audio files generated with emotional control are saved to a designated `output-emotion` folder.

### Phase 5: Refinements and Error Handling

- [x] **Centralized Model Loading:** Optimize model loading to occur once at the start of the application, rather than in each function, to improve performance.
- [x] **Robust Input Handling:** Improve user input validation for all commands (e.g., ensuring file paths are valid, numerical inputs are correct).
- [x] **Clear User Feedback:** Provide informative messages for success, errors, and progress.
- [x] **Exit Option:** Ensure the "Exit" option gracefully terminates the application.
- [x] **Automatic File Extension Handling:** Modify the CLI to automatically append `.wav` to output filenames if no extension is provided by the user, and update prompts to clarify this behavior.
- [x] **Implement "Back" Option:** Add a "back" option to sub-menus to allow users to return to the previous menu level.
- [x] **Output to Dedicated Folder:** Ensure all generated audio files are saved to a designated `output` folder (excluding emotional output).

### Phase 6: Future Considerations

- [ ] **Configuration Management:** Allow users to configure default settings (e.g., default output directory, model device preference) via a configuration file.
- [ ] **Advanced Features:** Explore adding more advanced features like listing available voices, managing output files, or integrating with other Chatterbox capabilities if they exist.
- [ ] **Packaging:** Prepare the CLI tool for distribution.
- [ ] **Comprehensive Documentation:** Create detailed user documentation.

This revised plan incorporates the structure and best practices from `example_CLI.py`, providing a more concrete roadmap for developing the "spitztxt" CLI tool.
