"""
Membership functions and fuzzy variable representations for Fuzzy Inference.
Supports Triangular, Trapezoidal, Gaussian, and Left/Right shoulder functions.
"""
from typing import Callable, Dict, List, Tuple
import numpy as np


def triangular(x: float or np.ndarray, a: float, b: float, c: float) -> float or np.ndarray:
    """
    Triangular membership function:
    a: left base
    b: peak (membership = 1.0)
    c: right base
    """
    x = np.asarray(x, dtype=float)
    y = np.zeros_like(x)

    # Left slope: a <= x <= b
    if b > a:
        left_mask = (a <= x) & (x <= b)
        y = np.where(left_mask, (x - a) / (b - a), y)
    elif b == a:
        y = np.where(x == a, 1.0, y)

    # Right slope: b < x <= c
    if c > b:
        right_mask = (b < x) & (x <= c)
        y = np.where(right_mask, (c - x) / (c - b), y)
    elif c == b:
        y = np.where(x == c, 1.0, y)

    y = np.clip(y, 0.0, 1.0)
    return float(y) if y.ndim == 0 else y


def trapezoidal(x: float or np.ndarray, a: float, b: float, c: float, d: float) -> float or np.ndarray:
    """
    Trapezoidal membership function:
    a: left foot
    b: left shoulder (membership reaches 1.0)
    c: right shoulder (membership leaves 1.0)
    d: right foot
    """
    x = np.asarray(x, dtype=float)
    y = np.zeros_like(x)

    # Left slope: a <= x < b
    if b > a:
        left_mask = (a <= x) & (x < b)
        y = np.where(left_mask, (x - a) / (b - a), y)

    # Plateau: b <= x <= c
    plateau_mask = (b <= x) & (x <= c)
    y = np.where(plateau_mask, 1.0, y)

    # Right slope: c < x <= d
    if d > c:
        right_mask = (c < x) & (x <= d)
        y = np.where(right_mask, (d - x) / (d - c), y)

    y = np.clip(y, 0.0, 1.0)
    return float(y) if y.ndim == 0 else y


class FuzzySet:
    """Represents a named linguistic term with its membership function."""
    def __init__(self, name: str, mf: Callable[[float or np.ndarray], float or np.ndarray], params: Tuple[float, ...]):
        self.name = name
        self.mf = mf
        self.params = params

    def membership(self, x: float or np.ndarray) -> float or np.ndarray:
        return self.mf(x, *self.params)


class LinguisticVariable:
    """
    Represents a Fuzzy Variable with its Universe of Discourse and Linguistic Sets.
    Example: Variable 'Budget' with Universe [0, 5000] and Sets ['Low', 'Medium', 'High'].
    """
    def __init__(self, name: str, universe: Tuple[float, float], unit: str = ""):
        self.name = name
        self.universe = universe
        self.unit = unit
        self.sets: Dict[str, FuzzySet] = {}

    def add_triangular(self, term_name: str, a: float, b: float, c: float):
        self.sets[term_name] = FuzzySet(term_name, triangular, (a, b, c))

    def add_trapezoidal(self, term_name: str, a: float, b: float, c: float, d: float):
        self.sets[term_name] = FuzzySet(term_name, trapezoidal, (a, b, c, d))

    def fuzzify(self, value: float) -> Dict[str, float]:
        """Calculates membership degree for each linguistic term of the variable."""
        # Clamp value to universe
        val_clamped = max(self.universe[0], min(self.universe[1], float(value)))
        return {term: float(fset.membership(val_clamped)) for term, fset in self.sets.items()}
