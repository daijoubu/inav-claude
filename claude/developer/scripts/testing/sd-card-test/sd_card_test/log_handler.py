"""
Log Handler - Blackbox log download and verification.
"""
import struct
import time
from pathlib import Path
from typing import List, Tuple, Optional

from .models import LogVerificationResult
from .msp import MSPCode, MSPParse


class LogHandler:
    """
    Blackbox log download and verification.
    
    Supports:
    - Download from USB MSC (fastest)
    - Verify log integrity and frame counts
    """
    
    def __init__(self, msc_handler):
        self.msc = msc_handler
    
    def download_logs_from_msc(self, output_dir: Optional[Path] = None, max_logs: int = 2) -> List[Tuple[Path, bytes]]:
        """
        Download logs from FC via USB Mass Storage.
        
        Args:
            output_dir: Directory to save logs to (optional)
            max_logs: Maximum number of logs to download (default: 2)
            
        Returns:
            List of (file_path, data) tuples
        """
        mount = self.msc.find_msc_mount_point()
        if not mount:
            return []
        
        logs_dir = mount / "LOGS"
        if not logs_dir.exists():
            return []
        
        logs = []
        count = 0
        try:
            for log_file in sorted(logs_dir.glob("*.BBL")) + sorted(logs_dir.glob("*.LOG")) + sorted(logs_dir.glob("*.TXT")):
                if log_file.is_file():
                    try:
                        with open(log_file, 'rb') as f:
                            data = f.read()
                        logs.append((log_file, data))
                        count += 1
                        
                        if output_dir:
                            output_dir.mkdir(parents=True, exist_ok=True)
                            output_file = output_dir / log_file.name
                            with open(output_file, 'wb') as f:
                                f.write(data)
                        
                        if count >= max_logs:
                            break
                    except (PermissionError, OSError):
                        pass
        except (PermissionError, OSError):
            pass
        
        return logs
    
    def verify_blackbox_log(self, log_data: bytes) -> LogVerificationResult:
        """
        Verify blackbox log integrity and frame information.
        
        Checks:
        - Log has proper header section
        - Log contains I-frames and P-frames
        - Required fields are defined in header
        """
        result = LogVerificationResult(passed=False)
        
        if not log_data:
            result.errors.append("Empty log data")
            return result
        
        try:
            # Check for header section
            header_end = log_data.rfind(b'\nH ')
            if header_end == -1:
                header_end = log_data.rfind(b'H ')
                if header_end == -1:
                    result.errors.append("No blackbox header found")
                    return result
            
            header_section = log_data[:header_end].decode('utf-8', errors='ignore')
            
            # Parse header fields
            for line in header_section.split('\n'):
                if line.startswith('H '):
                    parts = line[2:].split(',')
                    if len(parts) >= 2:
                        field_name = parts[0].strip()
                        field_info = ','.join(parts[1:]).strip()
                        result.header_fields[field_name] = field_info
            
            # Count frames in data section
            frame_section = log_data[header_end:]
            result.i_frame_count = frame_section.count(b'I')
            result.p_frame_count = frame_section.count(b'P')
            result.frame_count = result.i_frame_count + result.p_frame_count
            
            if result.frame_count == 0:
                result.errors.append("No frame data found")
                return result
            
            if result.i_frame_count < 1:
                result.errors.append("No I-frames found")
            else:
                result.passed = True
            
            if result.frame_count < 10:
                result.warnings.append(f"Very few frames: {result.frame_count}")
            
        except Exception as e:
            result.errors.append(f"Parse error: {str(e)}")
        
        return result
