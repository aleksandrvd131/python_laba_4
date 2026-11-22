import random


def random_list(
    n: int,
    *,
    min_val: int = -100_000_000,
    max_val: int = 100_000_000,
    seed: int | None = None,
) -> list[int]:
    # список случайных чисел
    rng = random.Random(seed)
    return [rng.randint(min_val, max_val) for _ in range(n)]


def sorted_list(n: int, *, seed: int | None = None) -> list[int]:
    # отсортированный список
    _ = seed
    start = -(n // 2)
    return list(range(start, start + n))


def reversed_list(n: int, *, seed: int | None = None) -> list[int]:
    # список наоборот через срез [::-1]
    _ = seed
    return sorted_list(n)[::-1]


def nearly_sorted_list(n: int, *, swaps: int | None = None, seed: int | None = None) -> list[int]:
    # почти отсортированный список со случайными свапами
    rng = random.Random(seed)
    arr = sorted_list(n)
    if n < 2:
        return arr
    # если не передали число перестановок, берем 5% от размера
    count = swaps if swaps is not None else max(1, n // 20)
    for _ in range(count):
        i, j = rng.randrange(n), rng.randrange(n)
        arr[i], arr[j] = arr[j], arr[i]
    return arr


def many_duplicates_list(n: int, *, unique_values: int = 5, seed: int | None = None) -> list[int]:
    # список где куча повторяющихся значений
    if n <= 0:
        return []
    rng = random.Random(seed)
    pool = [rng.randint(-100, 100) for _ in range(max(1, unique_values))]
    return [rng.choice(pool) for _ in range(n)]
