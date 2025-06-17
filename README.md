███████╗██████╗ ██╗████████╗███████╗████████╗██╗  ██╗████████╗
██╔════╝██╔══██╗██║╚══██╔══╝╚══███╔╝╚══██╔══╝╚██╗██╔╝╚══██╔══╝
███████╗██████╔╝██║   ██║     ███╔╝    ██║    ╚███╔╝    ██║   
╚════██║██╔═══╝ ██║   ██║    ███╔╝     ██║    ██╔██╗    ██║   
███████║██║     ██║   ██║   ███████╗   ██║   ██╔╝ ██╗   ██║   
╚══════╝╚═╝     ╚═╝   ╚═╝   ╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   
     ### Your Awesome Text-to-Speech Tool ###
```

# spitztxt - Your Command-Line Text-to-Speech Tool

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Development-orange.svg)](https://github.com/your-username/spitztxt/pulse)

## Description

`spitztxt` is a powerful command-line interface (CLI) tool built on top of the Chatterbox TTS model, designed to provide easy access to advanced Text-to-Speech (TTS), Voice Cloning, and Emotional Tone Control functionalities. Whether you need to convert text to speech, clone a voice from an audio sample, or infuse your generated audio with specific emotions, `spitztxt` offers a straightforward and interactive experience directly from your terminal.

## Features

-   **Basic Text-to-Speech (TTS):** Convert any input text into high-quality spoken audio.
-   **Voice Cloning:** Generate speech in a voice that mimics a provided audio prompt, allowing for personalized audio output.
-   **Emotional Tone Control:** Fine-tune the emotional expression of the generated speech using `exaggeration` and `cfg_weight` parameters for nuanced results.
-   **Interactive CLI:** User-friendly menu-driven interface for seamless navigation and operation.
-   **Cross-Platform Compatibility:** Built with `colorama` for consistent stylized output across different operating systems.
-   **Automatic Device Detection:** Automatically utilizes `cuda` (GPU) if available for faster processing, falling back to `cpu` otherwise.

## Installation

To get `spitztxt` up and running, follow these steps:

### Prerequisites

-   Python 3.8 or higher
-   `pip` (Python package installer)

### Clone the Repository

```bash
git clone https://github.com/your-username/spitztxt.git
cd spitztxt
```

### Install Dependencies

`spitztxt` relies on `chatterbox` for its core TTS functionalities, along with `torch`, `torchaudio`, and `colorama`.

```bash
pip install -r requirements.txt
# If you don't have a requirements.txt, you might need to install them manually:
# pip install torch torchaudio colorama chatterbox
```
**Note:** `torch` and `torchaudio` installation might vary based on your system and CUDA availability. Refer to the official PyTorch documentation for specific instructions if you encounter issues.

## Usage

To start the `spitztxt` CLI, simply run the `spitztxt-CLI.py` script:

```bash
python spitztxt-CLI.py
```

Upon launching, you will be presented with a main menu:

```
 
███████╗██████╗ ██╗████████╗███████╗████████╗██╗  ██╗████████╗
██╔════╝██╔══██╗██║╚══██╔══╝╚══███╔╝╚══██╔══╝╚██╗██╔╝╚══██╔══╝
███████╗██████╔╝██║   ██║     ███╔╝    ██║    ╚███╔╝    ██║   
╚════██║██╔═══╝ ██║   ██║    ███╔╝     ██║    ██╔██╗    ██║   
███████║██║     ██║   ██║   ███████╗   ██║   ██╔╝ ██╗   ██║   
╚══════╝╚═╝     ╚═╝   ╚═╝   ╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   

     ### Your Awesome Text-to-Speech Tool ###

This is the spitztxt CLI tool for Text-to-Speech, Voice Cloning, and Emotional Tone Control.

Choose an option to proceed:

1. Basic Text-to-Speech
2. Voice Cloning
3. Emotional Tone Control
0. Exit
```

Follow the on-screen prompts to select your desired functionality.

### Examples

#### Basic Text-to-Speech

1.  Select option `1` from the main menu.
2.  Enter the text you wish to convert to speech.
3.  Provide an output filename (e.g., `my_audio.wav`).

#### Voice Cloning

1.  Select option `2` from the main menu.
2.  You will be prompted to provide a path to a voice prompt audio file (e.g., an MP3 or WAV file). You can also choose from available templates in the `voice-templates` directory.
3.  Enter the text you want the cloned voice to speak.
4.  Provide an output filename (e.g., `cloned_voice_output.wav`).

#### Emotional Tone Control

1.  Select option `3` from the main menu.
2.  Enter the text you wish to speak.
3.  Optionally, provide a path to a voice prompt audio file for cloning the voice.
4.  Adjust `exaggeration` (e.g., `0.5` to `1.5`) and `cfg_weight` (e.g., `0.0` to `1.0`) parameters to control the emotional intensity and pacing.
    *   **Tips:**
        *   **General Use:** Default settings (exaggeration=0.5, cfg_weight=0.5) work well.
        *   **Fast Speaking Style:** Lower `cfg_weight` (around `0.3`) can improve pacing.
        *   **Expressive/Dramatic Speech:** Try lower `cfg_weight` (e.g., `~0.3`) and increase `exaggeration` (e.g., `0.7` or higher).
5.  Provide an output filename (e.g., `emotional_speech.wav`). Emotional audio files are saved to the `output-emotion` directory.

## Voice Templates

The `voice-templates` directory is used to store audio files that can be used as prompts for voice cloning and emotional tone control. You can place your `.mp3` or `.wav` files in this directory, and `spitztxt` will list them as available options.

## Output Directories

-   **`output/`**: Contains audio files generated from basic TTS and voice cloning.
-   **`output-emotion/`**: Contains audio files generated with emotional tone control.

## Error Logging

`spitztxt` logs errors to a dedicated `errors/` directory. Each error log file is timestamped for easy debugging and tracking.

## Contributing

We welcome contributions to `spitztxt`! If you have suggestions for improvements, new features, or bug fixes, please feel free to:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add new feature'`).
5.  Push to the branch (`git push origin feature/your-feature-name`).
6.  Open a Pull Request.

Please ensure your code adheres to good practices and includes relevant tests if applicable.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For any questions or feedback, please open an issue on the GitHub repository.
