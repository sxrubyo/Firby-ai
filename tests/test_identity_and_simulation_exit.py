import sys
from pathlib import Path

ROOT = Path("/home/ubuntu/firby")
sys.path.insert(0, str(ROOT))

import pytest
from src.firby.utils.helpers import is_negative

def test_simulation_exit_is_negative_detection():
    # Verify is_negative includes 'salte' to catch user commands like "salte de la simulacion"
    assert is_negative("salte de la simulacion") is True
    assert is_negative("salte") is True
    assert is_negative("salir") is True
    assert is_negative("cancelar") is True


