"""Loaded by child Python processes of a guarded spec run (hermetic_guard puts this dir on PYTHONPATH)."""
import os

if os.environ.get('HERMETIC_GUARD') == '1':
    import hermetic_guard

    hermetic_guard.install()
