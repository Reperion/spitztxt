"""
spitztxt generation helpers — shared by interactive CLI and non-interactive smoke/tests.

Loads one model family at a time (VRAM-safe). Call unload_model() between families.
"""
from __future__ import annotations

import gc
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import torch
import torchaudio

# Repo-relative defaults
REPO_ROOT = Path(__file__).resolve().parent
VOICE_TEMPLATES_DIR = REPO_ROOT / "voice-templates"
OUTPUT_DIR = REPO_ROOT / "output"
OUTPUT_EMOTION_DIR = REPO_ROOT / "output-emotion"
OUTPUT_TURBO_DIR = REPO_ROOT / "output-turbo"
OUTPUT_MTL_DIR = REPO_ROOT / "output-multilingual"
OUTPUT_VC_DIR = REPO_ROOT / "output-vc"

MODEL_ORIGINAL = "original"
MODEL_TURBO = "turbo"
MODEL_MTL = "multilingual"
MODEL_VC = "vc"
MODEL_FAMILIES = (MODEL_ORIGINAL, MODEL_TURBO, MODEL_MTL, MODEL_VC)

# Capability matrix (what CLI should expose / pass through)
CAPABILITIES: dict[str, dict[str, bool]] = {
    MODEL_ORIGINAL: {
        "text": True,
        "clone": True,
        "emotion": True,
        "cfg": True,
        "exaggeration": True,
        "temperature": True,
        "min_p": True,
        "top_p": True,
        "top_k": False,
        "norm_loudness": False,
        "language_id": False,
        "vc": False,
    },
    MODEL_TURBO: {
        "text": True,
        "clone": True,
        "emotion": False,  # library ignores exaggeration/cfg/min_p
        "cfg": False,
        "exaggeration": False,
        "temperature": True,
        "min_p": False,
        "top_p": True,
        "top_k": True,
        "norm_loudness": True,
        "language_id": False,
        "vc": False,
    },
    MODEL_MTL: {
        "text": True,
        "clone": True,
        "emotion": True,
        "cfg": True,
        "exaggeration": True,
        "temperature": True,
        "min_p": True,
        "top_p": True,
        "top_k": False,
        "norm_loudness": False,
        "language_id": True,
        "vc": False,
    },
    MODEL_VC: {
        "text": False,
        "clone": False,
        "emotion": False,
        "cfg": False,
        "exaggeration": False,
        "temperature": False,
        "min_p": False,
        "top_p": False,
        "top_k": False,
        "norm_loudness": False,
        "language_id": False,
        "vc": True,
    },
}


@dataclass
class GenParams:
    """Sampling / quality knobs; only applied if the model family supports them."""

    temperature: float = 0.8
    cfg_weight: float = 0.5
    exaggeration: float = 0.5
    repetition_penalty: float = 1.2
    min_p: float = 0.05
    top_p: float = 1.0
    top_k: int = 1000
    norm_loudness: bool = True
    language_id: str = "en"
    extra: dict[str, Any] = field(default_factory=dict)


# Module-level single-model slot
_loaded_family: Optional[str] = None
_model: Any = None
_device: str = "cpu"


def detect_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def package_version() -> str:
    try:
        import importlib.metadata as md

        return md.version("chatterbox-tts")
    except Exception:
        try:
            import chatterbox  # noqa: F401

            return getattr(chatterbox, "__version__", "unknown")
        except Exception:
            return "unknown"


def ensure_output_dirs() -> None:
    for d in (
        OUTPUT_DIR,
        OUTPUT_EMOTION_DIR,
        OUTPUT_TURBO_DIR,
        OUTPUT_MTL_DIR,
        OUTPUT_VC_DIR,
        REPO_ROOT / "errors",
    ):
        d.mkdir(parents=True, exist_ok=True)


def unload_model() -> None:
    """Free GPU memory between sequential model loads."""
    global _loaded_family, _model
    _model = None
    _loaded_family = None
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def load_model(family: str, device: Optional[str] = None) -> Any:
    """Load one model family; unloads any previously loaded family."""
    global _loaded_family, _model, _device
    family = family.lower().strip()
    if family not in MODEL_FAMILIES:
        raise ValueError(f"Unknown model family {family!r}; choose from {MODEL_FAMILIES}")

    if _loaded_family == family and _model is not None:
        return _model

    unload_model()
    _device = device or detect_device()

    # Suppress noisy future warnings from deps
    import warnings

    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", message=".*LlamaSdpaAttention.*", category=UserWarning)

    if family == MODEL_ORIGINAL:
        from chatterbox.tts import ChatterboxTTS

        _model = ChatterboxTTS.from_pretrained(device=_device)
    elif family == MODEL_TURBO:
        from chatterbox.tts_turbo import ChatterboxTurboTTS

        _model = ChatterboxTurboTTS.from_pretrained(device=_device)
    elif family == MODEL_MTL:
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS

        _model = ChatterboxMultilingualTTS.from_pretrained(device=_device)
    elif family == MODEL_VC:
        from chatterbox.vc import ChatterboxVC

        _model = ChatterboxVC.from_pretrained(device=_device)
    else:
        raise ValueError(family)

    _loaded_family = family
    return _model


def current_family() -> Optional[str]:
    return _loaded_family


def current_model() -> Any:
    return _model


def current_sr() -> int:
    if _model is None:
        raise RuntimeError("No model loaded")
    return int(getattr(_model, "sr", 24000))


def list_voice_templates() -> list[Path]:
    if not VOICE_TEMPLATES_DIR.is_dir():
        return []
    return sorted(
        p
        for p in VOICE_TEMPLATES_DIR.iterdir()
        if p.suffix.lower() in {".mp3", ".wav", ".flac", ".ogg", ".m4a"}
    )


def ensure_wav_name(filename: str) -> str:
    if not filename.lower().endswith(".wav"):
        return filename + ".wav"
    return filename


def save_wav(wav: torch.Tensor, path: Path | str, sr: Optional[int] = None) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if sr is None:
        sr = current_sr()
    torchaudio.save(str(path), wav.cpu() if wav.device.type != "cpu" else wav, sr)
    return path


def generate_tts(
    text: str,
    *,
    family: Optional[str] = None,
    audio_prompt_path: Optional[str | Path] = None,
    params: Optional[GenParams] = None,
    out_path: Optional[str | Path] = None,
) -> Path:
    """
    Text-to-speech (optional voice clone) for original / turbo / multilingual.
    Returns path to saved WAV.
    """
    params = params or GenParams()
    fam = family or _loaded_family
    if fam is None:
        raise RuntimeError("No model family loaded; call load_model() first")
    if fam == MODEL_VC:
        raise ValueError("Use generate_vc() for voice conversion")
    if _loaded_family != fam or _model is None:
        load_model(fam)

    caps = CAPABILITIES[fam]
    if not caps["text"]:
        raise ValueError(f"{fam} does not support text TTS")

    prompt = str(audio_prompt_path) if audio_prompt_path else None
    kwargs: dict[str, Any] = {"text": text}

    if fam == MODEL_ORIGINAL:
        kwargs.update(
            audio_prompt_path=prompt,
            temperature=params.temperature,
            cfg_weight=params.cfg_weight,
            exaggeration=params.exaggeration,
            repetition_penalty=params.repetition_penalty,
            min_p=params.min_p,
            top_p=params.top_p,
        )
    elif fam == MODEL_TURBO:
        # CFG / exaggeration / min_p ignored by library — only pass supported knobs
        if not prompt:
            raise ValueError("Turbo requires audio_prompt_path (reference > ~5s recommended)")
        kwargs.update(
            audio_prompt_path=prompt,
            temperature=params.temperature,
            top_p=params.top_p,
            top_k=params.top_k,
            repetition_penalty=params.repetition_penalty,
            norm_loudness=params.norm_loudness,
            # keep zeros so library does not warn unless user forced values
            cfg_weight=0.0,
            exaggeration=0.0,
            min_p=0.0,
        )
    elif fam == MODEL_MTL:
        kwargs.update(
            language_id=params.language_id,
            audio_prompt_path=prompt,
            temperature=params.temperature,
            cfg_weight=params.cfg_weight,
            exaggeration=params.exaggeration,
            repetition_penalty=params.repetition_penalty
            if params.repetition_penalty != 1.2
            else 2.0,  # mtl default
            min_p=params.min_p,
            top_p=params.top_p,
        )
    else:
        raise ValueError(fam)

    wav = _model.generate(**kwargs)

    if out_path is None:
        if fam == MODEL_TURBO:
            base = OUTPUT_TURBO_DIR
        elif fam == MODEL_MTL:
            base = OUTPUT_MTL_DIR
        elif params.exaggeration != 0.5 or params.cfg_weight != 0.5:
            base = OUTPUT_EMOTION_DIR
        else:
            base = OUTPUT_DIR
        out_path = base / ensure_wav_name("spitztxt_out")
    else:
        out_path = Path(out_path)
        if out_path.suffix.lower() != ".wav":
            out_path = out_path.with_suffix(".wav")

    return save_wav(wav, out_path, current_sr())


def generate_vc(
    source_audio: str | Path,
    target_voice: str | Path,
    *,
    out_path: Optional[str | Path] = None,
) -> Path:
    """Voice conversion: re-speak source audio in target voice."""
    if _loaded_family != MODEL_VC or _model is None:
        load_model(MODEL_VC)

    source_audio = Path(source_audio)
    target_voice = Path(target_voice)
    if not source_audio.is_file():
        raise FileNotFoundError(f"source audio not found: {source_audio}")
    if not target_voice.is_file():
        raise FileNotFoundError(f"target voice not found: {target_voice}")

    wav = _model.generate(str(source_audio), target_voice_path=str(target_voice))

    if out_path is None:
        out_path = OUTPUT_VC_DIR / "vc_out.wav"
    else:
        out_path = Path(out_path)
        if out_path.suffix.lower() != ".wav":
            out_path = out_path.with_suffix(".wav")

    return save_wav(wav, out_path, current_sr())


def get_supported_languages() -> dict[str, str]:
    """Return multilingual language id -> name map if available."""
    try:
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS, SUPPORTED_LANGUAGES

        if hasattr(ChatterboxMultilingualTTS, "get_supported_languages"):
            return dict(ChatterboxMultilingualTTS.get_supported_languages())
        return dict(SUPPORTED_LANGUAGES)
    except Exception:
        return {"en": "English"}


def resolve_prompt(user_input: str, templates: Optional[list[Path]] = None) -> Optional[Path]:
    """Resolve template index (1-based), path, or empty -> None."""
    user_input = (user_input or "").strip()
    if not user_input:
        return None
    templates = templates if templates is not None else list_voice_templates()
    if user_input.isdigit():
        idx = int(user_input) - 1
        if 0 <= idx < len(templates):
            return templates[idx]
        raise ValueError(f"Invalid template number {user_input}")
    p = Path(user_input).expanduser()
    if not p.is_file():
        # try relative to templates
        alt = VOICE_TEMPLATES_DIR / user_input
        if alt.is_file():
            return alt
        raise FileNotFoundError(f"Voice prompt not found: {user_input}")
    return p
