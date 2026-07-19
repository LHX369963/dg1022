import pytest

from dg1022_cli.catalog import COMMANDS, get_command, render_command
from dg1022_cli.errors import ProtocolError


def test_catalog_names_unique_and_all_manual_sections_covered():
    assert len(COMMANDS) == len({item.name for item in COMMANDS})
    assert {"ieee488", "apply", "function", "frequency", "voltage", "output", "pulse", "am", "fm", "pm",
            "fsk", "sweep", "trigger", "burst", "data", "memory", "system", "phase", "display", "coupling",
            "counter"} == {item.section for item in COMMANDS}


def test_channel_rendering_matches_manual_ch2_suffix_positions():
    assert render_command(get_command("voltage.high"), 1) == "VOLTage:HIGH"
    assert render_command(get_command("voltage.high"), 2) == "VOLTage:HIGH:CH2"
    assert render_command(get_command("apply.sine"), 2) == "APPLy:SINusoid:CH2"
    assert render_command(get_command("pulse.duty"), 1) == "PULSe:DCYCle"
    assert render_command(get_command("pulse.duty"), 2) == "PULSe:DCYC:CH2"
    with pytest.raises(ProtocolError, match="requires --channel"):
        render_command(get_command("output.enabled"), None)


def test_catalog_has_106_merged_command_paths():
    assert len(COMMANDS) == 106
    assert get_command("data.load").kind == "transfer"
    expanded = sum(
        (2 if item.kind == "query-set" else 1)
        * (2 if "{ch}" in item.command or "{pulse_duty}" in item.command else 1)
        for item in COMMANDS
    )
    assert expanded == 214
