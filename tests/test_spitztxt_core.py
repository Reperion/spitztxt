"""
Tests against shipped spitztxt_core / CLI helpers.

GPU generate tests are marked and may be skipped if CUDA unavailable;
structural tests always run.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import spitztxt_core as core  # noqa: E402

NEW_PY = REPO / "venv-0.1.7" / "bin" / "python"
LEGACY_PY = REPO / "venv" / "bin" / "python"
CLI = REPO / "spitztxt-CLI.py"


def test_capabilities_matrix_covers_all_families():
    assert set(core.CAPABILITIES) == set(core.MODEL_FAMILIES)
    assert core.CAPABILITIES[core.MODEL_TURBO]["cfg"] is False
    assert core.CAPABILITIES[core.MODEL_MTL]["language_id"] is True
    assert core.CAPABILITIES[core.MODEL_VC]["vc"] is True


def test_ensure_wav_name():
    assert core.ensure_wav_name("foo") == "foo.wav"
    assert core.ensure_wav_name("foo.WAV") == "foo.WAV"


def test_split_text_chunks_short_stays_one():
    assert core.split_text_chunks("Hello there.", max_chars=160) == ["Hello there."]


def test_split_text_chunks_long_splits_sentences():
    text = (
        "First sentence is here. Second sentence follows after that. "
        "Third one also exists for good measure."
    )
    chunks = core.split_text_chunks(text, max_chars=40)
    assert len(chunks) >= 2
    assert all(len(c) <= 50 for c in chunks)  # soft bound with word wrap
    joined = " ".join(chunks)
    assert "First sentence" in joined and "Third one" in joined


def test_defaults_for_clone_near_stock():
    p = core.defaults_for_clone("original")
    # Near stock Chatterbox; light calm only (not the overly slow 0.35/0.45 set)
    assert p.temperature == 0.8
    assert p.exaggeration == 0.5
    assert 0.4 <= p.cfg_weight <= 0.5
    assert p.chunk_long_text is True


def test_resolve_prompt_templates():
    templates = core.list_voice_templates()
    assert templates, "voice-templates should contain at least one file"
    p = core.resolve_prompt("1", templates)
    assert p is not None and p.is_file()
    assert core.resolve_prompt("", templates) is None


def test_package_version_readable_in_new_env():
    if not NEW_PY.is_file():
        pytest.skip("venv-0.1.7 not installed")
    out = subprocess.check_output(
        [str(NEW_PY), "-c", "import importlib.metadata as m; print(m.version('chatterbox-tts'))"],
        text=True,
    ).strip()
    parts = [int(x) for x in out.split(".")[:3]]
    assert parts >= [0, 1, 7], out


def test_cli_version_flag_uses_new_env():
    if not NEW_PY.is_file():
        pytest.skip("venv-0.1.7 not installed")
    r = subprocess.run(
        [str(NEW_PY), str(CLI), "--version"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        check=True,
    )
    assert "chatterbox-tts" in r.stdout
    # version string like 0.1.7
    assert "0.1." in r.stdout


@pytest.mark.skipif(not NEW_PY.is_file(), reason="venv-0.1.7 missing")
def test_cli_generate_original_basic(tmp_path):
    """Drive shipped CLI entry (non-interactive) for original basic TTS."""
    out = tmp_path / "t_basic.wav"
    env = os.environ.copy()
    r = subprocess.run(
        [
            str(NEW_PY),
            str(CLI),
            "--model",
            "original",
            "--text",
            "Unit test line from spitztxt.",
            "-o",
            str(out),
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=env,
        timeout=600,
    )
    assert r.returncode == 0, r.stdout + "\n" + r.stderr
    assert out.is_file() and out.stat().st_size > 1024


@pytest.mark.skipif(not NEW_PY.is_file(), reason="venv-0.1.7 missing")
def test_generate_tts_helper_clone(tmp_path):
    """Call shipped generate_tts helper with real model (sequential)."""
    prompt = core.VOICE_TEMPLATES_DIR / "kitt.mp3"
    if not prompt.is_file():
        pytest.skip("no kitt template")
    # run under new env by re-exec if needed
    if Path(sys.executable).resolve() != NEW_PY.resolve():
        r = subprocess.run(
            [
                str(NEW_PY),
                "-c",
                f"""
import sys
sys.path.insert(0, {str(REPO)!r})
import spitztxt_core as c
c.load_model('original')
p = c.generate_tts(
    'Helper clone unit test.',
    family='original',
    audio_prompt_path={str(prompt)!r},
    params=c.GenParams(temperature=0.7),
    out_path={str(tmp_path / 'helper_clone.wav')!r},
)
assert p.stat().st_size > 1024
c.unload_model()
print('OK', p)
""",
            ],
            capture_output=True,
            text=True,
            timeout=600,
        )
        assert r.returncode == 0, r.stdout + r.stderr
        return
    core.load_model(core.MODEL_ORIGINAL)
    try:
        p = core.generate_tts(
            "Helper clone unit test.",
            family=core.MODEL_ORIGINAL,
            audio_prompt_path=prompt,
            params=core.GenParams(temperature=0.7),
            out_path=tmp_path / "helper_clone.wav",
        )
        assert p.stat().st_size > 1024
    finally:
        core.unload_model()
