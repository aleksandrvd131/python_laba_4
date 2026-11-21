class EmptyStackError(IndexError):
    # исключение если пытаемся достать что-то из пустого стека
    pass


class Stack[T]:
    # реализация стека поверх стандартного списка питона

    def __init__(self) -> None:
        # внутри храним элементы в обычном списке
        self._items: list[T] = []

    def push(self, item: T) -> None:
        # кладем элемент на вершину стека
        self._items.append(item)

    def pop(self) -> T:
        # достаем и удаляем верхний элемент если стек не пустой
        if not self._items:
            raise EmptyStackError("pop из пустого стека")
        return self._items.pop()

    def peek(self) -> T:
        # просто смотрим верхний элемент без удаления
        if not self._items:
            raise EmptyStackError("peek из пустого стека")
        return self._items[-1]

    def __len__(self) -> int:
        # размер стека
        return len(self._items)

    def __bool__(self) -> bool:
        # проверка пустой стек или нет
        return bool(self._items)

    def __repr__(self) -> str:
        # строковое представление для отладки
        return f"Stack({self._items!r})"
