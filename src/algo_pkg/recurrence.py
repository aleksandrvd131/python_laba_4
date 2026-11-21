# проверка входного n на корректность
def _validate_n(n: int) -> None:
    # проверяем что передали именно целое число
    if type(n) is not int:
        raise TypeError("n должно быть целым числом")
    # отрицательные числа передавать нельзя
    if n < 0:
        raise ValueError("n должно быть неотрицательным")


def fibonacci_iterative(n: int) -> int:
    # вычисление фибоначчи через обычный цикл
    _validate_n(n)
    # стартовые два числа ряда
    a, b = 0, 1
    for _ in range(n):
        # сдвигаем числа на каждом шаге
        a, b = b, a + b
    return a


def fibonacci_recursive(n: int) -> int:
    # рекурсивное вычисление фибоначчи
    _validate_n(n)

    # вспомогательный шаг с аккумулятором чтобы не забивать стек вызовов
    def _step(k: int, a: int = 0, b: int = 1) -> int:
        return a if k == 0 else _step(k - 1, b, a + b)

    return _step(n)
