def _check_n(n: int) -> None:
    # проверка типа n (строго int, не bool)
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("n должно быть целым числом (int)")
    if n < 0:
        raise ValueError("n не может быть меньше нуля")


def fibonacci_iterative(n: int) -> int:
    # цикл для подсчета
    _check_n(n)
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def fibonacci_recursive(n: int, a: int = 0, b: int = 1) -> int:
    # рекурсия с аккумулятором
    if a == 0 and b == 1:
        _check_n(n)
    # базовый случай
    if n == 0:
        return a
    # шаг рекурсии
    return fibonacci_recursive(n - 1, b, a + b)
