from collections.abc import Callable, Iterable
from typing import Any

type KeyFunc[T] = Callable[[T], Any]


def insertion_sort[T](items: Iterable[T], *, key: KeyFunc[T] | None = None) -> list[T]:
    # обычная сортировка вставками
    a = list(items)
    k = key or (lambda x: x)
    # по-питонски через enumerate вместо range(1, len(a)) и a[i]
    for i, val in enumerate(a[1:], start=1):
        j = i - 1
        # пока элемент слева больше текущего, двигаем его вправо
        while j >= 0 and k(a[j]) > k(val):
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = val
    return a


def heap_sort[T](items: Iterable[T], *, key: KeyFunc[T] | None = None) -> list[T]:
    # пирамидальная сортировка
    a = list(items)
    n = len(a)
    k = key or (lambda x: x)

    # просеивание вниз
    def sift_down(root: int, end: int) -> None:
        while (left := 2 * root + 1) < end:
            # ищем кто больше - левый или правый потомок (через морж :=)
            largest = right if (right := left + 1) < end and k(a[right]) > k(a[left]) else left
            if k(a[root]) >= k(a[largest]):
                break
            a[root], a[largest] = a[largest], a[root]
            root = largest

    # строим начальную кучу (reversed(range(...)) вместо сишного range(n//2 - 1, -1, -1))
    for i in reversed(range(n // 2)):
        sift_down(i, n)

    # вытаскиваем максимум в конец
    for i in reversed(range(1, n)):
        a[0], a[i] = a[i], a[0]
        sift_down(0, i)

    return a


def radix_sort(arr: list[int] | Iterable[int], *, bits: int = 8) -> list[int]:
    # поразрядная сортировка (LSD)
    items = list(arr)
    if len(items) <= 1:
        return items

    # делим на отрицательные и неотрицательные (только списки ссылок, без создания новых int в памяти!)
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
        # разрядность максимального по модулю отрицательного числа
        w = (-min_val).bit_length()
        w = ((w + bits - 1) // bits) * bits
        buckets: list[list[int]] = [[] for _ in range(base)]
        cur = lst
        for shift in range(0, w, bits):
            for b in buckets:
                b.clear()
            for x in cur:
                # в питоне сдвиг отрицательных чисел дает биты дополнительного кода
                buckets[(x >> shift) & mask].append(x)
            cur = [x for b in buckets for x in b]
        return cur

    return sort_negatives(neg) + sort_unsigned(pos)
