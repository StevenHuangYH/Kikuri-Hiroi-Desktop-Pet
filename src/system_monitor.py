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


class WindowsAudioDetector:
    """Detects active audio output playback across Windows OS using WASAPI peak meter."""

    def __init__(self):
        self._pMeter = None
        self._GetPeakValue = None
        self._initialized = False
        self._init_wasapi()

    def _init_wasapi(self) -> None:
        if os.name != 'nt':
            return
        try:
            import ctypes
            from ctypes import wintypes
            import uuid

            class GUID(ctypes.Structure):
                _fields_ = [
                    ('Data1', wintypes.DWORD),
                    ('Data2', wintypes.WORD),
                    ('Data3', wintypes.WORD),
                    ('Data4', wintypes.BYTE * 8)
                ]

            def str_to_guid(s):
                u = uuid.UUID(s)
                return GUID.from_buffer_copy(u.bytes_le)

            ole32 = ctypes.windll.ole32
            ole32.CoInitialize(None)

            CLSID_MMDeviceEnumerator = str_to_guid('BCDE0395-E52F-467C-8E3D-C4579291692E')
            IID_IMMDeviceEnumerator = str_to_guid('A95664D2-9614-4F35-A746-DE8DB63617E6')
            IID_IAudioMeterInformation = str_to_guid('C02216F6-8C67-4B5B-9D00-D008E73E0064')

            pEnumerator = ctypes.c_void_p()
            hr = ole32.CoCreateInstance(
                ctypes.byref(CLSID_MMDeviceEnumerator),
                None,
                1,  # CLSCTX_INPROC_SERVER
                ctypes.byref(IID_IMMDeviceEnumerator),
                ctypes.byref(pEnumerator)
            )
            if hr != 0 or not pEnumerator:
                return

            vtbl_enum = ctypes.cast(pEnumerator, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
            GetDefaultAudioEndpoint = ctypes.WINFUNCTYPE(
                ctypes.c_long, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p)
            )(vtbl_enum[4])

            pDevice = ctypes.c_void_p()
            hr = GetDefaultAudioEndpoint(pEnumerator, 0, 0, ctypes.byref(pDevice))
            if hr != 0 or not pDevice:
                return

            vtbl_dev = ctypes.cast(pDevice, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
            Activate = ctypes.WINFUNCTYPE(
                ctypes.c_long, ctypes.c_void_p, ctypes.POINTER(GUID), ctypes.c_ulong, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)
            )(vtbl_dev[3])

            pMeter = ctypes.c_void_p()
            hr = Activate(pDevice, ctypes.byref(IID_IAudioMeterInformation), 1, None, ctypes.byref(pMeter))
            if hr != 0 or not pMeter:
                return

            vtbl_meter = ctypes.cast(pMeter, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
            self._GetPeakValue = ctypes.WINFUNCTYPE(
                ctypes.c_long, ctypes.c_void_p, ctypes.POINTER(ctypes.c_float)
            )(vtbl_meter[3])
            self._pMeter = pMeter
            self._initialized = True
        except Exception:
            self._initialized = False

    def get_peak_level(self) -> float:
        """Return instantaneous master audio peak level in [0.0, 1.0]."""
        if not self._initialized or not self._pMeter or not self._GetPeakValue:
            return 0.0
        try:
            import ctypes
            peak = ctypes.c_float()
            hr = self._GetPeakValue(self._pMeter, ctypes.byref(peak))
            if hr == 0:
                return float(peak.value)
            else:
                self._init_wasapi()
                return 0.0
        except Exception:
            return 0.0


class SystemMonitor:
    """Background hardware & audio monitor for CPU, RAM, GPU stats, and music detection."""

    def __init__(self, on_update: Callable[[float, float, float, bool], None] | None = None):
        self.on_update = on_update
        self.cpu_pct: float = 0.0
        self.ram_pct: float = 0.0
        self.gpu_pct: float = 0.0
        self.audio_active: bool = False
        self.audio_detector = WindowsAudioDetector()
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
        """Continuous sampling loop (0.5s intervals)."""
        while self.running:
            try:
                if psutil:
                    self.cpu_pct = psutil.cpu_percent(interval=0.5)
                    vmem = psutil.virtual_memory()
                    self.ram_pct = vmem.percent
                else:
                    time.sleep(0.5)

                gpu_u, _, _ = get_gpu_usage()
                self.gpu_pct = gpu_u

                # Sample audio peak output
                peak = self.audio_detector.get_peak_level()
                self.audio_active = (peak > 0.005)

                if self.on_update:
                    self.on_update(self.cpu_pct, self.ram_pct, self.gpu_pct, self.audio_active)
            except Exception:
                time.sleep(0.5)
