"""Tests for DOS/PDOS workflow bridges."""

import pytest
from aiida.common.exceptions import NotExistent

from aiida_abacus.workflows.band import AbacusBandWorkChain
from aiida_abacus.workflows.dos import AbacusDosWorkChain, AbacusPdosWorkChain


def test_run_bands_flag_compatibility():
    """Support both `run_bands` and the legacy `run_band` toggle."""

    assert AbacusBandWorkChain._should_run_bands_from_settings({"run_bands": True}) is True
    assert AbacusBandWorkChain._should_run_bands_from_settings({"run_bands": False}) is False
    assert AbacusBandWorkChain._should_run_bands_from_settings({"run_band": False}) is False
    assert AbacusBandWorkChain._should_run_bands_from_settings({}) is True


@pytest.mark.parametrize("workflow_cls", [AbacusDosWorkChain, AbacusPdosWorkChain])
def test_dos_like_builder_defaults(workflow_cls, abacus_code, si_structure, pseudo_family_v2):
    """DOS-like builders disable band paths and enable DOS by default."""

    _ = pseudo_family_v2

    try:
        builder = workflow_cls.get_builder_from_protocol(
            code=abacus_code,
            structure=si_structure,
            protocol="fast",
            overrides={"base": {"pseudo_family": "apns-efficiency-test"}},
        )
    except (NotExistent, ValueError):
        pytest.skip("Pseudopotential family not available")

    assert builder.band_settings["run_bands"] is False
    assert builder.band_settings["run_dos"] is True
