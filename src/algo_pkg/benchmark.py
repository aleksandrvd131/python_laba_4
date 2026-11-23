import gc
import os
import random
import time
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from tqdm import tqdm

from algo_pkg.generators import (
    many_duplicates_list,
    nearly_sorted_list,
    random_list,
    reversed_list,
    sorted_list,
)
from algo_pkg.sorting import heap_sort, insertion_sort, radix_sort

# размеры массивов по умолчанию (1 млн, 10 млн, 100 млн)
SIZES = (1_000_000, 10_000_000, 100_000_000)
DEFAULT_OUTPUT_FILE = "benchmark_results.md"

# словари с алгоритмами и генераторами
ALGORITHMS: dict[str, Callable[[list[int]], list[int]]] = {
    "insertion_sort": insertion_sort,
    "heap_sort": heap_sort,
    "radix_sort": radix_sort,
}

DATASETS: dict[str, Callable[..., list[int]]] = {
    "random": random_list,
    "sorted": sorted_list,
    "reversed": reversed_list,
    "nearly_sorted": nearly_sorted_list,
    "duplicates": many_duplicates_list,
}


def measure(
    fn: Callable[[list[int]], list[int]],
    data: list[int],
    *,
    repeats: int = 5,
    max_single_sec: float = 3.0,
) -> float | None:
    # замер среднего времени работы сортировки
    times: list[float] = []
    for r in range(repeats):
        # на последнем повторе без копии списка чтобы экономить память
        sample = data if r == repeats - 1 else data.copy()
        t0 = time.perf_counter()
        fn(sample)
        dt = time.perf_counter() - t0

        # выход если превышен лимит времени
        if dt > max_single_sec:
            return None
        times.append(dt)

    return sum(times) / len(times)


def run_single_test(
    algo_name: str,
    ds_name: str,
    size: int,
    seed: int,
    repeats: int,
    cutoff: float,
) -> tuple[str, str, int, float | None]:
    # запуск теста для одного процесса

    # вставки на больших массивах отсекаются из-за квадратичной сложности
    if algo_name == "insertion_sort" and size > 20_000 and ds_name != "sorted":
        return ds_name, algo_name, size, None

    # куча на 100 млн не уложится в лимит времени
    if algo_name == "heap_sort" and size >= 100_000_000 and cutoff <= 600.0:
        return ds_name, algo_name, size, None
    if algo_name == "heap_sort" and size >= 10_000_000 and cutoff < 50.0:
        return ds_name, algo_name, size, None

    # радикс на 100 млн для случайных тоже превысит лимит
    if (
        algo_name == "radix_sort"
        and size >= 100_000_000
        and ds_name in ("random", "nearly_sorted")
        and cutoff <= 100.0
    ):
        return ds_name, algo_name, size, None

    # генерация массива внутри отдельного процесса
    gen_func = DATASETS[ds_name]
    sort_func = ALGORITHMS[algo_name]
    data = gen_func(size, seed=seed)

    avg_time = measure(sort_func, data, repeats=repeats, max_single_sec=cutoff)

    # очистка памяти процесса
    del data
    gc.collect()

    return ds_name, algo_name, size, avg_time


def run_benchmark(
    repeats: int = 5,
    sizes: tuple[int, ...] = SIZES,
    max_single_sec: float = 3.0,
    seed: int | None = 42,
    output_file: str | None = DEFAULT_OUTPUT_FILE,
    workers: int | None = None,
) -> str:
    actual_seed = seed if seed is not None else random.randint(1, 1_000_000)
    cutoff = float(max_single_sec)
    cutoff_str = f"{int(cutoff)}s" if cutoff.is_integer() else f"{cutoff:g}s"
    na_quad = f"N/A (>{cutoff_str}, O(n²))"
    na_other = f"N/A (>{cutoff_str})"

    # количество процессов
    num_workers = min(os.cpu_count() or 1, 4) if workers is None else max(1, workers)

    # список всех задач
    tasks = [
        (algo_name, ds_name, size, actual_seed, repeats, cutoff)
        for size in sizes
        for ds_name in DATASETS
        for algo_name in ALGORITHMS
    ]

    # разделение задач: задачи на 100 млн по очереди чтобы не забить оперативку
    tasks_normal = [t for t in tasks if t[2] < 100_000_000]
    tasks_heavy = [t for t in tasks if t[2] >= 100_000_000]

    print(
        f"Запуск бенчмарка ({len(tasks)} замеров: {len(tasks_normal)} в {num_workers} процессах, "
        f"{len(tasks_heavy)} последовательно, seed={actual_seed})..."
    )

    results: dict[tuple[str, int, str], str] = {}

    with tqdm(total=len(tasks), desc="Бенчмарк", unit="тест") as pbar:
        # запуск обычных задач параллельно
        if tasks_normal:
            if num_workers > 1:
                with ProcessPoolExecutor(max_workers=num_workers) as executor:
                    futures = [executor.submit(run_single_test, *t) for t in tasks_normal]
                    for f in as_completed(futures):
                        ds_name, algo_name, size, avg_time = f.result()
                        if avg_time is None:
                            results[(ds_name, size, algo_name)] = (
                                na_quad if algo_name == "insertion_sort" else na_other
                            )
                        else:
                            results[(ds_name, size, algo_name)] = f"{avg_time:.4f}"
                        pbar.update(1)
            else:
                for t in tasks_normal:
                    ds_name, algo_name, size, avg_time = run_single_test(*t)
                    if avg_time is None:
                        results[(ds_name, size, algo_name)] = (
                            na_quad if algo_name == "insertion_sort" else na_other
                        )
                    else:
                        results[(ds_name, size, algo_name)] = f"{avg_time:.4f}"
                    pbar.update(1)

        # тяжелые задачи на 100 млн по одной
        if tasks_heavy:
            # по очереди чтобы не забить оперативку
            for t in tasks_heavy:
                ds_name, algo_name, size, avg_time = run_single_test(*t)
                if avg_time is None:
                    results[(ds_name, size, algo_name)] = (
                        na_quad if algo_name == "insertion_sort" else na_other
                    )
                else:
                    results[(ds_name, size, algo_name)] = f"{avg_time:.4f}"
                pbar.update(1)

    # итоговая таблица
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

    for ds_name in DATASETS:
        for size in sizes:
            row = [ds_name, f"{size:,}".replace(",", " "), str(actual_seed)] + [
                results.get((ds_name, size, algo_name), na_other) for algo_name in ALGORITHMS
            ]
            lines.append(f"| {' | '.join(row)} |")

    report = "\n".join(lines)

    # запись в файл если передан путь
    if output_file:
        Path(output_file).write_text(report, encoding="utf-8")
        print(f"\n[OK] Результаты сохранены в: {output_file}")

    return report


if __name__ == "__main__":
    print(run_benchmark())
