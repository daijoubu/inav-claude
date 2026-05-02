import os
import platform
import subprocess
from pathlib import Path
from typing import Optional

import time


class MSCOperations:
    """USB Mass Storage operations for FC"""

    def __init__(self, fc_connection):
        self.fc = fc_connection

    def _wait_for_msc_block_device(self, timeout: float = 30.0) -> bool:
        """Wait for USB MSC block device to appear in /dev/."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            elapsed = time.time() - start_time
            for device in ['/dev/sdb', '/dev/sdb1', '/dev/sdc', '/dev/sdc1']:
                if os.path.exists(device):
                    print(f"  ✓ Found MSC block device: {device} (after {elapsed:.1f}s)")
                    return True

            time.sleep(0.2)

        print(f"  ✗ Block device not found after {timeout}s")
        return False

    def find_msc_mount_point(self) -> Optional[Path]:
        """Find the USB Mass Storage device mount point for the FC."""
        system = platform.system()

        if system == "Linux":
            return self._find_msc_mount_linux()
        elif system == "Darwin":
            return self._find_msc_mount_macos()
        elif system == "Windows":
            return self._find_msc_mount_windows()
        else:
            return None

    def _find_msc_mount_linux(self) -> Optional[Path]:
        """Find USB MSC mount point on Linux"""
        possible_paths = [Path("/run/media"), Path("/media"), Path("/mnt"), Path(os.path.expanduser("~"))]

        try:
            result = subprocess.run(
                ["findmnt", "-r", "-o", "TARGET,SOURCE"],
                capture_output=True,
                text=True,
                timeout=5
            )

            for line in result.stdout.split('\n'):
                if 'sd' in line.lower() or 'usb' in line.lower():
                    parts = line.split()
                    if len(parts) >= 1:
                        mount_path = Path(parts[0])
                        if mount_path.exists() and mount_path.is_dir():
                            logs_dir = mount_path / "LOGS"
                            if logs_dir.exists():
                                return mount_path
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        for base_path in possible_paths:
            if not base_path.exists():
                continue

            try:
                for item in base_path.iterdir():
                    if item.is_dir() and (item / "LOGS").exists():
                        return item
            except (PermissionError, OSError):
                pass

        return None

    def _find_msc_mount_macos(self) -> Optional[Path]:
        """Find USB MSC mount point on macOS"""
        volumes_path = Path("/Volumes")
        if not volumes_path.exists():
            return None

        try:
            for item in volumes_path.iterdir():
                if item.is_dir() and (item / "LOGS").exists():
                    return item
        except (PermissionError, OSError):
            pass

        return None

    def _find_msc_mount_windows(self) -> Optional[Path]:
        """Find USB MSC mount point on Windows"""
        import string

        for drive_letter in string.ascii_uppercase:
            drive_path = Path(f"{drive_letter}:\\")
            try:
                if drive_path.exists():
                    logs_dir = drive_path / "LOGS"
                    if logs_dir.exists():
                        return drive_path
            except (PermissionError, OSError):
                pass

        return None

    def clear_sd_card_logs(self) -> bool:
        """Clear old log files from SD card via USB Mass Storage."""
        mount_point = self.find_msc_mount_point()
        if not mount_point:
            return False

        logs_dir = mount_point / "LOGS"
        if not logs_dir.exists():
            return False

        try:
            deleted_files = 0
            for file_path in logs_dir.glob("*"):
                if file_path.is_file() and file_path.suffix.upper() in ['.LOG', '.BBL']:
                    try:
                        file_path.unlink()
                        deleted_files += 1
                    except (PermissionError, OSError):
                        pass

            return deleted_files > 0
        except (PermissionError, OSError):
            return False
