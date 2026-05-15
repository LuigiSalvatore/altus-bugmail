# ---------------------------------------------------------------------------
# Application State Service
# ---------------------------------------------------------------------------
# Centralized state container with threading lock.
# All route handlers access state through this module.

import threading
from backend.services.persistence import load_config, load_data


_state = {
    'config': load_config(),
    'data': load_data(),
    'lock': threading.Lock()
}


def get_state():
    """Return the shared state dictionary.
    
    Callers should acquire _state['lock'] before reading/writing 
    'config' or 'data'.
    """
    return _state
