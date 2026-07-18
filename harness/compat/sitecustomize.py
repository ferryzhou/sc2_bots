"""Compatibility shim auto-loaded into opponent subprocesses via PYTHONPATH.

Many downloaded AI Arena bots bundle an OLD python-sc2 whose ``sc2/distances.py``
uses ``np.float`` (and other numpy aliases removed in NumPy 1.24+). Under our
shared modern venv that raises ``AttributeError`` mid-game and the opponent
crashes at launch, so the match never happens. ``sitecustomize`` is imported
automatically at interpreter startup when it is on ``sys.path``; restoring the
deprecated aliases here -- before the bot imports its bundled sc2 -- lets that
whole cohort run without touching each bot's vendored code.
"""

try:
    import numpy as _np
    # (a) Aliases removed in NumPy 1.24 (old python-sc2's distances.py). NOT
    #     np.object/np.str/np.complex -- touching those trips a FutureWarning.
    for _name, _t in (("float", float), ("int", int), ("bool", bool),
                      ("long", int)):
        if not hasattr(_np, _name):
            setattr(_np, _name, _t)
    # (b) Trailing-underscore scalar aliases removed in NumPy 2.0.
    for _name, _alias in (("float_", "float64"), ("complex_", "complex128"),
                          ("longfloat", "longdouble"), ("unicode_", "str_"),
                          ("string_", "bytes_"), ("bool8", "bool_")):
        if not hasattr(_np, _name) and hasattr(_np, _alias):
            setattr(_np, _name, getattr(_np, _alias))
except Exception:
    pass

try:
    # fractions.gcd was removed in Python 3.9; older bot deps still import it.
    import fractions as _fr
    import math as _math
    if not hasattr(_fr, "gcd"):
        _fr.gcd = _math.gcd
except Exception:
    pass
