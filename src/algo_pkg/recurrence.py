def _validate_n(n: int) -> None:
    if type(n) is not int:
        raise TypeError("n должно быть целым числом")
    if n < 0:
        raise ValueError("n должно быть неотрицательным")


def fibonacci_iterative(n: int) -> int:
    """Итеративное вычисление n-го числа Фибоначчи.

    Сложность: O(n) по времени, O(1) по памяти.
    """
    _validate_n(n)
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def fibonacci_recursive(n: int) -> int:
    """Рекурсивное вычисление n-го числа Фибоначчи с хвостовым шагом."""
    _validate_n(n)

    def _step(k: int, a: int = 0, b: int = 1) -> int:
        return a if k == 0 else _step(k - 1, b, a + b)

    return _step(n)
