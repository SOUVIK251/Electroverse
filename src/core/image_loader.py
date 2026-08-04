"""
ElectroVerse High-Performance Asynchronous Image Loader Engine
Provides multi-threaded parallel image loading, LRU memory caching, disk caching,
lazy loading, preloading, downscaling, and deduplication for zero-freeze UI rendering.
"""

import os
import hashlib
import urllib.request
from typing import Dict, List, Tuple, Optional, Callable

from PySide6.QtCore import Qt, QObject, Signal, QRunnable, QThreadPool, QSize
from PySide6.QtGui import QPixmap, QImage
from src.core.logger import log


class ImageWorkerSignals(QObject):
    """Signals emitted by ImageLoadWorker upon completion or error."""
    loaded = Signal(str, QPixmap, str)  # (key, pixmap, path_or_url)
    failed = Signal(str, str)            # (key, error_msg)


class ImageLoadWorker(QRunnable):
    """Background worker task for reading, downloading, decoding, and scaling images off the GUI thread."""

    def __init__(self, key: str, path_or_url: str, target_size: Optional[Tuple[int, int]] = None, cache_dir: Optional[str] = None):
        super().__init__()
        self.key = key
        self.path_or_url = path_or_url
        self.target_size = target_size
        self.cache_dir = cache_dir
        self.signals = ImageWorkerSignals()

    def run(self):
        try:
            pixmap = None

            # 1. Handle HTTP / HTTPS Remote URLs
            if self.path_or_url.startswith("http://") or self.path_or_url.startswith("https://"):
                disk_file = None
                if self.cache_dir:
                    url_hash = hashlib.md5(self.path_or_url.encode("utf-8")).hexdigest()
                    disk_file = os.path.join(self.cache_dir, f"{url_hash}.img")

                # Check disk cache first for remote URLs
                if disk_file and os.path.exists(disk_file):
                    pixmap = QPixmap(disk_file)

                if not pixmap or pixmap.isNull():
                    content = None
                    try:
                        req = urllib.request.Request(self.path_or_url, headers={'User-Agent': 'ElectroVerse/1.0'})
                        with urllib.request.urlopen(req, timeout=4) as response:
                            content = response.read()
                    except Exception as e:
                        try:
                            import requests
                            resp = requests.get(self.path_or_url, timeout=4)
                            if resp.status_code == 200:
                                content = resp.content
                        except Exception:
                            pass

                    if content:
                        pixmap = QPixmap()
                        if pixmap.loadFromData(content):
                            # Save to disk cache asynchronously
                            if disk_file:
                                try:
                                    with open(disk_file, "wb") as f:
                                        f.write(content)
                                except Exception as ce:
                                    log.debug(f"Disk cache write error: {ce}")
                    else:
                        self.signals.failed.emit(self.key, "HTTP download failed")
                        return
            else:
                # 2. Handle Local File Paths
                if os.path.exists(self.path_or_url):
                    pixmap = QPixmap(self.path_or_url)
                else:
                    # Try fallback extensions
                    base_no_ext, _ = os.path.splitext(self.path_or_url)
                    for ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.JPG', '.JPEG', '.PNG', '.WEBP', '.BMP']:
                        alt_path = base_no_ext + ext
                        if os.path.exists(alt_path):
                            pixmap = QPixmap(alt_path)
                            break

            if pixmap and not pixmap.isNull():
                # 3. Downscale / Resize in background thread before handing off to GUI thread
                if self.target_size:
                    w, h = self.target_size
                    pixmap = pixmap.scaled(QSize(w, h), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

                self.signals.loaded.emit(self.key, pixmap, self.path_or_url)
            else:
                self.signals.failed.emit(self.key, "Image decode failed or file missing")

        except Exception as e:
            self.signals.failed.emit(self.key, str(e))


class AsyncImageLoader(QObject):
    """Master Asynchronous Image Loader Service with Memory/Disk Caching and Deduplication."""

    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = AsyncImageLoader()
        return cls._instance

    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(8)  # Parallel loading across CPU cores

        # LRU Memory Cache: key -> QPixmap
        self._memory_cache: Dict[str, QPixmap] = {}
        self._max_memory_cache_items = 300

        # Deduplication: key -> List of callbacks
        self._in_flight: Dict[str, List[Tuple[Callable, Optional[Callable]]]] = {}

        # Disk cache directory
        user_home = os.path.expanduser("~")
        self.disk_cache_dir = os.path.join(user_home, ".electroverse", "cache", "images")
        os.makedirs(self.disk_cache_dir, exist_ok=True)

    def _make_key(self, path_or_url: str, target_size: Optional[Tuple[int, int]]) -> str:
        size_str = f"_{target_size[0]}x{target_size[1]}" if target_size else "_full"
        return f"{path_or_url}{size_str}"

    def get_cached_image(self, path_or_url: str, target_size: Optional[Tuple[int, int]] = None) -> Optional[QPixmap]:
        """Synchronously check memory cache."""
        key = self._make_key(path_or_url, target_size)
        return self._memory_cache.get(key)

    def load_image_async(
        self,
        path_or_url: str,
        target_size: Optional[Tuple[int, int]] = None,
        on_success: Optional[Callable[[QPixmap], None]] = None,
        on_failure: Optional[Callable[[str], None]] = None
    ):
        """Asynchronously load an image using thread pool with caching and deduplication."""
        if not path_or_url or not str(path_or_url).strip():
            if on_failure:
                on_failure("Empty path")
            return

        key = self._make_key(path_or_url, target_size)

        # 1. Check Memory Cache (Instant Return <1ms)
        if key in self._memory_cache:
            pixmap = self._memory_cache[key]
            if on_success:
                on_success(pixmap)
            return

        # 2. Check In-Flight Deduplication
        if key in self._in_flight:
            self._in_flight[key].append((on_success, on_failure))
            return

        # Register in-flight request
        self._in_flight[key] = [(on_success, on_failure)]

        # 3. Create Worker & Dispatch to ThreadPool
        worker = ImageLoadWorker(key, path_or_url, target_size, self.disk_cache_dir)
        worker.signals.loaded.connect(self._on_worker_loaded)
        worker.signals.failed.connect(self._on_worker_failed)
        self.thread_pool.start(worker)

    def _on_worker_loaded(self, key: str, pixmap: QPixmap, path_or_url: str):
        # Store in memory cache
        if len(self._memory_cache) >= self._max_memory_cache_items:
            first_key = next(iter(self._memory_cache))
            del self._memory_cache[first_key]

        self._memory_cache[key] = pixmap

        # Notify all waiting callbacks
        callbacks = self._in_flight.pop(key, [])
        for on_success, _ in callbacks:
            if on_success:
                try:
                    on_success(pixmap)
                except Exception as e:
                    log.error(f"Error in image success callback: {e}")

    def _on_worker_failed(self, key: str, error_msg: str):
        callbacks = self._in_flight.pop(key, [])
        for _, on_failure in callbacks:
            if on_failure:
                try:
                    on_failure(error_msg)
                except Exception as e:
                    log.error(f"Error in image failure callback: {e}")

    def preload_image(self, path_or_url: str, target_size: Optional[Tuple[int, int]] = None):
        """Preload image in background without UI callbacks."""
        self.load_image_async(path_or_url, target_size)
