"""
Configuration Handler.

FC configuration validation and application.
"""
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional, List, Dict


class ConfigHandler:
    """
    Flight controller configuration operations.
    
    Handles configuration validation, diff application, and baseline config management.
    """
    
    def __init__(self, port: str, baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
    
    def validate_configuration(self, config_file: str = "baseline-fc-config.txt") -> Dict:
        """
        Validate FC configuration against baseline requirements.
        
        Checks for:
        - Motor mixer (4 motors)
        - Servo mixer (4 servos)
        - GPS feature enabled
        - PWM_OUTPUT_ENABLE enabled
        - Blackbox rate set correctly
        - Serial ports configured
        
        Returns:
            dict with 'valid', 'issues', 'details' keys
        """
        result = {
            'valid': True,
            'issues': [],
            'config': None,
            'details': {}
        }
        
        try:
            config_text = None
            config_path = None
            
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config_text = f.read()
                config_path = config_file
            else:
                return {
                    'valid': False,
                    'issues': [f'Config file not found: {config_file}'],
                    'config': None,
                    'details': {}
                }
            
            if not config_text:
                return {
                    'valid': False,
                    'issues': ['No configuration data'],
                    'config': None,
                    'details': {}
                }
            
            result['config'] = config_path
            
            # Parse configuration
            lines = config_text.split('\n')
            
            has_gps = False
            has_pwm_output = False
            motor_mixer_lines = []
            servo_mixer_lines = []
            blackbox_rate = None
            serial_ports = []
            
            in_motor_mixer = False
            in_servo_mixer = False
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if 'blackbox_rate_denom' in line and '=' in line:
                    try:
                        value_part = line.split('=')[1].strip()
                        blackbox_rate = int(value_part)
                    except:
                        pass
                
                if line.startswith('feature GPS'):
                    has_gps = True
                elif line.startswith('feature PWM_OUTPUT_ENABLE'):
                    has_pwm_output = True
                elif line == 'mmix reset':
                    in_motor_mixer = True
                elif in_motor_mixer and line.startswith('mmix '):
                    motor_mixer_lines.append(line)
                elif line.startswith('smix reset'):
                    in_motor_mixer = False
                    in_servo_mixer = True
                elif in_servo_mixer and line.startswith('smix '):
                    servo_mixer_lines.append(line)
                elif line.startswith('mixer_profile') or line.startswith('set '):
                    in_servo_mixer = False
                elif line.startswith('serial '):
                    serial_ports.append(line)
            
            result['details'] = {
                'has_gps': has_gps,
                'has_pwm_output': has_pwm_output,
                'motor_mixer_count': len(motor_mixer_lines),
                'servo_mixer_count': len(servo_mixer_lines),
                'blackbox_rate_denom': blackbox_rate,
                'serial_ports': len(serial_ports),
            }
            
            if not has_gps:
                result['issues'].append("GPS feature not enabled")
                result['valid'] = False
            
            if not has_pwm_output:
                result['issues'].append("PWM_OUTPUT_ENABLE feature not enabled")
                result['valid'] = False
            
            if len(motor_mixer_lines) != 4:
                result['issues'].append(f"Motor mixer: expected 4 motors, found {len(motor_mixer_lines)}")
                result['valid'] = False
            
            if len(servo_mixer_lines) != 4:
                result['issues'].append(f"Servo mixer: expected 4 servos, found {len(servo_mixer_lines)}")
                result['valid'] = False
            
            if blackbox_rate != 2:
                result['issues'].append(f"Blackbox rate: expected denom=2, found denom={blackbox_rate}")
                result['valid'] = False
            
            if len(serial_ports) < 2:
                result['issues'].append(f"Serial ports: expected at least 2, found {len(serial_ports)}")
                result['valid'] = False
            
            return result
            
        except Exception as e:
            result['issues'].append(f"Validation error: {str(e)}")
            result['valid'] = False
            return result
    
    def apply_diff(self, settings: Dict) -> bool:
        """
        Apply minimal configuration diff using cliterm -f.
        
        Args:
            settings: Dictionary of settings to apply
            
        Returns:
            True if applied successfully
        """
        if not settings:
            return True
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                diff_file = f.name
                for key, value in settings.items():
                    f.write(f"set {key} = {value}\n")
                f.write("save\n")
            
            cmd = f"cliterm -d {self.port} -f {diff_file}"
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            try:
                stdout, stderr = process.communicate(timeout=30)
            except subprocess.TimeoutExpired:
                process.kill()
                print("  ERROR: cliterm timed out")
                return False
            
            if process.returncode != 0:
                print(f"  ERROR: cliterm failed with code {process.returncode}")
                return False
            
            print("  ✓ Configuration applied")
            return True
            
        except Exception as e:
            print(f"  ERROR: Failed to apply configuration: {e}")
            return False
        finally:
            try:
                os.unlink(diff_file)
            except:
                pass
    
    def apply_baseline(self, config_file: str) -> bool:
        """
        Apply full baseline configuration.
        
        Args:
            config_file: Path to baseline configuration file
            
        Returns:
            True if applied successfully
        """
        if not os.path.exists(config_file):
            print(f"ERROR: Baseline config not found: {config_file}")
            return False
        
        try:
            with open(config_file, 'r') as f:
                lines = f.readlines()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                diff_file = f.name
                in_batch = False
                for line in lines:
                    line = line.rstrip()
                    if not line or line.startswith('#'):
                        continue
                    if line == 'batch start':
                        in_batch = True
                        continue
                    elif line == 'batch end':
                        in_batch = False
                        continue
                    if in_batch or line in ['save', 'defaults noreboot']:
                        f.write(line + '\n')
            
            cmd = f"cliterm -d {self.port} -f {diff_file}"
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            try:
                stdout, stderr = process.communicate(timeout=30)
            except subprocess.TimeoutExpired:
                process.kill()
                print("  ERROR: cliterm timed out")
                return False
            
            if process.returncode != 0:
                print(f"  ERROR: cliterm failed")
                return False
            
            print("  ✓ Baseline configuration applied")
            return True
            
        except Exception as e:
            print(f"  ERROR: Failed to apply baseline: {e}")
            return False
        finally:
            try:
                os.unlink(diff_file)
            except:
                pass
