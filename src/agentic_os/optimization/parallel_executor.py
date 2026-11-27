import asyncio
import time
from typing import List, Callable, Any, Dict, Tuple


class ParallelPipelineExecutor:
    """Layer 5: Async and Parallel Execution.
    Dispatches independent operations concurrently using asyncio.gather.
    Eliminates sequential latency bottlenecks without mutable state corruption.
    """

    def __init__(self):
        self.parallel_jobs_dispatched = 0
        self.total_time_saved_sec = 0.0

    async def execute_concurrently(self, tasks: List[Tuple[str, Callable[[], Any]]]) -> Dict[str, Any]:
        """Runs a list of (task_name, callable) concurrently and returns a dictionary of results."""
        start_time = time.perf_counter()

        async def _run_sync_task(name: str, fn: Callable[[], Any]):
            # Run blocking task in default thread pool executor
            return name, await asyncio.to_thread(fn)

        async_tasks = [_run_sync_task(name, fn) for name, fn in tasks]
        completed = await asyncio.gather(*async_tasks)

        elapsed = time.perf_counter() - start_time
        results = dict(completed)

        # Estimate sequential execution time
        estimated_sequential_time = sum(0.15 for _ in tasks)
        time_saved = max(0.0, estimated_sequential_time - elapsed)
        self.total_time_saved_sec += time_saved
        self.parallel_jobs_dispatched += len(tasks)

        return results

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "parallel_jobs_dispatched": self.parallel_jobs_dispatched,
            "estimated_latency_saved_sec": round(self.total_time_saved_sec, 3)
        }
