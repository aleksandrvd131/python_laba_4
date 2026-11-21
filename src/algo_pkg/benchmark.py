import random
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
from algo_pkg.sorting import heap_sort, insertion_sort, radix_sort

# размеры массивов для тестов скорости по умолчанию
SIZES = (1_000_000, 10_000_000, 100_000_000)
DEFAULT_OUTPUT_FILE = "benchmark_results.md"


def measure(
    fn: Callable[[list[int]], list[int]],
    data: list[int],
    *,
    repeats: int = 5,
    max_single_sec: float = 3.0,
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
    max_single_sec: float = 3.0,
    seed: int | None = 42,
    output_file: str | None = DEFAULT_OUTPUT_FILE,
) -> str:
    # запуск бенчмарка для сравнения сортировок
    algos = [
        ("insertion_sort", insertion_sort),
        ("heap_sort", heap_sort),
        ("radix_sort", radix_sort),
    ]
    datasets = [
        ("random", random_list),
        ("sorted", sorted_list),
        ("reversed", reversed_list),
        ("nearly_sorted", nearly_sorted_list),
        ("duplicates", many_duplicates_list),
    ]

    actual_seed = seed if seed is not None else random.randint(1, 1_000_000)
    cutoff = float(max_single_sec)
    cutoff_str = f"{int(cutoff)}s" if cutoff.is_integer() else f"{cutoff:g}s"
    na_quad = f"N/A (>{cutoff_str}, O(n²))"
    na_other = f"N/A (>{cutoff_str})"

    # шапка итоговой markdown таблицы
    lines = [
        "# Результаты бенчмарка алгоритмов сортировки",
        "",
        f"- **Повторов для каждого замера:** {repeats}",
        f"- **Размеры массивов:** {', '.join(f'{s:,}'.replace(',', ' ') for s in sizes)}",
        f"- **Лимит отсечки для $O(n^2)$:** {cutoff:.1f} с",
        f"- **Seed:** {actual_seed}",
        "",
        "| Dataset | Size | Seed | insertion_sort (s) | heap_sort (s) | radix_sort (s) |",
        "| :--- | ---: | ---: | ---: | ---: | ---: |",
    ]

    print(
        f"Запуск бенчмарка (повторов: {repeats}, наборов: {len(datasets)}, "
        f"размеры: {sizes}, отсечка: {cutoff}s, seed: {actual_seed})..."
    )

    # прогоняем все типы данных
    for ds_idx, (ds_name, gen) in enumerate(datasets, 1):
        timed_out: set[str] = set()
        print(f"  [{ds_idx}/{len(datasets)}] Набор: {ds_name}...")
        for size in sizes:
            # Оптимизация: если алгоритмы заведомо превышают лимит cutoff,
            # пропускаем генерацию гигантского массива (на 100M это >4 ГБ RAM)
            eligible_algos = []
            for algo_name, algo in algos:
                if algo_name in timed_out:
                    continue
                if algo_name == "insertion_sort" and size > 15_000 and ds_name != "sorted" and cutoff < 20_000:
                    timed_out.add(algo_name)
                    continue
                if algo_name == "heap_sort" and size >= 1_000_000 and cutoff < 8.0:
                    timed_out.add(algo_name)
                    continue
                if algo_name == "heap_sort" and size >= 10_000_000 and cutoff < 100.0:
                    timed_out.add(algo_name)
                    continue
                if algo_name == "radix_sort" and size >= 10_000_000 and cutoff < 10.0:
                    timed_out.add(algo_name)
                    continue
                if algo_name == "radix_sort" and size >= 100_000_000 and cutoff < 100.0:
                    timed_out.add(algo_name)
                    continue
                if algo_name == "insertion_sort" and size >= 100_000_000 and cutoff < 12.0:
                    timed_out.add(algo_name)
                    continue
                eligible_algos.append((algo_name, algo))

            row = [ds_name, f"{size:,}".replace(",", " "), str(actual_seed)]

            if not eligible_algos:
                for algo_name, _ in algos:
                    if algo_name == "insertion_sort":
                        row.append(na_quad)
                    else:
                        row.append(na_other)
                lines.append(f"| {' | '.join(row)} |")
                continue

            base_data = gen(size, seed=actual_seed)
            for algo_name, algo in algos:
                if algo_name in timed_out:
                    if algo_name == "insertion_sort":
                        row.append(na_quad)
                    else:
                        row.append(na_other)
                    continue
                avg = measure(algo, base_data, repeats=repeats, max_single_sec=cutoff)
                if avg is None:
                    timed_out.add(algo_name)
                    if algo_name == "insertion_sort":
                        row.append(na_quad)
                    else:
                        row.append(na_other)
                else:
                    row.append(f"{avg:.4f}")
            lines.append(f"| {' | '.join(row)} |")
    report = "\n".join(lines)

    if output_file:
        Path(output_file).write_text(report, encoding="utf-8")
        print(f"\n[OK] Таблица сохранена в файл: {output_file}")
        print(f"[Воспроизводимость] Использован seed: {actual_seed}")
        print(f"  Перепроверить отдельный замер: algo sort --dataset <dataset> --size <size> --seed {actual_seed}")
        print(f"  Повторить весь бенчмарк: algo bench --seed {actual_seed} --timeout {cutoff}\n")

    return report


if __name__ == "__main__":
    print(run_benchmark())
