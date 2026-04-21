"""
DOS/PDOS workflow bridges reusing the band workflow implementation.
"""

from .band import AbacusBandWorkChain


class AbacusDosWorkChain(AbacusBandWorkChain):
    """Workflow bridge for DOS calculations."""

    _protocol_tag = "dos"


class AbacusPdosWorkChain(AbacusBandWorkChain):
    """Workflow bridge for PDOS-like calculations."""

    _protocol_tag = "pdos"
