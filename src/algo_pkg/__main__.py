import argparse
import sys
import time

from algo_pkg.benchmark import run_benchmark
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

GENERATORS = {
    "random": random_list,
    "sorted": sorted_list,
    "reversed": reversed_list,
    "nearly_sorted": nearly_sorted_list,
    "duplicates": many_duplicates_list,
}

SORTS = {"insertion": insertion_sort, "heap": heap_sort}


def _run_fib(n: int, mode: str) -> None:
    if mode in ("iter", "both"):
        print(f"iterative({n}) = {fibonacci_iterative(n)}")
    if mode in ("rec", "both"):
        try:
            print(f"recursive({n}) = {fibonacci_recursive(n)}")
        except RecursionError:
            print(f"recursive({n}) -> RecursionError (превышен лимит стека Python)")


def _run_sort(algo: str, dataset: str, size: int, seed: int) -> None:
    data = GENERATORS[dataset](size, seed=seed)
    expected = sorted(data)
    preview = f"{data[:15]}{'...' if size > 15 else ''}"
    print(f"Вход ({dataset}, n={size}): {preview}")

    targets = SORTS.items() if algo == "both" else [(algo, SORTS[algo])]
    for name, fn in targets:
        t0 = time.perf_counter()
        res = fn(data)
        dt = (time.perf_counter() - t0) * 1000
        status = "OK" if res == expected else "MISMATCH"
        res_preview = f"{res[:15]}{'...' if size > 15 else ''}"
        print(f"{name:10} [{status}, {dt:.3f} ms]: {res_preview}")


def _run_stack(items: list[str]) -> None:
    stack = Stack[str]()
    print(f"Пустой стек: bool={bool(stack)}, len={len(stack)}")
    for item in items:
        stack.push(item)
        print(f"push({item!r}) -> peek={stack.peek()!r}, len={len(stack)}")
    while stack:
        print(f"pop() -> {stack.pop()!r}, len={len(stack)}")
    try:
        stack.pop()
    except EmptyStackError as exc:
        print(f"pop() на пустом стеке -> {type(exc).__name__}: {exc}")


def _run_tests(target: str) -> None:
    import pytest

    args = ["-v"] if target == "all" else ["-v", "-k", target]
    raise SystemExit(pytest.main(args))


def _interactive_argv() -> list[str]:
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
    return [menu.get(input("Номер [1-6]: ").strip(), "test")]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="algo", description="CLI для тестирования algo-pkg")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_fib = sub.add_parser("fib", help="Проверить числа Фибоначчи")
    p_fib.add_argument("n", nargs="?", type=int, default=10)
    p_fib.add_argument("--mode", choices=("iter", "rec", "both"), default="both")

    p_sort = sub.add_parser("sort", help="Проверить сортировки")
    p_sort.add_argument("--algo", choices=("insertion", "heap", "both"), default="both")
    p_sort.add_argument("--dataset", choices=tuple(GENERATORS), default="random")
    p_sort.add_argument("--size", type=int, default=20)
    p_sort.add_argument("--seed", type=int, default=42)

    p_stack = sub.add_parser("stack", help="Проверить стек (LIFO)")
    p_stack.add_argument("items", nargs="*", default=["A", "B", "C"])

    p_gen = sub.add_parser("gen", help="Сгенерировать тестовый набор")
    p_gen.add_argument("--type", choices=tuple(GENERATORS), default="random")
    p_gen.add_argument("--size", type=int, default=15)
    p_gen.add_argument("--seed", type=int, default=42)

    p_bench = sub.add_parser("bench", help="Запустить бенчмарк")
    p_bench.add_argument("--repeats", type=int, default=5)

    p_test = sub.add_parser("test", help="Запустить pytest по выбранной категории")
    p_test.add_argument("target", nargs="?", choices=("all", "fib", "sort", "stack", "gen"), default="all")

    return parser


def main(argv: list[str] | None = None) -> None:
    raw_args = sys.argv[1:] if argv is None else argv
    if not raw_args:
        raw_args = _interactive_argv()

    args = build_parser().parse_args(raw_args)
    match args.cmd:
        case "fib":
            _run_fib(args.n, args.mode)
        case "sort":
            _run_sort(args.algo, args.dataset, args.size, args.seed)
        case "stack":
            _run_stack(args.items)
        case "gen":
            data = GENERATORS[args.type](args.size, seed=args.seed)
            print(f"{args.type} (n={args.size}, seed={args.seed}): {data}")
        case "bench":
            print(run_benchmark(repeats=args.repeats))
        case "test":
            _run_tests(args.target)


if __name__ == "__main__":
    main()
