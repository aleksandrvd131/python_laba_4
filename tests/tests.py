import random

import pytest

from algo_pkg.benchmark import measure, run_benchmark
from algo_pkg.generators import (
    many_duplicates_list,
    nearly_sorted_list,
    random_list,
    reversed_list,
    sorted_list,
)
from algo_pkg.recurrence import fibonacci_iterative, fibonacci_recursive
from algo_pkg.sorting import heap_sort, insertion_sort, radix_sort
from algo_pkg.structures import EmptyStackError, Stack

# список сортировок для прогона тестов
ALL_SORTS = [insertion_sort, heap_sort, radix_sort]
COMPARISON_SORTS = [insertion_sort, heap_sort]


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
@pytest.mark.parametrize("sort_fn", ALL_SORTS)
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
@pytest.mark.parametrize("sort_fn", ALL_SORTS)
@pytest.mark.parametrize("seed", [1, 42, 999])
def test_sorts_random_matches_builtin(sort_fn, seed):
    data = random_list(250, seed=seed)
    original = data.copy()
    assert sort_fn(data) == sorted(data)
    assert data == original


# проверка работы параметра key и ошибок при несовместимых типах для сортировок на сравнениях
@pytest.mark.parametrize("sort_fn", COMPARISON_SORTS)
def test_sort_key_and_type_error(sort_fn):
    assert sort_fn(["bbb", "a", "cc"], key=len) == ["a", "cc", "bbb"]
    assert sort_fn([-10, 2, -5], key=abs) == [2, -5, -10]

    with pytest.raises(TypeError):
        sort_fn([1, "two"])  # type: ignore[list-item]


# проверка поразрядной сортировки с разным размером корзин (bits)
@pytest.mark.parametrize("bits", [4, 8, 11])
def test_radix_sort_bits_and_stability(bits):
    data = random_list(1000, seed=42)
    assert radix_sort(data, bits=bits) == sorted(data)
    # проверка на списке с одинаковыми элементами
    assert radix_sort([7, 7, 7, 7], bits=bits) == [7, 7, 7, 7]


# проверка базовых операций со стеком и ошибок
def test_stack_operations_and_errors():
    s = Stack()
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
    s = Stack()
    items = [10, -5, 0, 42, 10]

    # добавление по одному и проверка вершины
    for idx, x in enumerate(items):
        s.push(x)
        assert len(s) == idx + 1
        assert s.peek() == x
        assert len(s) == idx + 1

    # извлечение всех элементов обратно
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


# тесты для модуля бенчмарка
def test_benchmark_measure_and_isolation():
    data = [5, 2, 8, 1, 9]
    original = data.copy()
    avg = measure(insertion_sort, data, repeats=3, max_single_sec=1.0)
    assert isinstance(avg, float)
    assert avg >= 0.0
    # исходный массив не должен быть изменен
    assert data == original


def test_benchmark_timeout_trigger():
    data = list(range(1000, 0, -1))
    # минимальный лимит времени для отсечки
    avg = measure(insertion_sort, data, repeats=2, max_single_sec=0.000000001)
    assert avg is None


def test_benchmark_run_small_table():
    md = run_benchmark(repeats=1, sizes=(10, 20), max_single_sec=2.5, seed=42, output_file=None)
    assert "# Результаты бенчмарка алгоритмов сортировки" in md
    assert "Лимит отсечки для $O(n^2)$:** 2.5 с" in md
    assert "Seed:** 42" in md
    assert "| Dataset | Size | Seed | insertion_sort (s) | heap_sort (s) | radix_sort (s) |" in md
    assert "| random | 10 | 42 |" in md


def test_benchmark_seed_reproducibility():
    md1 = run_benchmark(repeats=1, sizes=(10,), max_single_sec=2.5, seed=12345, output_file=None)
    md2 = run_benchmark(repeats=1, sizes=(10,), max_single_sec=2.5, seed=12345, output_file=None)
    assert "| random | 10 | 12345 |" in md1
    assert "Seed:** 12345" in md1
    # проверка структуры строк (dataset, size, seed) без учета миллисекунд
    rows1 = [line.split("|")[:4] for line in md1.splitlines() if line.startswith("| ")]
    rows2 = [line.split("|")[:4] for line in md2.splitlines() if line.startswith("| ")]
    assert rows1 == rows2


def test_benchmark_parallel_workers():
    # Проверка работы параллельного запуска (workers=2) против последовательного (workers=1)
    md_seq = run_benchmark(repeats=1, sizes=(10, 20), max_single_sec=2.0, seed=77, output_file=None, workers=1)
    md_par = run_benchmark(repeats=1, sizes=(10, 20), max_single_sec=2.0, seed=77, output_file=None, workers=2)
    assert "| random | 10 | 77 |" in md_par
    assert "| duplicates | 20 | 77 |" in md_par
    # Табличные заголовки и строки должны совпадать по структуре
    rows_seq = [line.split("|")[:4] for line in md_seq.splitlines() if line.startswith("| ")]
    rows_par = [line.split("|")[:4] for line in md_par.splitlines() if line.startswith("| ")]
    assert rows_seq == rows_par


