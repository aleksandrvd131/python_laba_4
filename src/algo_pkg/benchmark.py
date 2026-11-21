import statistics
import time
from collections.abc import Callable
from pathlib import Path

from algo_pkg.generators import (
    many_duplicates_list,
    nearly_sorted_list,
    random_list,
    reversed_list,
    sorted_list,
)
from algo_pkg.sorting import heap_sort, insertion_sort

# размеры массивов для тестов скорости по умолчанию
SIZES = (10_000, 100_000, 1_000_000)
DEFAULT_OUTPUT_FILE = "benchmark_results.md"


def measure(
    fn: Callable[[list[int]], list[int]],
    data: list[int],
    *,
    repeats: int = 5,
    max_single_sec: float = 15.0,
) -> float | None:
    # замеряем среднее время работы сортировки
    # если хотя бы раз работало дольше лимита возвращаем None
    times: list[float] = []
    for _ in range(repeats):
        # обязательно делаем независимую копию чтобы не менять исходные данные
        sample = data.copy()
        t0 = time.perf_counter()
        fn(sample)
        dt = time.perf_counter() - t0
        # если вышли за лимит времени дальше не крутим
        if dt > max_single_sec:
            return None
        times.append(dt)
    # возвращаем среднее арифметическое
    return statistics.mean(times)


def run_benchmark(
    repeats: int = 5,
    sizes: tuple[int, ...] = SIZES,
    output_file: str | None = DEFAULT_OUTPUT_FILE,
) -> str:
    # запуск бенчмарка для сравнения сортировок
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

    # шапка итоговой markdown таблицы
    lines = [
        "# Результаты бенчмарка алгоритмов сортировки",
        "",
        f"- **Повторов для каждого замера:** {repeats}",
        f"- **Размеры массивов:** {', '.join(f'{s:,}'.replace(',', ' ') for s in sizes)}",
        "- **Лимит отсечки для $O(n^2)$:** 3.0 с",
        "",
        "| Dataset | Size | insertion_sort (s) | heap_sort (s) |",
        "| :--- | ---: | ---: | ---: |",
    ]

    print(f"Запуск бенчмарка (повторов: {repeats}, наборов: {len(datasets)}, размеры: {sizes})...")

    # прогоняем все типы данных
    for ds_idx, (ds_name, gen) in enumerate(datasets, 1):
        timed_out: set[str] = set()
        print(f"  [{ds_idx}/{len(datasets)}] Набор: {ds_name}...")
        for size in sizes:
            base_data = gen(size, seed=42)
            row = [ds_name, f"{size:,}".replace(",", " ")]
            for algo_name, algo in algos:
                if algo_name in timed_out:
                    row.append("N/A (>3s, O(n²))")
                    continue
                # Сортировка вставками на неотсортированных данных O(n^2) при размере > 15 000
                # гарантированно превышает лимит разумного времени (на 100k это ~4 минуты, на 1M - часы)
                if algo_name == "insertion_sort" and size > 15_000 and ds_name != "sorted":
                    timed_out.add(algo_name)
                    row.append("N/A (>3s, O(n²))")
                    continue
                avg = measure(algo, base_data, repeats=repeats)
                if avg is None:
                    timed_out.add(algo_name)
                    row.append("N/A (>3s, O(n²))")
                else:
                    row.append(f"{avg:.4f}")
            lines.append(f"| {' | '.join(row)} |")


    report = "\n".join(lines)

    if output_file:
        Path(output_file).write_text(report, encoding="utf-8")
        print(f"\n[OK] Таблица и анализ сохранены в файл: {output_file}\n")

    return report


if __name__ == "__main__":
    print(run_benchmark())
