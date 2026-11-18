from collections.abc import Callable
import statistics
import time

from algo_pkg.generators import (
    many_duplicates_list,
    nearly_sorted_list,
    random_list,
    reversed_list,
    sorted_list,
)
from algo_pkg.sorting import heap_sort, insertion_sort

SIZES = (1_000, 5_000, 10_000)


def measure(
    fn: Callable[[list[int]], list[int]],
    data: list[int],
    *,
    repeats: int = 5,
    max_single_sec: float = 3.0,
) -> float | None:
    """Измерение среднего времени работы функции сортировки.

    Возвращает None, если хотя бы один запуск превысил max_single_sec.
    """
    times: list[float] = []
    for _ in range(repeats):
        sample = data.copy()
        t0 = time.perf_counter()
        fn(sample)
        dt = time.perf_counter() - t0
        if dt > max_single_sec:
            return None
        times.append(dt)
    return statistics.mean(times)


def run_benchmark(repeats: int = 5, sizes: tuple[int, ...] = SIZES) -> str:
    """Запуск сравнительного бенчмарка алгоритмов сортировки."""
    algos = [
        ("insertion_sort", insertion_sort),
        ("heap_sort", heap_sort),
    ]
    datasets = [
        ("random", random_list),
        ("sorted", sorted_list),
        ("reversed", reversed_list),
        ("nearly_sorted", nearly_sorted_list),
        ("duplicates", many_duplicates_list),
    ]

    lines = [
        "| Dataset | Size | insertion_sort (s) | heap_sort (s) |",
        "| :--- | ---: | ---: | ---: |",
    ]
    for ds_name, gen in datasets:
        timed_out: set[str] = set()
        for size in sizes:
            base_data = gen(size, seed=42)
            row = [ds_name, f"{size:,}".replace(",", " ")]
            for algo_name, algo in algos:
                if algo_name in timed_out:
                    row.append("N/A (>3s, O(n²))")
                    continue
                avg = measure(algo, base_data, repeats=repeats)
                if avg is None:
                    timed_out.add(algo_name)
                    row.append("N/A (>3s, O(n²))")
                else:
                    row.append(f"{avg:.4f}")
            lines.append(f"| {' | '.join(row)} |")
    return "\n".join(lines)


if __name__ == "__main__":
    print(run_benchmark())
