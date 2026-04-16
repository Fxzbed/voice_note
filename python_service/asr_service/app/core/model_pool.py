from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List


@dataclass
class ModelEntry:
    alias: str
    instance_id: int
    model: Any
    in_use: bool = False


class ModelPool:
    def __init__(self) -> None:
        self._registry: Dict[str, dict] = {}
        self._models: Dict[str, List[ModelEntry]] = {}
        self._loading_aliases: set[str] = set()

        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)

    def register(
        self,
        alias: str,
        loader: Callable[[], Any],
        instance_count: int = 1,
    ) -> None:
        if instance_count <= 0:
            raise ValueError("instance_count must be >= 1")

        with self._lock:
            self._registry[alias] = {
                "loader": loader,
                "instance_count": instance_count,
            }

    def acquire(self, alias: str, timeout: float | None = None) -> ModelEntry | None:
        start_time = time.time()

        while True:
            need_load = False
            config: dict | None = None

            with self._cond:
                if alias in self._models:
                    for entry in self._models[alias]:
                        if not entry.in_use:
                            entry.in_use = True
                            return entry

                elif alias in self._loading_aliases:
                    pass
                else:
                    if alias not in self._registry:
                        raise ValueError(f"model alias not registered: {alias}")
                    self._loading_aliases.add(alias)
                    config = self._registry[alias]
                    need_load = True

                if not need_load:
                    if timeout is not None:
                        elapsed = time.time() - start_time
                        remaining = timeout - elapsed
                        if remaining <= 0:
                            raise TimeoutError(f"no idle model instance for alias: {alias}")
                        self._cond.wait(timeout=remaining)
                    else:
                        self._cond.wait()
                    continue

            assert config is not None
            entries = self._build_entries(
                alias=alias,
                loader=config["loader"],
                instance_count=config["instance_count"],
            )

            with self._cond:
                self._models[alias] = entries
                self._loading_aliases.discard(alias)
                self._cond.notify_all()

    def release(self, entry: ModelEntry) -> None:
        with self._cond:
            entry.in_use = False
            self._cond.notify()

    def _build_entries(
        self,
        alias: str,
        loader: Callable[[], Any],
        instance_count: int,
    ) -> List[ModelEntry]:
        entries: List[ModelEntry] = []
        for i in range(instance_count):
            model = loader()
            entries.append(
                ModelEntry(
                    alias=alias,
                    instance_id=i,
                    model=model,
                    in_use=False,
                )
            )
        return entries

    def status(self) -> dict:
        with self._lock:
            return {
                "registered": {
                    alias: {
                        "instance_count": config["instance_count"],
                    }
                    for alias, config in self._registry.items()
                },
                "loaded": {
                    alias: [
                        {
                            "instance_id": entry.instance_id,
                            "in_use": entry.in_use,
                        }
                        for entry in entries
                    ]
                    for alias, entries in self._models.items()
                },
                "loading_aliases": list(self._loading_aliases),
            }