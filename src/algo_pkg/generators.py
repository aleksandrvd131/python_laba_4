import random


def random_list(n: int, *, seed: int | None = None) -> list[int]:
    """Генерация списка случайных чисел размера n в диапазоне [-n, n]."""
    rng = random.Random(seed)
    return [rng.randint(-n, n) for _ in range(n)]


def sorted_list(n: int, *, seed: int | None = None) -> list[int]:
    """Генерация отсортированного списка из n последовательных чисел."""
    _ = seed
    start = -(n // 2)
    return list(range(start, start + n))


def reversed_list(n: int, *, seed: int | None = None) -> list[int]:
    """Генерация списка из n чисел, отсортированного по убыванию."""
    _ = seed
    return sorted_list(n)[::-1]


def nearly_sorted_list(n: int, *, swaps: int | None = None, seed: int | None = None) -> list[int]:
    """Генерация почти отсортированного списка с несколькими перестановками."""
    rng = random.Random(seed)
    arr = sorted_list(n)
    if n < 2:
        return arr
    num_swaps = swaps if swaps is not None else max(1, n // 20)
    for _ in range(num_swaps):
        i, j = rng.randrange(n), rng.randrange(n)
        arr[i], arr[j] = arr[j], arr[i]
    return arr


def many_duplicates_list(n: int, *, unique_values: int = 5, seed: int | None = None) -> list[int]:
    """Генерация списка из n чисел с ограниченным набором уникальных значений."""
    if n <= 0:
        return []
    rng = random.Random(seed)
    pool = [rng.randint(-100, 100) for _ in range(max(1, unique_values))]
    return [rng.choice(pool) for _ in range(n)]
