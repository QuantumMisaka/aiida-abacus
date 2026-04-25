"""Tests for DOS/PDOS workflow bridges."""

from types import SimpleNamespace

import pytest
from aiida.common.exceptions import NotExistent, NotExistentAttributeError

from aiida_abacus.workflows.band import AbacusBandWorkChain
from aiida_abacus.workflows.dos import AbacusDosWorkChain, AbacusPdosWorkChain


def test_run_bands_flag_compatibility():
    """Support both `run_bands` and the legacy `run_band` toggle."""

    assert AbacusBandWorkChain._should_run_bands_from_settings({"run_bands": True}) is True
    assert AbacusBandWorkChain._should_run_bands_from_settings({"run_bands": False}) is False
    assert AbacusBandWorkChain._should_run_bands_from_settings({"run_band": False}) is False
    assert AbacusBandWorkChain._should_run_bands_from_settings({}) is True


def test_band_workchain_defines_subprocess_exit_codes():
    assert AbacusBandWorkChain.exit_codes.ERROR_RELAX_PROCESS_FAILED.status == 401
    assert AbacusBandWorkChain.exit_codes.ERROR_SCF_PROCESS_FAILED.status == 402
    assert AbacusBandWorkChain.exit_codes.ERROR_SUB_PROC_BANDS_FAILED.status == 403
    assert AbacusBandWorkChain.exit_codes.ERROR_SUB_PROC_DOS_FAILED.status == 404


def test_verify_scf_returns_exit_code_for_non_ok_subworkflow():
    messages = []
    fake = SimpleNamespace(
        ctx=SimpleNamespace(
            scf_workchain=SimpleNamespace(
                is_excepted=False,
                is_killed=False,
                is_finished_ok=False,
                exit_status=301,
            )
        ),
        exit_codes=SimpleNamespace(ERROR_SCF_PROCESS_FAILED="scf-failed"),
        report=messages.append,
    )

    exit_code = AbacusBandWorkChain.verify_scf(fake)

    assert exit_code == "scf-failed"
    assert messages == ["SCF workchain finished with non-zero exit status: 301"]


def test_verify_scf_returns_exit_code_when_remote_folder_is_missing():
    messages = []

    class _MissingOutputs:
        def __getattr__(self, _name):
            raise NotExistentAttributeError

    fake = SimpleNamespace(
        ctx=SimpleNamespace(
            scf_workchain=SimpleNamespace(
                is_excepted=False,
                is_killed=False,
                is_finished_ok=True,
                exit_status=0,
                outputs=_MissingOutputs(),
            )
        ),
        exit_codes=SimpleNamespace(ERROR_SCF_PROCESS_FAILED="scf-failed"),
        report=messages.append,
    )

    exit_code = AbacusBandWorkChain.verify_scf(fake)

    assert exit_code == "scf-failed"
    assert messages == ["SCF workchain finished without remote_folder output"]


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
