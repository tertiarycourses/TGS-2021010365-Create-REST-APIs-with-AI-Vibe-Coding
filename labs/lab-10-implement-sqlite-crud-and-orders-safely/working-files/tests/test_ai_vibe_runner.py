from pathlib import Path

import pytest

from ai_vibe import CodeBundle, GeneratedFile, safe_output_path, write_bundle


def test_write_bundle_keeps_files_under_generated(tmp_path: Path):
    bundle = CodeBundle(
        summary="demo",
        assumptions=["learner will run tests"],
        files=[GeneratedFile(path="app/generated_demo.py", purpose="test", content="VALUE = 1\n")],
        verification_steps=["pytest -q"],
    )
    written = write_bundle(bundle, tmp_path / "generated")
    assert written == ["app/generated_demo.py"]
    assert (tmp_path / "generated" / "app" / "generated_demo.py").read_text() == "VALUE = 1\n"


@pytest.mark.parametrize("path", ["../escape.py", "/tmp/escape.py", "unsafe.exe"])
def test_generated_paths_are_rejected(tmp_path: Path, path: str):
    with pytest.raises(ValueError):
        safe_output_path(tmp_path / "generated", path)
