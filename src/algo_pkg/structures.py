class EmptyStackError(IndexError):
    # ошибка когда стек пустой
    pass


class Stack[T]:
    # реализация LIFO стека на списках
    def __init__(self) -> None:
        self.data: list[T] = []

    def push(self, item: T) -> None:
        self.data.append(item)

    def pop(self) -> T:
        if not self.data:
            raise EmptyStackError("нельзя делать pop из пустого стека")
        return self.data.pop()

    def peek(self) -> T:
        if not self.data:
            raise EmptyStackError("стек пустой")
        return self.data[-1]

    def __len__(self) -> int:
        return len(self.data)

    def __bool__(self) -> bool:
        # по-питонски: пустой список сам по себе False
        return bool(self.data)

    def __repr__(self) -> str:
        return f"Stack({self.data})"
