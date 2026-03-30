"""Tests for CLI."""

from __future__ import annotations

from click.testing import CliRunner

from hidproto.cli import cli

runner = CliRunner()


def test_root_help() -> None:
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "hidproto" in result.output
    assert "devices" in result.output


def test_devices() -> None:
    result = runner.invoke(cli, ["devices"])
    assert result.exit_code == 0


def test_info_ite8910() -> None:
    result = runner.invoke(cli, ["info", "ite8910"])
    assert result.exit_code == 0
    assert "048d:8910" in result.output
    assert "wave" in result.output
    assert "breathing" in result.output


def test_info_unknown() -> None:
    result = runner.invoke(cli, ["info", "nonexistent"])
    assert result.exit_code != 0


def test_ite8910_help() -> None:
    result = runner.invoke(cli, ["ite8910", "--help"])
    assert result.exit_code == 0
    assert "wave" in result.output
    assert "breathing" in result.output
    assert "off" in result.output
    assert "brightness" in result.output
    assert "speed" in result.output


def test_ite8910_wave_help() -> None:
    result = runner.invoke(cli, ["ite8910", "wave", "--help"])
    assert result.exit_code == 0
    assert "--direction" in result.output
    assert "up_left" in result.output
    assert "right" in result.output


def test_ite8910_scan_help() -> None:
    result = runner.invoke(cli, ["ite8910", "scan", "--help"])
    assert result.exit_code == 0
    assert "--color" in result.output
    assert "--color2" in result.output


def test_ite8910_spectrum_cycle_help() -> None:
    result = runner.invoke(cli, ["ite8910", "spectrum_cycle", "--help"])
    assert result.exit_code == 0
    assert "--brightness" in result.output
    assert "--direction" not in result.output
    assert "--color" not in result.output
