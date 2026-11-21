from collections.abc import Callable, Iterable
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
