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


def radix_sort(arr: Iterable[int], *, bits: int = 8) -> list[int]:
    # поразрядная сортировка lsd
    items = list(arr)
    if len(items) <= 1:
        return items

    # разделение на отрицательные и положительные
    neg = [x for x in items if x < 0]
    pos = [x for x in items if x >= 0]

    base = 1 << bits
    mask = base - 1

    def sort_unsigned(lst: list[int]) -> list[int]:
        if len(lst) <= 1:
            return lst
        max_val = max(lst)
        buckets: list[list[int]] = [[] for _ in range(base)]
        cur = lst
        for shift in range(0, max_val.bit_length(), bits):
            for b in buckets:
                b.clear()
            for x in cur:
                buckets[(x >> shift) & mask].append(x)
            cur = [x for b in buckets for x in b]
        return cur

    def sort_negatives(lst: list[int]) -> list[int]:
        if len(lst) <= 1:
            return lst
        min_val = min(lst)
        # число бит под отрицательные числа
        w = (-min_val).bit_length()
        w = ((w + bits - 1) // bits) * bits
        buckets: list[list[int]] = [[] for _ in range(base)]
        cur = lst
        for shift in range(0, w, bits):
            for b in buckets:
                b.clear()
            for x in cur:
                # сдвиг для дополнительного кода
                buckets[(x >> shift) & mask].append(x)
            cur = [x for b in buckets for x in b]
        return cur

    return sort_negatives(neg) + sort_unsigned(pos)
