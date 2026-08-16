#!/usr/bin/env python3
"""
System Monitor
--------------
Monitors hardware utilization (CPU, RAM, NVIDIA GPU) in a background thread
and triggers reactive visual feedback when high load is detected.
"""

from __future__ import annotations

import os
import subprocess
import threading
import time
from typing import Callable

try:
    import psutil
except ImportError:
    psutil = None


def get_gpu_usage() -> tuple[float, float, float]:
    """Query NVIDIA GPU usage, used memory (MB), and total memory (MB) via nvidia-smi."""
    try:
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        out = subprocess.check_output(
            [
                'nvidia-smi',
                '--query-gpu=utilization.gpu,memory.used,memory.total',
                '--format=csv,noheader,nounits',
            ],
            encoding='utf-8',
            startupinfo=startupinfo,
            creationflags=0x08000000 if os.name == 'nt' else 0,
            timeout=1.0,
        )
        parts = [p.strip() for p in out.strip().split(',')]
        if len(parts) >= 3:
            return float(parts[0]), float(parts[1]), float(parts[2])
    except Exception:
        pass
    return 0.0, 0.0, 0.0


class SystemMonitor:
    """Background hardware monitor for CPU, RAM, and GPU stats."""

    def __init__(self, on_update: Callable[[float, float, float], None] | None = None):
        self.on_update = on_update
        self.cpu_pct: float = 0.0
        self.ram_pct: float = 0.0
        self.gpu_pct: float = 0.0
        self.running: bool = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start the background monitoring thread."""
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the monitoring thread."""
        self.running = False

    def _monitor_loop(self) -> None:
        """Continuous sampling loop."""
        while self.running:
            try:
                if psutil:
                    self.cpu_pct = psutil.cpu_percent(interval=1.0)
                    vmem = psutil.virtual_memory()
                    self.ram_pct = vmem.percent
                else:
                    time.sleep(1.0)

                gpu_u, _, _ = get_gpu_usage()
                self.gpu_pct = gpu_u

                if self.on_update:
                    self.on_update(self.cpu_pct, self.ram_pct, self.gpu_pct)
            except Exception:
                time.sleep(1.0)
