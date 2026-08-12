"""
ElectroVerse Screen-Capture Protection Utility with Environment Auto-Detection.

DEVELOPMENT ENVIRONMENT (ELECTROVERSE_ENV=development or running from python source):
- Protection is OFF by default.
- Sets SetWindowDisplayAffinity(hwnd, WDA_NONE).
- Windows Snipping Tool, Win + Shift + S, PrintScreen, and OBS capture normally.

PRODUCTION ENVIRONMENT (ELECTROVERSE_ENV=production or packaged user build):
- Protection is ON by default.
- Sets SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE).
- Window is excluded from normal OS screen capture.
"""

import sys
import os
import ctypes
from ctypes import wintypes
from PySide6.QtCore import QObject, QEvent
from PySide6.QtWidgets import QWidget, QDialog, QMainWindow, QApplication
from src.core.logger import log
from src.core.config import config_manager

# --- Windows API Display Affinity Constants ---
WDA_NONE = 0x00000000
WDA_MONITOR = 0x00000001
WDA_EXCLUDEFROMCAPTURE = 0x00000011  # Supported on Windows 10 Version 2004+ and Windows 11

_user32 = None
if sys.platform == "win32":
    try:
        _user32 = ctypes.windll.user32
        _user32.SetWindowDisplayAffinity.argtypes = [wintypes.HWND, wintypes.DWORD]
        _user32.SetWindowDisplayAffinity.restype = wintypes.BOOL
    except Exception as e:
        log.error(f"[SCREEN PROTECTION] Failed to bind SetWindowDisplayAffinity: {e}")


def is_development_environment() -> bool:
    """
    Detects whether ElectroVerse is running in a development environment.
    
    Priority rules:
    1. ELECTROVERSE_ENV == 'production' or 'prod' -> False (Production)
    2. ELECTROVERSE_ENV == 'development' or 'dev' -> True (Development)
    3. ELECTROVERSE_DEV_MODE in ['1', 'true', 'yes'] -> True (Development)
    4. config_manager.get('developer_mode') == True -> True (Development)
    5. Running un-frozen from local python source directory -> True (Development)
    6. Packaged executable without dev flag -> False (Production)
    """
    env_setting = os.getenv("ELECTROVERSE_ENV", "").strip().lower()
    if env_setting in ["production", "prod"]:
        return False
    if env_setting in ["development", "dev", "developer"]:
        return True

    env_dev_flag = os.getenv("ELECTROVERSE_DEV_MODE", "").strip().lower()
    if env_dev_flag in ["1", "true", "yes"]:
        return True

    cfg_dev = config_manager.get("developer_mode", False)
    if cfg_dev:
        return True

    # Auto-detect un-frozen local dev environment
    is_frozen = getattr(sys, "frozen", False)
    if not is_frozen:
        return True

    return False


class ScreenProtectionManager:
    """Master Coordinator for Windows OS-Level Screen Capture Protection."""

    def __init__(self):
        self._dev_mode = False
        self._protection_enabled = True
        self._protected_hwnds = set()
        self.reload_config()

    def reload_config(self):
        """Loads environment and configuration settings."""
        self._dev_mode = is_development_environment()
        
        # Explicit disable setting
        env_prot = os.getenv("ELECTROVERSE_DISABLE_PROTECTION", "").strip().lower()
        cfg_prot = config_manager.get("screen_capture_protection", True)
        
        if env_prot in ["1", "true", "yes"] or not cfg_prot:
            self._protection_enabled = False
        else:
            self._protection_enabled = not self._dev_mode

        env_str = "DEVELOPMENT" if self._dev_mode else "PRODUCTION"
        status_str = "ENABLED (WDA_EXCLUDEFROMCAPTURE)" if self.is_protection_enabled() else "DISABLED (WDA_NONE)"
        log.info(f"[SCREEN PROTECTION] Environment: {env_str} | Capture Protection: {status_str}")

    def is_developer_mode(self) -> bool:
        return self._dev_mode

    def set_developer_mode(self, enabled: bool):
        self._dev_mode = enabled
        self._protection_enabled = not enabled

    def is_protection_enabled(self) -> bool:
        return self._protection_enabled and not self._dev_mode

    def is_protection_supported(self) -> bool:
        return sys.platform == "win32" and _user32 is not None

    def enable_protection(self, target):
        """
        Applies display affinity to target window.
        - In Production: Sets WDA_EXCLUDEFROMCAPTURE (0x11) to block screenshots.
        - In Development: Sets WDA_NONE (0x00) to allow normal screenshots.
        """
        if not self.is_protection_supported():
            log.info("[SCREEN PROTECTION] Platform: Non-Windows or API unavailable. Protection skipped.")
            return False

        hwnd = self._get_hwnd(target)
        if not hwnd:
            return False

        if not self.is_protection_enabled():
            # In Development Mode: Explicitly set WDA_NONE to allow capture
            success = self._apply_affinity(hwnd, WDA_NONE)
            if hwnd in self._protected_hwnds:
                self._protected_hwnds.remove(hwnd)
            log.info(f"[SCREEN PROTECTION] Environment: DEVELOPMENT | HWND: {hex(hwnd)} | Mode: Developer | Protection: DISABLED (WDA_NONE)")
            return False

        # In Production Mode: Set WDA_EXCLUDEFROMCAPTURE (0x11)
        success = self._apply_affinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
        if not success:
            log.warning(f"[SCREEN PROTECTION] WDA_EXCLUDEFROMCAPTURE failed for HWND {hex(hwnd)}. Retrying WDA_MONITOR...")
            success = self._apply_affinity(hwnd, WDA_MONITOR)

        if success:
            self._protected_hwnds.add(hwnd)
            log.info(f"[SCREEN PROTECTION] Environment: PRODUCTION | HWND: {hex(hwnd)} | Protection: ENABLED (WDA_EXCLUDEFROMCAPTURE)")
        else:
            log.error(f"[SCREEN PROTECTION] Failed to set display affinity for HWND {hex(hwnd)}")

        return success

    def disable_protection(self, target):
        """Disables display-capture exclusion on a specific window."""
        if not self.is_protection_supported():
            return False

        hwnd = self._get_hwnd(target)
        if hwnd:
            success = self._apply_affinity(hwnd, WDA_NONE)
            if hwnd in self._protected_hwnds:
                self._protected_hwnds.remove(hwnd)
            log.info(f"[SCREEN PROTECTION] Protection disabled for HWND {hex(hwnd)}")
            return success
        return False

    def apply_to_dialog(self, dialog):
        """Helper to apply screen capture protection to child dialogs and popups."""
        return self.enable_protection(dialog)

    def _get_hwnd(self, target):
        if isinstance(target, int):
            return target
        if hasattr(target, "effectiveWinId"):
            try:
                wid = target.effectiveWinId()
                if wid:
                    return int(wid)
            except Exception:
                pass
        if hasattr(target, "winId"):
            try:
                wid = target.winId()
                if wid:
                    return int(wid)
            except Exception:
                pass
        if hasattr(target, "windowHandle") and target.windowHandle():
            try:
                return int(target.windowHandle().winId())
            except Exception:
                pass
        return None

    def _apply_affinity(self, hwnd: int, affinity: int) -> bool:
        if not _user32 or not hwnd:
            return False
        try:
            res = _user32.SetWindowDisplayAffinity(wintypes.HWND(hwnd), wintypes.DWORD(affinity))
            return bool(res)
        except Exception as e:
            log.error(f"[SCREEN PROTECTION] Exception executing SetWindowDisplayAffinity: {e}")
            return False


# Global Singleton Instance
screen_protection = ScreenProtectionManager()


class GlobalScreenProtectionEventFilter(QObject):
    """
    Global Qt Event Filter that intercepts window show, state changes, and creation
    to continuously enforce screen capture settings across all top-level windows and popups.
    """

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.Type.Show, QEvent.Type.WindowStateChange, QEvent.Type.WinIdChange):
            if isinstance(obj, (QMainWindow, QDialog)) or (isinstance(obj, QWidget) and obj.isWindow()):
                screen_protection.enable_protection(obj)
        return super().eventFilter(obj, event)


def install_screen_protection(app: QApplication):
    """Installs global event filter on QApplication instance to enforce window display protection."""
    filter_obj = GlobalScreenProtectionEventFilter(app)
    app.installEventFilter(filter_obj)
    log.info("[SCREEN PROTECTION] Global Qt Event Filter installed successfully.")
    return filter_obj
