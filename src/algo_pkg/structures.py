class EmptyStackError(IndexError):
    # ошибка когда стек пустой
    pass


class Stack:
    # стек lifo на списке
    def __init__(self) -> None:
        self.data: list = []

    def push(self, item) -> None:
        # положить элемент на вершину
        self.data.append(item)

    def pop(self):
        # достать элемент с вершины
        if not self.data:
            raise EmptyStackError("нельзя делать pop из пустого стека")
        return self.data.pop()

    def peek(self):
        # посмотреть верхний элемент
        if not self.data:
            raise EmptyStackError("стек пустой")
        return self.data[-1]

    def __len__(self) -> int:
        return len(self.data)

    def __bool__(self) -> bool:
        return bool(self.data)

    def __repr__(self) -> str:
        return f"Stack({self.data})"
