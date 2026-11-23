from collections.abc import Callable, Iterable
from typing import Any


def insertion_sort(items: Iterable[Any], *, key: Callable[[Any], Any] | None = None) -> list[Any]:
    # сортировка вставками
    a = list(items)
    k = key if key is not None else (lambda x: x)
    for i in range(1, len(a)):
        val = a[i]
        j = i - 1
        # сдвиг элементов вправо пока они больше val
        while j >= 0 and k(a[j]) > k(val):
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = val
    return a


def heap_sort(items: Iterable[Any], *, key: Callable[[Any], Any] | None = None) -> list[Any]:
    # пирамидальная сортировка
    a = list(items)
    n = len(a)
    k = key if key is not None else (lambda x: x)

    # просеивание вниз
    def sift_down(root: int, end: int) -> None:
        while True:
            left = 2 * root + 1
            if left >= end:
                break
            largest = left
            right = left + 1
            # поиск большего потомка
            if right < end and k(a[right]) > k(a[left]):
                largest = right

            if k(a[root]) >= k(a[largest]):
                break
            a[root], a[largest] = a[largest], a[root]
            root = largest

    # сборка начальной кучи
    for i in range(n // 2 - 1, -1, -1):
        sift_down(i, n)

    # корень кучи в конец
    for i in range(n - 1, 0, -1):
        a[0], a[i] = a[i], a[0]
        sift_down(0, i)

    return a


def radix_sort(
    items: Iterable[Any],
    *,
    key: Callable[[Any], Any] | None = None,
    bits: int = 8,
) -> list[Any]:
    # поразрядная сортировка lsd
    a = list(items)
    if len(a) <= 1:
        return a

    k = key if key is not None else (lambda x: x)
    base = 1 << bits
    mask = base - 1

    # сохраняем пары (элемент, числовой ключ)
    pairs: list[tuple[Any, int]] = []
    for x in a:
        val = k(x)
        # ключ для поразрядной сортировки должен быть целым числом
        if not isinstance(val, int) or isinstance(val, bool):
            raise TypeError(f"Ключ radix_sort должен быть целым числом, получен {type(val).__name__}")
        pairs.append((x, val))

    # разделение на отрицательные и положительные по ключу
    neg = [p for p in pairs if p[1] < 0]
    pos = [p for p in pairs if p[1] >= 0]

    def sort_unsigned(lst: list[tuple[Any, int]]) -> list[tuple[Any, int]]:
        if len(lst) <= 1:
            return lst
        max_val = max(p[1] for p in lst)
        buckets: list[list[tuple[Any, int]]] = [[] for _ in range(base)]
        cur = lst
        # проход по разрядам положительных чисел
        for shift in range(0, max_val.bit_length(), bits):
            for b in buckets:
                b.clear()
            for p in cur:
                buckets[(p[1] >> shift) & mask].append(p)
            cur = [p for b in buckets for p in b]
        return cur

    def sort_negatives(lst: list[tuple[Any, int]]) -> list[tuple[Any, int]]:
        if len(lst) <= 1:
            return lst
        min_val = min(p[1] for p in lst)
        # число бит под отрицательные числа
        w = (-min_val).bit_length()
        w = ((w + bits - 1) // bits) * bits
        buckets: list[list[tuple[Any, int]]] = [[] for _ in range(base)]
        cur = lst
        # сдвиг для дополнительного кода
        for shift in range(0, w, bits):
            for b in buckets:
                b.clear()
            for p in cur:
                buckets[(p[1] >> shift) & mask].append(p)
            cur = [p for b in buckets for p in b]
        return cur

    # склеиваем обе части и достаем сами элементы
    res = sort_negatives(neg) + sort_unsigned(pos)
    return [p[0] for p in res]
