#!/usr/bin/env python3
"""Generate a reviewable FastAPI code bundle with the OpenAI Python SDK.

The script never overwrites working source.  It writes only validated relative
paths below generated/ so learners can inspect, test and selectively apply the
draft.  Run --dry-run first to inspect the exact request without an API call.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath

from pydantic import BaseModel, Field


class GeneratedFile(BaseModel):
    path: str = Field(description="Safe project-relative output path")
    purpose: str = Field(description="Why this file is needed")
    content: str = Field(description="Complete file content, without Markdown fences")


class CodeBundle(BaseModel):
    summary: str
    assumptions: list[str]
    files: list[GeneratedFile]
    verification_steps: list[str]


SAFE_SUFFIXES = {".py", ".md", ".json", ".html", ".css", ".js", ".sql", ".txt", ".toml", ".yaml", ".yml"}


def _asset(root: Path, filename: str) -> Path:
    candidates = [root / filename, root / "prompts" / filename, root.parent / filename]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"Required lab asset not found: {filename}")


def _project_context(project: Path, limit: int = 120_000) -> str:
    parts: list[str] = []
    used = 0
    for path in sorted(project.rglob("*")):
        if not path.is_file() or any(p in {"generated", ".venv", "__pycache__", ".pytest_cache"} for p in path.parts):
            continue
        if path.suffix.lower() not in SAFE_SUFFIXES or path.name in {"mock-data.json", "generation-manifest.json"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        block = f"\n=== CURRENT FILE: {path.relative_to(project).as_posix()} ===\n{text}\n"
        if used + len(block) > limit:
            break
        parts.append(block); used += len(block)
    return "".join(parts)


def read_bundle(response) -> CodeBundle:
    direct = getattr(response, "output_parsed", None)
    if isinstance(direct, CodeBundle):
        return direct
    for output in getattr(response, "output", []):
        if getattr(output, "type", None) != "message":
            continue
        for item in getattr(output, "content", []):
            parsed = getattr(item, "parsed", None)
            if isinstance(parsed, CodeBundle):
                return parsed
    raise RuntimeError("The SDK response did not contain a parsed CodeBundle")


def safe_output_path(output_root: Path, relative: str) -> Path:
    posix = PurePosixPath(relative)
    if posix.is_absolute() or ".." in posix.parts or not posix.parts:
        raise ValueError(f"Unsafe generated path: {relative}")
    if posix.suffix.lower() not in SAFE_SUFFIXES:
        raise ValueError(f"Generated file type is not allowed: {relative}")
    target = output_root.joinpath(*posix.parts)
    resolved_root = output_root.resolve()
    if resolved_root not in target.resolve().parents:
        raise ValueError(f"Generated path escapes output folder: {relative}")
    return target


def write_bundle(bundle: CodeBundle, output_root: Path) -> list[str]:
    output_root.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for generated in bundle.files:
        target = safe_output_path(output_root, generated.path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(generated.content, encoding="utf-8")
        written.append(target.relative_to(output_root).as_posix())
    manifest = {
        "summary": bundle.summary,
        "assumptions": bundle.assumptions,
        "files": written,
        "verification_steps": bundle.verification_steps,
    }
    (output_root / "generation-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview the exact request without calling the API")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-5-mini"))
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    project = root / "working-files" if (root / "working-files").is_dir() else root
    prompt_path = _asset(root, "Prompts.md")
    mock_path = _asset(root, "mock-data.json")
    prompt = prompt_path.read_text(encoding="utf-8")
    mock_data = json.loads(mock_path.read_text(encoding="utf-8"))
    developer = (
        "You are a senior FastAPI engineer. Return a typed CodeBundle only. "
        "Use complete file contents, project-relative paths, parameterized SQL, no secrets, "
        "and tests that prove the requested behaviour. Do not claim a test passed unless the learner runs it."
    )
    user = f"{prompt}\n\nMOCK DATA\n{json.dumps(mock_data, indent=2)}\n\nCURRENT PROJECT\n{_project_context(project)}"
    request_preview = {"model": args.model, "input": [{"role": "developer", "content": developer}, {"role": "user", "content": user}], "text_format": "CodeBundle"}
    if args.dry_run:
        print(json.dumps(request_preview, indent=2)); return 0
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set. Export it in the shell; never store it in the lab files.")

    from openai import OpenAI

    response = OpenAI().responses.parse(
        model=args.model,
        input=request_preview["input"],
        text_format=CodeBundle,
    )
    bundle = read_bundle(response)
    written = write_bundle(bundle, project / "generated")
    print(f"Generated {len(written)} reviewable file(s) under {project / 'generated'}")
    for path in written:
        print(f"  - {path}")
    print("Review the generated diff, run tests, and copy only accepted changes into the working source.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
