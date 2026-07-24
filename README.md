```
 
███████╗██████╗ ██╗████████╗███████╗████████╗██╗  ██╗████████╗
██╔════╝██╔══██╗██║╚══██╔══╝╚══███╔╝╚══██╔══╝╚██╗██╔╝╚══██╔══╝
███████╗██████╔╝██║   ██║     ███╔╝    ██║    ╚███╔╝    ██║   
╚════██║██╔═══╝ ██║   ██║    ███╔╝     ██║    ██╔██╗    ██║   
███████║██║     ██║   ██║   ███████╗   ██║   ██╔╝ ██╗   ██║   
╚══════╝╚═╝     ╚═╝   ╚═╝   ╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   

     ### spitztxt — Chatterbox TTS family CLI ###
```

# spitztxt

> **Active repo:** [Reperion/spitztxt](https://github.com/Reperion/spitztxt)  
> Formerly [Reperion/Chatterbox](https://github.com/Reperion/Chatterbox) (kept for history).

CLI for **ResembleAI Chatterbox** — basic TTS, zero-shot voice cloning, emotion/CFG, **Turbo**, **Multilingual**, and **Voice Conversion**.

| Stack | Package | How to run |
|-------|---------|------------|
| **Default (new)** | `chatterbox-tts` **≥ 0.1.7** in `venv-0.1.7/` | `spitztxt` |
| **Legacy** | `chatterbox-tts` **0.1.2** in linked `venv/` | `spitztxt-legacy` |

## Quick start

```bash
# New stack (interactive menu)
spitztxt

# Or from repo
cd /home/lucid/projects/spitztxt
./run_spitztxt.sh
```

### Non-interactive examples

```bash
spitztxt --version

# Original TTS
spitztxt --model original --text "Hello from spitztxt." -o output/hello.wav

# Clone (KITT / Morgan templates in voice-templates/)
spitztxt --model original --text "Knight Rider." --prompt voice-templates/kitt.mp3 -o output/kitt.wav

# Emotion / CFG knobs
spitztxt --model original --text "Dramatic line." --prompt voice-templates/morgan_cropped.mp3 \
  --exaggeration 0.8 --cfg-weight 0.3 -o output-emotion/drama.wav

# Turbo (requires prompt; CFG/exaggeration ignored by library)
spitztxt --model turbo --text "Fast clone." --prompt voice-templates/morgan_cropped.mp3 \
  --temperature 0.7 --top-k 1000 -o output-turbo/t.wav

# Multilingual
spitztxt --model multilingual --text "Hello from multilingual." --language en \
  --prompt voice-templates/morgan_cropped.mp3 -o output-multilingual/en.wav

# Voice conversion (source speech → target voice)
spitztxt --model vc --source output/hello.wav --target voice-templates/kitt.mp3 -o output-vc/vc.wav

# Full sequential smoke (loads one model at a time — VRAM safe)
spitztxt --smoke --smoke-dir output/smoke
```

### Legacy (0.1.2)

```bash
spitztxt-legacy   # old interactive menu only
```

Does **not** use `venv-0.1.7`. Old env is the symlink `venv` → `../chatterbox/venv`.

## Model families

| Family | CLI `--model` | Notes |
|--------|---------------|--------|
| Original | `original` | Emotion + CFG + clone; ~6s enc / ~10s dec ref caps |
| Turbo | `turbo` | Fast; **prompt required** (>~5s); no CFG/exaggeration/min_p |
| Multilingual | `multilingual` | Requires `--language` / language_id (e.g. `en`) |
| VC | `vc` | `--source` + `--target` audio (no text) |

Sampling knobs exposed when supported: `temperature`, `cfg_weight`, `exaggeration`, `min_p`, `top_p`, `top_k`, `norm_loudness`, `repetition_penalty`.

## Layout

| Path | Role |
|------|------|
| `spitztxt_core.py` | Load/generate/save helpers (used by CLI + tests) |
| `spitztxt-CLI.py` | Interactive + argparse entry |
| `spitztxt-CLI-legacy.py` | Frozen 0.1.2 interactive CLI |
| `venv-0.1.7/` | New stack (not in git) |
| `venv` | Symlink to legacy 0.1.2 env |
| `voice-templates/` | Clone / VC target prompts |
| `output/`, `output-emotion/`, `output-turbo/`, `output-multilingual/`, `output-vc/` | WAV outputs |

## Install (new machine)

```bash
git clone git@github.com:Reperion/spitztxt.git
cd spitztxt
python3 -m venv venv-0.1.7
source venv-0.1.7/bin/activate
pip install -U 'pip' 'setuptools>=70,<81'   # pkg_resources needed by resemble-perth
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu124
pip install -r requirements.txt
./run_spitztxt.sh --version
```

First run may download multi-GB HF weights (Turbo / Multilingual). Sequential load only — do not load all four models at once on a 16GB laptop GPU.

## Tests

```bash
venv-0.1.7/bin/python -m pytest tests/ -v
# GPU generate tests may take minutes; structural tests are fast
```

## Reference audio tips

- Clean, single-speaker, little reverb/noise.
- Original: ~6–10s is enough (hard caps in the model).
- Turbo: prompt must be **> 5 seconds**.
- Longer files are truncated; crop the best segment rather than feeding a full podcast.
