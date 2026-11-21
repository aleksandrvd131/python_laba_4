import argparse
import random
import sys
import time

from algo_pkg.benchmark import SIZES, run_benchmark
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

# генераторы тестовых данных
GENERATORS = {
    "random": random_list,
    "sorted": sorted_list,
    "reversed": reversed_list,
    "nearly_sorted": nearly_sorted_list,
    "duplicates": many_duplicates_list,
}

# алгоритмы сортировки
SORTS = {"insertion": insertion_sort, "heap": heap_sort}


def _run_fib(n: int, mode: str) -> None:
    # запуск расчета чисел фибоначчи
    if mode in ("iter", "both"):
        print(f"iterative({n}) = {fibonacci_iterative(n)}")
    if mode in ("rec", "both"):
        try:
            print(f"recursive({n}) = {fibonacci_recursive(n)}")
        except RecursionError:
            print(f"recursive({n}) -> RecursionError (превышен лимит стека Python)")


def _run_sort(algo: str, dataset: str, size: int, seed: int | None) -> None:
    # запуск сортировки с замером времени и сверкой результата
    actual_seed = seed if seed is not None else random.randint(1, 1_000_000)
    data = GENERATORS[dataset](size, seed=actual_seed)
    expected = sorted(data)
    print(f"\nВход ({dataset}, n={size}, seed={actual_seed}):\n{data}")

    targets = SORTS.items() if algo == "both" else [(algo, SORTS[algo])]
    for name, fn in targets:
        t0 = time.perf_counter()
        res = fn(data)
        dt = (time.perf_counter() - t0) * 1000
        # сверяем результат со стандартной сортировкой питона
        status = "OK" if res == expected else "MISMATCH"
        print(f"{name:10} [{status}, {dt:.3f} ms]: {res}")
    print(f"\n[Воспроизводимость] Чтобы повторить этот же набор, используйте seed={actual_seed}:")
    print(f"  algo sort --dataset {dataset} --size {size} --seed {actual_seed}")


def _run_stack(items: list[str]) -> None:
    # проверка работы со стеком
    stack = Stack[str]()
    print(f"Пустой стек: bool={bool(stack)}, len={len(stack)}")
    # последовательно закидываем элементы
    for item in items:
        stack.push(item)
        print(f"push({item!r}) -> peek={stack.peek()!r}, len={len(stack)}")
    # вытаскиваем пока не опустеет
    while stack:
        print(f"pop() -> {stack.pop()!r}, len={len(stack)}")
    # проверяем обработку ошибки на пустом стеке
    try:
        stack.pop()
    except EmptyStackError as exc:
        print(f"pop() на пустом стеке -> {type(exc).__name__}: {exc}")


def _run_tests(target: str) -> None:
    # запуск тестов pytest
    import pytest

    args = ["-v"] if target == "all" else ["-v", "-k", target]
    raise SystemExit(pytest.main(args))


def _run_gen(gen_type: str, size: int, seed: int | None) -> None:
    # запуск генератора с пояснением назначения набора данных
    actual_seed = seed if seed is not None else random.randint(1, 1_000_000)
    data = GENERATORS[gen_type](size, seed=actual_seed)
    desc_map = {
        "random": "Случайные числа (от -1 млн до 1 млн): базовый тест для проверки среднего случая.",
        "sorted": "Отсортированный список: лучший случай для insertion_sort (O(n)).",
        "reversed": "Обратный порядок (по убыванию): худший случай для insertion_sort (O(n²)).",
        "nearly_sorted": "Почти отсортированный список (с несколькими перестановками): проверка устойчивости.",
        "duplicates": "Список с повторяющимися значениями: проверка поведения при одинаковых элементах.",
    }
    print(f"\n[Генератор: {gen_type}]")
    print(f"Назначение: {desc_map.get(gen_type, '')}")
    print(f"Сгенерированный набор (n={size}, seed={actual_seed}):\n{data}\n")
    print(f"[Воспроизводимость] Использован seed: {actual_seed}")
    print(f"  Повторить генерацию: algo gen --type {gen_type} --size {size} --seed {actual_seed}")
    print(f"  Отсортировать набор: algo sort --dataset {gen_type} --size {size} --seed {actual_seed}")


def _ask_seed() -> str | None:
    # запрос режима работы с seed для воспроизводимости
    print(
        "\nРежим seed (воспроизводимость):\n"
        "  1. Сгенерировать новый случайный seed\n"
        "  2. Ввести свой seed вручную (для повтора данных)"
    )
    choice = input("Выбор [1/2, по умолчанию 1]: ").strip()
    if choice == "2":
        raw_seed = input("Введите целое число для seed: ").strip()
        if raw_seed.lstrip("-").isdigit():
            return raw_seed
        print("Некорректный ввод, будет сгенерирован случайный seed.")
    return None


def _interactive_argv() -> list[str]:
    # простое меню если скрипт запустили без параметров в консоли
    menu = {"1": "fib", "2": "sort", "3": "stack", "4": "gen", "5": "bench", "6": "test"}
    print(
        "Выберите модуль для проверки:\n"
        "  1. Фибоначчи (fib)\n"
        "  2. Сортировки (sort)\n"
        "  3. Стек (stack)\n"
        "  4. Генераторы наборов (gen)\n"
        "  5. Бенчмарк (bench)\n"
        "  6. Автотесты pytest (test)"
    )
    raw_choice = input("Номер [1-6]: ").strip()
    cmd = menu.get(raw_choice, "test")

    if cmd == "sort":
        print(
            "\nВыберите тип входного набора данных:\n"
            "  1. random (случайный)\n"
            "  2. sorted (отсортированный, O(n) для вставок)\n"
            "  3. reversed (обратный порядок, худший случай O(n²))\n"
            "  4. nearly_sorted (почти отсортированный)\n"
            "  5. duplicates (множество одинаковых значений)"
        )
        ds_choice = input("Тип набора [1-5, по умолчанию 1]: ").strip()
        ds_map = {"1": "random", "2": "sorted", "3": "reversed", "4": "nearly_sorted", "5": "duplicates"}
        dataset = ds_map.get(ds_choice, "random")

        raw_size = input("Количество чисел в массиве [по умолчанию 20]: ").strip()
        args = ["sort", "--dataset", dataset]
        if raw_size.isdigit() and int(raw_size) >= 0:
            args.extend(["--size", raw_size])

        seed = _ask_seed()
        if seed is not None:
            args.extend(["--seed", seed])

        return args

    if cmd == "fib":
        raw_n = input("Число n для Фибоначчи [по умолчанию 10]: ").strip()
        args = ["fib"]
        if raw_n.isdigit():
            args.append(raw_n)
        return args

    if cmd == "gen":
        print(
            "\nВыберите тип генерируемого набора:\n"
            "  1. random - случайные числа от -1 млн до 1 млн\n"
            "  2. sorted - отсортированный по возрастанию\n"
            "  3. reversed - отсортированный по убыванию\n"
            "  4. nearly_sorted - почти отсортированный\n"
            "  5. duplicates - с большим количеством дубликатов"
        )
        g_choice = input("Номер [1-5, по умолчанию 1]: ").strip()
        g_map = {"1": "random", "2": "sorted", "3": "reversed", "4": "nearly_sorted", "5": "duplicates"}
        gen_type = g_map.get(g_choice, "random")

        raw_size = input("Размер набора [по умолчанию 15]: ").strip()
        args = ["gen", "--type", gen_type]
        if raw_size.isdigit() and int(raw_size) >= 0:
            args.extend(["--size", raw_size])

        seed = _ask_seed()
        if seed is not None:
            args.extend(["--seed", seed])

        return args

    if cmd == "bench":
        raw_rep = input("Количество повторов [по умолчанию 5]: ").strip()
        args = ["bench"]
        if raw_rep.isdigit() and int(raw_rep) > 0:
            args.extend(["--repeats", raw_rep])
        return args

    return [cmd]

    return [cmd]


def build_parser() -> argparse.ArgumentParser:
    # парсер аргументов командной строки
    parser = argparse.ArgumentParser(prog="algo", description="CLI для тестирования algo-pkg")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # подкоманда для фибоначчи
    p_fib = sub.add_parser("fib", help="Проверить числа Фибоначчи")
    p_fib.add_argument("n", nargs="?", type=int, default=10)
    p_fib.add_argument("--mode", choices=("iter", "rec", "both"), default="both")

    # подкоманда для сортировок
    p_sort = sub.add_parser("sort", help="Проверить сортировки")
    p_sort.add_argument("--algo", choices=("insertion", "heap", "both"), default="both")
    p_sort.add_argument("--dataset", choices=tuple(GENERATORS), default="random")
    p_sort.add_argument("--size", type=int, default=20)
    p_sort.add_argument("--seed", type=int, default=None)

    # подкоманда для стека
    p_stack = sub.add_parser("stack", help="Проверить стек (LIFO)")
    p_stack.add_argument("items", nargs="*", default=["A", "B", "C"])

    # подкоманда для генераторов
    p_gen = sub.add_parser("gen", help="Сгенерировать тестовый набор")
    p_gen.add_argument("--type", choices=tuple(GENERATORS), default="random")
    p_gen.add_argument("--size", type=int, default=15)
    p_gen.add_argument("--seed", type=int, default=None)

    # подкоманда для бенчмарка
    p_bench = sub.add_parser("bench", help="Запустить бенчмарк")
    p_bench.add_argument("--repeats", type=int, default=5)
    p_bench.add_argument("--sizes", nargs="+", type=int, default=None)
    p_bench.add_argument("--output", type=str, default="benchmark_results.md")

    # подкоманда для тестов
    p_test = sub.add_parser("test", help="Запустить pytest по выбранной категории")
    p_test.add_argument("target", nargs="?", choices=("all", "fib", "sort", "stack", "gen"), default="all")

    return parser


def main(argv: list[str] | None = None) -> None:
    # точка входа
    raw_args = sys.argv[1:] if argv is None else argv
    # если ничего не передали запускаем менюшку
    if not raw_args:
        raw_args = _interactive_argv()

    args = build_parser().parse_args(raw_args)
    # вызываем нужную команду по названию
    match args.cmd:
        case "fib":
            _run_fib(args.n, args.mode)
        case "sort":
            _run_sort(args.algo, args.dataset, args.size, args.seed)
        case "stack":
            _run_stack(args.items)
        case "gen":
            _run_gen(args.type, args.size, args.seed)
        case "bench":
            sizes = tuple(args.sizes) if args.sizes else SIZES
            run_benchmark(repeats=args.repeats, sizes=sizes, output_file=args.output)
        case "test":
            _run_tests(args.target)


if __name__ == "__main__":
    main()
