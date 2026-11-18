class EmptyStackError(IndexError):
    """Исключение при извлечении или просмотре элемента из пустого стека."""


class Stack[T]:
    """Стек (LIFO) на основе встроенного списка Python."""

    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        if not self._items:
            raise EmptyStackError("pop из пустого стека")
        return self._items.pop()

    def peek(self) -> T:
        if not self._items:
            raise EmptyStackError("peek из пустого стека")
        return self._items[-1]

    def __len__(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return bool(self._items)

    def __repr__(self) -> str:
        return f"Stack({self._items!r})"
