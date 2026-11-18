from collections.abc import Callable, Iterable
from typing import Any

type KeyFunc[T] = Callable[[T], Any]


def insertion_sort[T](items: Iterable[T], *, key: KeyFunc[T] | None = None) -> list[T]:
    """Сортировка вставками (Insertion Sort)."""
    arr = list(items)
    keys = [key(x) for x in arr] if key is not None else arr.copy()

    for i in range(1, len(arr)):
        val, k_val = arr[i], keys[i]
        j = i - 1
        while j >= 0 and keys[j] > k_val:
            arr[j + 1] = arr[j]
            keys[j + 1] = keys[j]
            j -= 1
        arr[j + 1] = val
        keys[j + 1] = k_val
    return arr


def heap_sort[T](items: Iterable[T], *, key: KeyFunc[T] | None = None) -> list[T]:
    """Пирамидальная сортировка (Heap Sort)."""
    arr = list(items)
    keys = [key(x) for x in arr] if key is not None else arr.copy()
    n = len(arr)

    def sift_down(start: int, end: int) -> None:
        root = start
        while (left := 2 * root + 1) < end:
            largest = root
            if keys[left] > keys[largest]:
                largest = left
            if (right := left + 1) < end and keys[right] > keys[largest]:
                largest = right
            if largest == root:
                return
            arr[root], arr[largest] = arr[largest], arr[root]
            keys[root], keys[largest] = keys[largest], keys[root]
            root = largest

    for i in range(n // 2 - 1, -1, -1):
        sift_down(i, n)
    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        keys[0], keys[end] = keys[end], keys[0]
        sift_down(0, end)
    return arr
