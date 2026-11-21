import random

import pytest

from algo_pkg.generators import (
    many_duplicates_list,
    nearly_sorted_list,
    random_list,
    reversed_list,
    sorted_list,
)
from algo_pkg.recurrence import fibonacci_iterative, fibonacci_recursive
from algo_pkg.sorting import heap_sort, insertion_sort
from algo_pkg.structures import EmptyStackError, Stack

# список сортировок для прогона тестов
SORTS = [insertion_sort, heap_sort]


# тесты для чисел фибоначчи
@pytest.mark.parametrize("fib", [fibonacci_iterative, fibonacci_recursive])
def test_fibonacci(fib):
    assert [fib(i) for i in range(8)] == [0, 1, 1, 2, 3, 5, 8, 13]
    assert fibonacci_iterative(25) == fibonacci_recursive(25)
    # проверка на отрицательное число
    with pytest.raises(ValueError):
        fib(-1)
    # проверка на дробное число
    with pytest.raises(TypeError):
        fib(3.5)  # type: ignore[arg-type]
    # проверка на булев тип
    with pytest.raises(TypeError):
        fib(True)


# тесты сортировок на граничных случаях
@pytest.mark.parametrize("sort_fn", SORTS)
@pytest.mark.parametrize(
    "data",
    [
        [],                          # пустой вход
        [42],                        # один элемент
        [-5, -1, 0, 3, 9],           # уже отсортированный + отрицательные
        [9, 3, 0, -1, -5],           # обратный порядок + отрицательные
        [4, -2, 4, 0, -2, 4, 1],     # дубликаты + отрицательные
    ],
)
def test_sorts_edge_cases(sort_fn, data):
    original = data.copy()
    assert sort_fn(data) == sorted(data)
    assert data == original  # исходный список не изменён


# проверка что сортировка случайных списков совпадает со встроенной sorted
@pytest.mark.parametrize("sort_fn", SORTS)
@pytest.mark.parametrize("seed", [1, 42, 999])
def test_sorts_random_matches_builtin(sort_fn, seed):
    data = random_list(250, seed=seed)
    original = data.copy()
    assert sort_fn(data) == sorted(data)
    assert data == original


# проверка работы параметра key и ошибок при несовместимых типах
@pytest.mark.parametrize("sort_fn", SORTS)
def test_sort_key_and_type_error(sort_fn):
    assert sort_fn(["bbb", "a", "cc"], key=len) == ["a", "cc", "bbb"]
    assert sort_fn([-10, 2, -5], key=abs) == [2, -5, -10]

    with pytest.raises(TypeError):
        sort_fn([1, "two"])  # type: ignore[list-item]


# проверка базовых операций со стеком и ошибок
def test_stack_operations_and_errors():
    s = Stack[int]()
    assert not s
    assert len(s) == 0

    # попытка достать или посмотреть из пустого стека
    with pytest.raises(EmptyStackError):
        s.pop()
    with pytest.raises(EmptyStackError):
        s.peek()

    s.push(10)
    s.push(20)
    assert bool(s)
    assert len(s) == 2
    assert s.peek() == 20
    assert s.pop() == 20
    assert s.pop() == 10
    assert not s


# проверка инварианта LIFO когда элементы выходят в обратном порядке
def test_stack_lifo_invariant():
    s = Stack[int]()
    items = [10, -5, 0, 42, 10]

    # закидываем по одному и проверяем вершину
    for idx, x in enumerate(items):
        s.push(x)
        assert len(s) == idx + 1
        assert s.peek() == x
        assert len(s) == idx + 1

    # достаем все обратно и проверяем обратный порядок
    popped = [s.pop() for _ in range(len(items))]
    assert popped == list(reversed(items))
    assert len(s) == 0
    assert not s


# проверка воспроизводимости генераторов при одинаковом сиде
@pytest.mark.parametrize(
    "gen",
    [random_list, sorted_list, reversed_list, nearly_sorted_list, many_duplicates_list],
)
def test_generators_reproducibility_and_isolation(gen):
    random.seed(0)
    first = gen(100, seed=123)
    random.seed(99999)  # изменение глобального RNG не должно влиять на результат
    second = gen(100, seed=123)
    assert first == second
    assert len(gen(0, seed=123)) == 0


# проверка что разные сиды дают разные результаты
@pytest.mark.parametrize("gen", [random_list, nearly_sorted_list, many_duplicates_list])
def test_generators_different_seeds(gen):
    assert gen(100, seed=1) != gen(100, seed=2)
