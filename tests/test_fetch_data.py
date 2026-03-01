import builtins
from pathlib import Path

from scripts.fetch_data import choose_sources, prompt_acceptance, sha256sum


def test_choose_sources_all():
    selected = choose_sources(["all"])
    assert "clinvar" in selected
    assert "pharmgkb" in selected
    assert "cpic" in selected


def test_choose_sources_subset():
    selected = choose_sources(["clinvar", "cpic"])
    assert selected == ["clinvar", "cpic"]


def test_prompt_acceptance_auto_accept():
    assert prompt_acceptance("clinvar", auto_accept=True) is True


def test_prompt_acceptance_yes(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda _: "yes")
    assert prompt_acceptance("clinvar", auto_accept=False) is True


def test_prompt_acceptance_no(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda _: "no")
    assert prompt_acceptance("clinvar", auto_accept=False) is False


def test_sha256sum(tmp_path: Path):
    f = tmp_path / "sample.txt"
    f.write_text("genetic-health-ce", encoding="utf-8")
    digest = sha256sum(f)
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)
