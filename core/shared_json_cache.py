
import json
import os
import threading
import time
import logging
from typing import Dict, Any, List

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [JsonCache] %(message)s')
log = logging.getLogger(__name__)

class SharedJsonCache:
    """
    A thread-safe, in-memory cache for frequently accessed JSON files.
    It uses a background thread to monitor files for changes and keep the cache fresh.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(SharedJsonCache, cls).__new__(cls)
        return cls._instance

    def __init__(self, file_paths: List[str] = None, watch_interval: float = 0.5):
        # This check ensures __init__ runs only once for the singleton
        if hasattr(self, '_initialized') and self._initialized:
            return
        with self._lock:
            if hasattr(self, '_initialized') and self._initialized:
                return
            
            self._cache: Dict[str, Any] = {}
            self._file_mod_times: Dict[str, float] = {}
            self._file_paths: List[str] = file_paths or []
            self._watch_interval = watch_interval
            self._watcher_thread = None
            self._stop_event = threading.Event()

            # Initial load
            for path in self._file_paths:
                self.refresh(path)
            
            self._initialized = True
            log.info(f"SharedJsonCache initialized for: {self._file_paths}")

    def _load_from_disk(self, path: str) -> None:
        """Loads or reloads a specific JSON file from disk into the cache."""
        if not os.path.exists(path):
            log.warning(f"File not found on disk: {path}. Cache will hold an empty dict.")
            self._cache[path] = {}
            self._file_mod_times[path] = 0
            return

        try:
            mod_time = os.path.getmtime(path)
            with self._lock:
                # Only read if the file has been modified
                if mod_time != self._file_mod_times.get(path):
                    with open(path, 'r') as f:
                        self._cache[path] = json.load(f)
                        self._file_mod_times[path] = mod_time
                        log.debug(f"Cache updated for {os.path.basename(path)}.")
        except (json.JSONDecodeError, IOError) as e:
            log.error(f"Error reading {path}: {e}. Cache for this file may be stale.")

    def _write_to_disk(self, path: str, data: Dict[str, Any]) -> None:
        """Writes data to a specific JSON file on disk."""
        try:
            with self._lock:
                # Atomically write to a temp file and then rename
                temp_path = path + '.tmp'
                with open(temp_path, 'w') as f:
                    json.dump(data, f, indent=4)
                os.rename(temp_path, path)
                # Update mod time after successful write
                self._file_mod_times[path] = os.path.getmtime(path)
                log.debug(f"Data for {os.path.basename(path)} written to disk.")
        except IOError as e:
            log.error(f"Error writing to {path}: {e}")

    def get_json(self, path: str) -> Dict[str, Any]:
        """Returns a copy of the cached data for a given file path."""
        with self._lock:
            return self._cache.get(path, {}).copy()

    def set_json(self, path: str, data: Dict[str, Any]) -> None:
        """Updates the cache and writes to the file if the data has changed."""
        with self._lock:
            # To prevent race conditions, only write if data is different
            if data != self._cache.get(path):
                self._cache[path] = data
                self._write_to_disk(path, data)

    def refresh(self, path: str) -> None:
        """Forces a reload of a specific file from disk into the cache."""
        log.info(f"Force refreshing cache for {os.path.basename(path)}.")
        self._load_from_disk(path)

    def _watch_files(self) -> None:
        """The background task for the file watcher thread."""
        log.info("File watcher thread started.")
        while not self._stop_event.is_set():
            for path in self._file_paths:
                self._load_from_disk(path)
            time.sleep(self._watch_interval)
        log.info("File watcher thread stopped.")

    def start_cache_watcher(self) -> None:
        """Starts the background file watcher thread."""
        if self._watcher_thread is None or not self._watcher_thread.is_alive():
            self._stop_event.clear()
            self._watcher_thread = threading.Thread(target=self._watch_files, daemon=True)
            self._watcher_thread.start()

    def stop_cache_watcher(self) -> None:
        """Stops the background file watcher thread."""
        if self._watcher_thread and self._watcher_thread.is_alive():
            self._stop_event.set()
            self._watcher_thread.join(timeout=2)
            log.info("Cache watcher stopped successfully.")

# --- Singleton Instance ---
# You can define the files to be cached here
from .file_paths import TELEMETRY_FILE, FSM_STATE_FILE

# Assuming mission_status.json is at the same level
MISSION_STATUS_FILE = os.path.join(os.path.dirname(TELEMETRY_FILE), 'mission_status.json')

# List of files to be managed by the cache
CACHED_FILES = [TELEMETRY_FILE, FSM_STATE_FILE, MISSION_STATUS_FILE]

# Global cache instance
json_cache = SharedJsonCache(file_paths=CACHED_FILES)
