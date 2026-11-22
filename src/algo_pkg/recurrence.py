def _check_n(n: int) -> None:
    # ловушка питона: bool это наследник int, проверяем строго через type
    if type(n) is not int:
        raise TypeError("n должно быть int, никаких флоатов и булов")
    if n < 0:
        raise ValueError("n не может быть меньше нуля")


def fibonacci_iterative(n: int) -> int:
    # обычный цикл
    _check_n(n)
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def fibonacci_recursive(n: int) -> int:
    # рекурсия с аккумулятором чтобы не лагало
    _check_n(n)

    def helper(k: int, a: int = 0, b: int = 1) -> int:
        return a if k == 0 else helper(k - 1, b, a + b)

    return helper(n)
