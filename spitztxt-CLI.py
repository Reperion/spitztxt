#!/usr/bin/env python3
"""
spitztxt — interactive + non-interactive CLI for Chatterbox TTS family
(original, turbo, multilingual, voice conversion).

Generation logic lives in spitztxt_core so smokes/tests hit the same path.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import colorama
from colorama import Fore, Style

import spitztxt_core as core

colorama.init(autoreset=True)

LOG_DIR = core.REPO_ROOT / "errors"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"spitztxt_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logging.info(
    "spitztxt CLI started. chatterbox-tts=%s device=%s",
    core.package_version(),
    core.detect_device(),
)


def print_header_and_clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    ascii_art = r"""
 
███████╗██████╗ ██╗████████╗███████╗████████╗██╗  ██╗████████╗
██╔════╝██╔══██╗██║╚══██╔══╝╚══███╔╝╚══██╔══╝╚██╗██╔╝╚══██╔══╝
███████╗██████╔╝██║   ██║     ███╔╝    ██║    ╚███╔╝    ██║   
╚════██║██╔═══╝ ██║   ██║    ███╔╝     ██║    ██╔██╗    ██║   
███████║██║     ██║   ██║   ███████╗   ██║   ██╔╝ ██╗   ██║   
╚══════╝╚═╝     ╚═╝   ╚═╝   ╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   

     ### spitztxt — Chatterbox TTS family CLI ###
"""
    print(f"{Fore.GREEN + Style.BRIGHT}{ascii_art}{Style.RESET_ALL}")
    print(
        f"{Fore.CYAN}chatterbox-tts {core.package_version()}  |  device: {core.detect_device()}  |  "
        f"loaded: {core.current_family() or 'none'}{Style.RESET_ALL}\n"
    )


class BackToMenu(Exception):
    """User typed b / back — return to the main menu."""


def _is_back(raw: str) -> bool:
    return (raw or "").strip().lower() in ("b", "back")


def _prompt_line(label: str, *, default: str | None = None) -> str:
    """Read a line; raise BackToMenu on b/back. Empty uses default if given."""
    hint = f" [default {default}]" if default is not None else ""
    raw = input(f"{Fore.CYAN}{label}{hint} (or 'b' back): {Style.RESET_ALL}").strip()
    if _is_back(raw):
        raise BackToMenu()
    if not raw and default is not None:
        return default
    return raw


def _prompt_float(label: str, default: float) -> float:
    raw = input(
        f"{Fore.CYAN}{label} [default {default}] (or 'b' back): {Style.RESET_ALL}"
    ).strip()
    if _is_back(raw):
        raise BackToMenu()
    if not raw:
        return default
    return float(raw)


def _prompt_int(label: str, default: int) -> int:
    raw = input(
        f"{Fore.CYAN}{label} [default {default}] (or 'b' back): {Style.RESET_ALL}"
    ).strip()
    if _is_back(raw):
        raise BackToMenu()
    if not raw:
        return default
    return int(raw)


def _prompt_bool(label: str, default: bool) -> bool:
    d = "Y/n" if default else "y/N"
    raw = input(f"{Fore.CYAN}{label} [{d}] (or 'b' back): {Style.RESET_ALL}").strip().lower()
    if _is_back(raw):
        raise BackToMenu()
    if not raw:
        return default
    return raw in ("y", "yes", "1", "true")


def _pick_template(required: bool = False) -> Path | None:
    templates = core.list_voice_templates()
    if templates:
        print(f"{Fore.WHITE}Voice templates:{Style.RESET_ALL}")
        for i, t in enumerate(templates, 1):
            print(f"  {i}. {t.name}")
    skip = "blank to skip" if not required else "required"
    raw = input(
        f"{Fore.CYAN}Prompt path / template # / {skip} / 'b' back: {Style.RESET_ALL}"
    ).strip()
    if _is_back(raw):
        raise BackToMenu()
    if not raw:
        if required:
            raise ValueError("A voice prompt is required (or type 'b' to go back)")
        return None
    return core.resolve_prompt(raw, templates)


def _collect_params(
    family: str,
    *,
    base: core.GenParams | None = None,
    force: bool = False,
    ask_first: bool = True,
) -> core.GenParams:
    """
    Collect sampling knobs.

    By default (ask_first=True, force=False) asks once:
      "Tune sampling knobs? [y/N]"
    and if no, returns `base` (or family clone defaults) with no further prompts.
    Emotion menu can pass force=True to always show knobs (Enter keeps each default).
    """
    caps = core.CAPABILITIES[family]
    p = base or core.defaults_for_clone(family)

    if ask_first and not force:
        raw = input(
            f"{Fore.CYAN}Tune sampling knobs? [y/N] "
            f"(default: clone settings) / 'b' back: {Style.RESET_ALL}"
        ).strip().lower()
        if _is_back(raw):
            raise BackToMenu()
        if raw not in ("y", "yes", "1"):
            print(
                f"{Fore.WHITE}Using defaults: temp={p.temperature} cfg={p.cfg_weight} "
                f"exag={p.exaggeration} (chunk long text={p.chunk_long_text}){Style.RESET_ALL}"
            )
            return p

    print(
        f"{Fore.YELLOW}Sampling knobs — Enter keeps default; 'b' back to main menu. "
        f"Unsupported knobs skipped for {family}.{Style.RESET_ALL}"
    )
    if family == core.MODEL_TURBO:
        print(
            f"{Fore.YELLOW}Note: Turbo ignores CFG, exaggeration, and min_p "
            f"(library limitation).{Style.RESET_ALL}"
        )
    if caps["temperature"]:
        p.temperature = _prompt_float("temperature", p.temperature)
    if caps["cfg"]:
        p.cfg_weight = _prompt_float(
            "cfg_weight (lower ~0.3 = calmer / less rushed)", p.cfg_weight
        )
    if caps["exaggeration"]:
        p.exaggeration = _prompt_float(
            "exaggeration (higher can speed speech up)", p.exaggeration
        )
    if caps["min_p"]:
        p.min_p = _prompt_float("min_p", p.min_p)
    if caps["top_p"]:
        p.top_p = _prompt_float("top_p", p.top_p)
    if caps["top_k"]:
        p.top_k = _prompt_int("top_k", p.top_k)
    if caps["norm_loudness"]:
        p.norm_loudness = _prompt_bool("norm_loudness", p.norm_loudness)
    if caps["language_id"]:
        langs = core.get_supported_languages()
        print(f"{Fore.WHITE}Languages (sample): {', '.join(list(langs.keys())[:12])}...{Style.RESET_ALL}")
        lid = input(
            f"{Fore.CYAN}language_id [default {p.language_id}] (or 'b' back): {Style.RESET_ALL}"
        ).strip()
        if _is_back(lid):
            raise BackToMenu()
        p.language_id = lid or p.language_id
    return p


def ensure_model(family: str) -> None:
    if core.current_family() == family and core.current_model() is not None:
        return
    print(
        f"{Fore.BLUE}Loading '{family}' on {core.detect_device()} "
        f"(~10–30s when cached; first run can take longer if weights download)…{Style.RESET_ALL}"
    )
    t0 = time.time()
    try:
        core.load_model(family)
        print(
            f"{Fore.GREEN}Ready: {family}  sr={core.current_sr()}  "
            f"in {time.time() - t0:.1f}s{Style.RESET_ALL}"
        )
    except Exception as e:
        print(f"{Fore.RED}Failed to load {family}: {e}{Style.RESET_ALL}")
        logging.error("load_model %s: %s", family, e, exc_info=True)
        raise
    time.sleep(0.5)


def menu_select_model() -> None:
    print_header_and_clear()
    print(f"{Fore.BLUE}--- Select model family ---{Style.RESET_ALL}")
    print("1. original  — ChatterboxTTS (emotion + CFG + clone)")
    print("2. turbo     — ChatterboxTurboTTS (fast; clone required; no CFG)")
    print("3. multilingual — ChatterboxMultilingualTTS (language_id required)")
    print("4. vc        — ChatterboxVC (voice conversion)")
    print("b. back")
    choice = input(f"{Fore.CYAN}Choice: {Style.RESET_ALL}").strip().lower()
    mapping = {"1": core.MODEL_ORIGINAL, "2": core.MODEL_TURBO, "3": core.MODEL_MTL, "4": core.MODEL_VC}
    if choice in ("b", ""):
        return
    fam = mapping.get(choice)
    if not fam:
        print(f"{Fore.RED}Invalid{Style.RESET_ALL}")
        time.sleep(1)
        return
    ensure_model(fam)


def menu_basic_tts() -> None:
    fam = core.current_family() or core.MODEL_ORIGINAL
    if fam == core.MODEL_VC:
        print(f"{Fore.RED}VC is loaded — switch to original/turbo/mtl for TTS.{Style.RESET_ALL}")
        time.sleep(2)
        return
    if fam == core.MODEL_TURBO:
        print(f"{Fore.YELLOW}Turbo needs a clone prompt; use Voice Clone menu instead.{Style.RESET_ALL}")
        time.sleep(2)
        return
    ensure_model(fam)
    while True:
        print_header_and_clear()
        print(f"{Fore.BLUE}--- Basic TTS ({fam}) ---{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Type 'b' at any prompt to return to the main menu.{Style.RESET_ALL}")
        try:
            text = _prompt_line("Text")
            if not text:
                continue
            name = _prompt_line("Output name", default="basic_tts")
            out = core.OUTPUT_DIR / core.ensure_wav_name(name)
            params = core.GenParams()
            if fam == core.MODEL_MTL:
                params.language_id = _prompt_line("language_id", default="en") or "en"
            path = core.generate_tts(text, family=fam, params=params, out_path=out)
            print(f"{Fore.GREEN}Saved {path}{Style.RESET_ALL}")
            logging.info("basic tts -> %s", path)
        except BackToMenu:
            return
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            logging.error("basic tts: %s", e, exc_info=True)
        time.sleep(2)


def menu_clone() -> None:
    fam = core.current_family() or core.MODEL_ORIGINAL
    if fam == core.MODEL_VC:
        print(f"{Fore.RED}Switch to original/turbo/mtl for cloning.{Style.RESET_ALL}")
        time.sleep(2)
        return
    ensure_model(fam)
    while True:
        print_header_and_clear()
        print(f"{Fore.BLUE}--- Voice Clone ({fam}) ---{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Type 'b' at any prompt to return to the main menu.{Style.RESET_ALL}")
        try:
            prompt = _pick_template(required=True)
            text = _prompt_line("Text to speak")
            if not text:
                continue
            name = _prompt_line("Output name", default="cloned")
            if fam == core.MODEL_TURBO:
                out = core.OUTPUT_TURBO_DIR / core.ensure_wav_name(name)
            elif fam == core.MODEL_MTL:
                out = core.OUTPUT_MTL_DIR / core.ensure_wav_name(name)
            else:
                out = core.OUTPUT_DIR / core.ensure_wav_name(name)
            params = _collect_params(fam, base=core.defaults_for_clone(fam), ask_first=True)
            n_chunks = len(core.split_text_chunks(text, params.max_chunk_chars))
            if n_chunks > 1:
                print(
                    f"{Fore.BLUE}Long text → {n_chunks} chunks (clearer pacing, fewer skips)…{Style.RESET_ALL}"
                )
            path = core.generate_tts(
                text, family=fam, audio_prompt_path=prompt, params=params, out_path=out
            )
            print(f"{Fore.GREEN}Saved {path}{Style.RESET_ALL}")
            logging.info("clone -> %s", path)
        except BackToMenu:
            return
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            logging.error("clone: %s", e, exc_info=True)
        time.sleep(2)


def menu_emotion() -> None:
    fam = core.current_family() or core.MODEL_ORIGINAL
    if fam == core.MODEL_TURBO:
        print(
            f"{Fore.YELLOW}Turbo does not support emotion/CFG. Use clone with temperature/top_k instead.{Style.RESET_ALL}"
        )
        time.sleep(3)
        return
    if fam == core.MODEL_VC:
        print(f"{Fore.RED}VC has no emotion path.{Style.RESET_ALL}")
        time.sleep(2)
        return
    ensure_model(fam)
    while True:
        print_header_and_clear()
        print(f"{Fore.BLUE}--- Emotion / CFG ({fam}) ---{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Type 'b' at any prompt to return to the main menu.{Style.RESET_ALL}")
        try:
            text = _prompt_line("Text")
            if not text:
                continue
            prompt = _pick_template(required=False)
            params = _collect_params(
                fam, base=core.defaults_for_clone(fam), ask_first=True, force=False
            )
            name = _prompt_line("Output name", default="emotional")
            out = core.OUTPUT_EMOTION_DIR / core.ensure_wav_name(name)
            path = core.generate_tts(
                text, family=fam, audio_prompt_path=prompt, params=params, out_path=out
            )
            print(f"{Fore.GREEN}Saved {path}{Style.RESET_ALL}")
        except BackToMenu:
            return
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            logging.error("emotion: %s", e, exc_info=True)
        time.sleep(2)


def menu_vc() -> None:
    ensure_model(core.MODEL_VC)
    while True:
        print_header_and_clear()
        print(f"{Fore.BLUE}--- Voice Conversion ---{Style.RESET_ALL}")
        print("Convert source speech into the target speaker's voice.")
        print(f"{Fore.WHITE}Type 'b' at any prompt to return to the main menu.{Style.RESET_ALL}")
        try:
            src = _prompt_line("Source audio path")
            if not src:
                continue
            target = _pick_template(required=True)
            name = _prompt_line("Output name", default="vc_out")
            out = core.OUTPUT_VC_DIR / core.ensure_wav_name(name)
            path = core.generate_vc(src, target, out_path=out)
            print(f"{Fore.GREEN}Saved {path}{Style.RESET_ALL}")
        except BackToMenu:
            return
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            logging.error("vc: %s", e, exc_info=True)
        time.sleep(2)


def interactive_main() -> int:
    core.ensure_output_dirs()
    print_header_and_clear()
    print(
        f"{Fore.GREEN}Starting spitztxt (chatterbox-tts {core.package_version()}). "
        f"Loading default model: original…{Style.RESET_ALL}"
    )
    try:
        ensure_model(core.MODEL_ORIGINAL)
    except Exception:
        print(
            f"{Fore.RED}Could not load original model. "
            f"You can still pick another family from the menu (5).{Style.RESET_ALL}"
        )
        time.sleep(2)

    while True:
        print_header_and_clear()
        print(f"{Fore.GREEN}Choose an option:{Style.RESET_ALL}\n")
        print(f"{Style.BRIGHT}1. Basic Text-to-Speech{Style.RESET_ALL}")
        print(f"{Style.BRIGHT}2. Voice Cloning{Style.RESET_ALL}")
        print(f"{Style.BRIGHT}3. Emotional Tone / CFG{Style.RESET_ALL}")
        print(f"{Style.BRIGHT}4. Voice Conversion (VC){Style.RESET_ALL}")
        print(f"{Style.BRIGHT}5. Select model family{Style.RESET_ALL}")
        print(f"{Style.BRIGHT}6. Unload model (free VRAM){Style.RESET_ALL}")
        print(f"{Style.BRIGHT}0. Exit{Style.RESET_ALL}")
        print(f"{Fore.WHITE}(In submenus, type 'b' anytime to come back here.){Style.RESET_ALL}")
        choice = input(f"{Fore.CYAN}Choice: {Style.RESET_ALL}").strip().lower()
        try:
            if choice == "1":
                menu_basic_tts()
            elif choice == "2":
                menu_clone()
            elif choice == "3":
                menu_emotion()
            elif choice == "4":
                menu_vc()
            elif choice == "5":
                menu_select_model()
            elif choice == "6":
                core.unload_model()
                print(f"{Fore.GREEN}Unloaded.{Style.RESET_ALL}")
                time.sleep(1)
            elif choice in ("0", "q", "quit", "exit"):
                print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
                return 0
            else:
                print(f"{Fore.RED}Invalid choice{Style.RESET_ALL}")
                time.sleep(1)
        except BackToMenu:
            continue


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="spitztxt",
        description="spitztxt — Chatterbox TTS family (original / turbo / multilingual / vc)",
    )
    p.add_argument(
        "--version",
        action="store_true",
        help="print package + CLI banner info and exit",
    )
    p.add_argument(
        "--model",
        choices=list(core.MODEL_FAMILIES),
        default=None,
        help="model family for non-interactive generate",
    )
    p.add_argument("--text", default=None, help="text to speak (TTS families)")
    p.add_argument("--prompt", default=None, help="voice reference audio path")
    p.add_argument("--source", default=None, help="source audio for VC")
    p.add_argument("--target", default=None, help="target voice for VC")
    p.add_argument("--language", default="en", help="language_id for multilingual")
    p.add_argument("-o", "--output", default=None, help="output WAV path")
    p.add_argument("--temperature", type=float, default=0.8)
    p.add_argument("--cfg-weight", type=float, default=0.5)
    p.add_argument("--exaggeration", type=float, default=0.5)
    p.add_argument("--min-p", type=float, default=0.05)
    p.add_argument("--top-p", type=float, default=1.0)
    p.add_argument("--top-k", type=int, default=1000)
    p.add_argument("--repetition-penalty", type=float, default=1.2)
    p.add_argument("--no-norm-loudness", action="store_true")
    p.add_argument(
        "--smoke",
        action="store_true",
        help="run full non-interactive smoke (all families, sequential) then exit",
    )
    p.add_argument(
        "--smoke-dir",
        default=None,
        help="directory for --smoke outputs (default: project output/ + subdirs)",
    )
    return p


def run_noninteractive(args: argparse.Namespace) -> int:
    core.ensure_output_dirs()
    if args.version:
        print(f"spitztxt CLI | chatterbox-tts {core.package_version()} | device {core.detect_device()}")
        return 0

    if args.smoke:
        return run_smoke(Path(args.smoke_dir) if args.smoke_dir else None)

    if not args.model:
        print("error: --model required for non-interactive mode (or omit all flags for interactive)", file=sys.stderr)
        return 2

    fam = args.model
    params = core.GenParams(
        temperature=args.temperature,
        cfg_weight=args.cfg_weight,
        exaggeration=args.exaggeration,
        min_p=args.min_p,
        top_p=args.top_p,
        top_k=args.top_k,
        repetition_penalty=args.repetition_penalty,
        norm_loudness=not args.no_norm_loudness,
        language_id=args.language,
    )

    try:
        core.load_model(fam)
        if fam == core.MODEL_VC:
            if not args.source or not args.target:
                print("error: VC requires --source and --target", file=sys.stderr)
                return 2
            out = args.output or str(core.OUTPUT_VC_DIR / "cli_vc.wav")
            path = core.generate_vc(args.source, args.target, out_path=out)
        else:
            if not args.text:
                print("error: TTS requires --text", file=sys.stderr)
                return 2
            if fam == core.MODEL_TURBO and not args.prompt:
                print("error: turbo requires --prompt", file=sys.stderr)
                return 2
            out = args.output
            if not out:
                sub = {
                    core.MODEL_TURBO: core.OUTPUT_TURBO_DIR,
                    core.MODEL_MTL: core.OUTPUT_MTL_DIR,
                    core.MODEL_ORIGINAL: core.OUTPUT_DIR,
                }[fam]
                out = str(sub / "cli_out.wav")
            path = core.generate_tts(
                args.text,
                family=fam,
                audio_prompt_path=args.prompt,
                params=params,
                out_path=out,
            )
        print(f"OK {path}")
        return 0
    except Exception as e:
        logging.error("noninteractive: %s", e, exc_info=True)
        print(f"error: {e}", file=sys.stderr)
        return 1
    finally:
        core.unload_model()


def run_smoke(smoke_dir: Path | None = None) -> int:
    """Sequential full-family smoke using the same helpers as the CLI."""
    core.ensure_output_dirs()
    root = Path(smoke_dir) if smoke_dir else core.REPO_ROOT / "output" / "smoke"
    root.mkdir(parents=True, exist_ok=True)
    prompt = core.VOICE_TEMPLATES_DIR / "morgan_cropped.mp3"
    kitt = core.VOICE_TEMPLATES_DIR / "kitt.mp3"
    # Turbo needs >5s reference
    turbo_prompt = prompt if prompt.is_file() else kitt
    results = []
    print(f"SMOKE start chatterbox-tts={core.package_version()} device={core.detect_device()}")

    # 1 original basic
    try:
        core.load_model(core.MODEL_ORIGINAL)
        p = core.generate_tts(
            "Systems online. Spitz text original.",
            family=core.MODEL_ORIGINAL,
            params=core.GenParams(),
            out_path=root / "smoke_original_basic.wav",
        )
        results.append(("original_basic", p, p.stat().st_size))
        print(f"OK original_basic {p} bytes={p.stat().st_size}")
    except Exception as e:
        print(f"FAIL original_basic: {e}")
        logging.error("smoke original_basic: %s", e, exc_info=True)
        results.append(("original_basic", None, 0))
    finally:
        core.unload_model()

    # 2 original clone
    try:
        core.load_model(core.MODEL_ORIGINAL)
        p = core.generate_tts(
            "Knight Rider reporting for duty.",
            family=core.MODEL_ORIGINAL,
            audio_prompt_path=kitt if kitt.is_file() else prompt,
            params=core.GenParams(exaggeration=0.6, cfg_weight=0.4),
            out_path=root / "smoke_original_clone.wav",
        )
        results.append(("original_clone", p, p.stat().st_size))
        print(f"OK original_clone {p} bytes={p.stat().st_size}")
    except Exception as e:
        print(f"FAIL original_clone: {e}")
        logging.error("smoke original_clone: %s", e, exc_info=True)
        results.append(("original_clone", None, 0))
    finally:
        core.unload_model()

    # 3 turbo clone
    try:
        core.load_model(core.MODEL_TURBO)
        p = core.generate_tts(
            "Turbo clone check. Fast and clear.",
            family=core.MODEL_TURBO,
            audio_prompt_path=turbo_prompt,
            params=core.GenParams(temperature=0.7, top_k=1000, top_p=0.95),
            out_path=root / "smoke_turbo_clone.wav",
        )
        results.append(("turbo_clone", p, p.stat().st_size))
        print(f"OK turbo_clone {p} bytes={p.stat().st_size}")
    except Exception as e:
        print(f"FAIL turbo_clone: {e}")
        logging.error("smoke turbo_clone: %s", e, exc_info=True)
        results.append(("turbo_clone", None, 0))
    finally:
        core.unload_model()

    # 4 multilingual
    try:
        core.load_model(core.MODEL_MTL)
        p = core.generate_tts(
            "Hello from multilingual spitztxt.",
            family=core.MODEL_MTL,
            audio_prompt_path=prompt if prompt.is_file() else kitt,
            params=core.GenParams(language_id="en"),
            out_path=root / "smoke_mtl_en.wav",
        )
        results.append(("mtl_en", p, p.stat().st_size))
        print(f"OK mtl_en {p} bytes={p.stat().st_size}")
    except Exception as e:
        print(f"FAIL mtl_en: {e}")
        logging.error("smoke mtl_en: %s", e, exc_info=True)
        results.append(("mtl_en", None, 0))
    finally:
        core.unload_model()

    # 5 VC — need a short source wav (use original basic if present, else generate tiny with original)
    source_wav = root / "smoke_original_basic.wav"
    if not source_wav.is_file() or source_wav.stat().st_size < 1024:
        try:
            core.load_model(core.MODEL_ORIGINAL)
            source_wav = core.generate_tts(
                "Source line for voice conversion.",
                family=core.MODEL_ORIGINAL,
                out_path=root / "smoke_vc_source.wav",
            )
            core.unload_model()
        except Exception as e:
            print(f"FAIL vc_source_prep: {e}")
            source_wav = None
            core.unload_model()

    if source_wav and source_wav.is_file():
        try:
            core.load_model(core.MODEL_VC)
            target = kitt if kitt.is_file() else prompt
            p = core.generate_vc(source_wav, target, out_path=root / "smoke_vc.wav")
            results.append(("vc", p, p.stat().st_size))
            print(f"OK vc {p} bytes={p.stat().st_size}")
        except Exception as e:
            print(f"FAIL vc: {e}")
            logging.error("smoke vc: %s", e, exc_info=True)
            results.append(("vc", None, 0))
        finally:
            core.unload_model()

    failed = [n for n, path, sz in results if path is None or sz < 1024]
    print("SMOKE summary:", results)
    if failed:
        print(f"SMOKE FAILED: {failed}")
        return 1
    print("SMOKE OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    # Interactive if no meaningful flags
    if not argv:
        return interactive_main()
    args = parser.parse_args(argv)
    # If only default-ish? any of these means non-interactive
    non_interactive = any(
        [
            args.version,
            args.smoke,
            args.model is not None,
            args.text is not None,
            args.source is not None,
        ]
    )
    if non_interactive:
        return run_noninteractive(args)
    return interactive_main()


if __name__ == "__main__":
    raise SystemExit(main())
