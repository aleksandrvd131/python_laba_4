import random


def random_list(
    n: int,
    *,
    min_val: int = -100000000,
    max_val: int = 100000000,
    seed: int | None = None,
) -> list[int]:
    # список случайных чисел размера n от min_val до max_val (по умолчанию от -1 000 000 до 1 000 000)
    # отдельный генератор чтобы не трогать глобальный random
    rng = random.Random(seed)
    return [rng.randint(min_val, max_val) for _ in range(n)]


def sorted_list(n: int, *, seed: int | None = None) -> list[int]:
    # отсортированный по возрастанию список из n чисел
    _ = seed
    # берем середину чтобы в списке были и отрицательные числа
    start = -(n // 2)
    return list(range(start, start + n))


def reversed_list(n: int, *, seed: int | None = None) -> list[int]:
    # список отсортированный по убыванию
    _ = seed
    # берем отсортированный список и просто разворачиваем его
    return sorted_list(n)[::-1]


def nearly_sorted_list(n: int, *, swaps: int | None = None, seed: int | None = None) -> list[int]:
    # почти отсортированный список с несколькими случайными перестановками
    rng = random.Random(seed)
    arr = sorted_list(n)
    # если меньше двух элементов переставлять нечего
    if n < 2:
        return arr
    # если число перестановок не задали берем 5% от размера
    num_swaps = swaps if swaps is not None else max(1, n // 20)
    for _ in range(num_swaps):
        i, j = rng.randrange(n), rng.randrange(n)
        arr[i], arr[j] = arr[j], arr[i]
    return arr


def many_duplicates_list(n: int, *, unique_values: int = 5, seed: int | None = None) -> list[int]:
    # список где очень много повторяющихся элементов
    if n <= 0:
        return []
    rng = random.Random(seed)
    # создаем небольшой набор случайных значений
    pool = [rng.randint(-100, 100) for _ in range(max(1, unique_values))]
    # заполняем список случайными элементами из этого набора
    return [rng.choice(pool) for _ in range(n)]
