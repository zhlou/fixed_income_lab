"""Small shared checks for the lesson's numerical inputs."""

from math import isfinite
from numbers import Integral, Real


def finite_real(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite real number.")
    value = float(value)
    if not isfinite(value):
        raise ValueError(f"{name} must be a finite real number.")
    return value


def positive_face_value(face_value: float) -> float:
    face_value = finite_real("face_value", face_value)
    if face_value <= 0:
        raise ValueError("face_value must be positive.")
    return face_value


def positive_frequency(frequency: int) -> int:
    if (
        isinstance(frequency, bool)
        or not isinstance(frequency, Integral)
        or frequency <= 0
    ):
        raise ValueError("frequency must be a positive integer.")
    return int(frequency)
