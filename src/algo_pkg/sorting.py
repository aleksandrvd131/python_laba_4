from collections.abc import Callable, Iterable
from itertools import chain
from typing import Any

# тип функции для извлечения ключа сравнения
type KeyFunc[T] = Callable[[T], Any]


def insertion_sort[T](items: Iterable[T], *, key: KeyFunc[T] | None = None) -> list[T]:
    # сортировка простыми вставками
    # делаем копию чтобы не менять исходные данные
    arr = list(items)
    # если задан key то заранее считаем ключи для сравнения
    keys = [key(x) for x in arr] if key is not None else arr.copy()

    # идем со второго элемента и ищем ему правильное место слева
    for i in range(1, len(arr)):
        val, k_val = arr[i], keys[i]
        j = i - 1
        # сдвигаем элементы вправо пока они больше текущего
        while j >= 0 and keys[j] > k_val:
            arr[j + 1] = arr[j]
            keys[j + 1] = keys[j]
            j -= 1
        # ставим элемент на найденное место
        arr[j + 1] = val
        keys[j + 1] = k_val
    return arr


def heap_sort[T](items: Iterable[T], *, key: KeyFunc[T] | None = None) -> list[T]:
    # пирамидальная сортировка с помощью кучи
    arr = list(items)
    keys = [key(x) for x in arr] if key is not None else arr.copy()
    n = len(arr)

    # просеивание элемента вниз чтобы восстановить свойства кучи
    def sift_down(start: int, end: int) -> None:
        root = start
        while (left := 2 * root + 1) < end:
            largest = root
            # сравниваем с левым потомком
            if keys[left] > keys[largest]:
                largest = left
            # если есть правый потомок и он еще больше то берем его
            if (right := left + 1) < end and keys[right] > keys[largest]:
                largest = right
            # если корень и так самый большой то все на своих местах
            if largest == root:
                return
            # меняем местами с наибольшим потомком
            arr[root], arr[largest] = arr[largest], arr[root]
            keys[root], keys[largest] = keys[largest], keys[root]
            root = largest

    # строим начальную кучу снизу вверх
    for i in range(n // 2 - 1, -1, -1):
        sift_down(i, n)
    # по очереди достаем максимум в конец и чиним оставшуюся кучу
    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        keys[0], keys[end] = keys[end], keys[0]
        sift_down(0, end)
    return arr


def radix_sort(arr: list[int] | Iterable[int], *, bits: int = 8) -> list[int]:
    res_input = list(arr)
    if len(res_input) <= 1:
        return list(res_input)

    min_val = min(res_input)
    max_val = max(res_input)
    if min_val == max_val:
        return list(res_input)

    # Если есть отрицательные числа, сдвигаем диапазон в неотрицательную область
    offset = min(0, min_val)
    if offset:
        res = [x - offset for x in res_input]
        max_val -= offset
    else:
        res = list(res_input)

    base = 1 << bits
    mask = base - 1
    from_iter = chain.from_iterable

    buckets: list[list[int]] = [[] for _ in range(base)]
    # Кэшируем ссылки на метод .append для ускорения цикла
    appends = [b.append for b in buckets]

    # Первый проход (shift == 0 — экономим на битовом сдвиге)
    for x in res:
        appends[x & mask](x)
    res = list(from_iter(buckets))

    # Остальные проходы
    shift = bits
    while max_val >> shift:
        for b in buckets:
            b.clear()
        for x in res:
            appends[(x >> shift) & mask](x)
        res = list(from_iter(buckets))
        shift += bits

    if offset:
        res = [x + offset for x in res]

    return res
