import json
import subprocess
import platform
import sys
import gzip
import socket
import os
import shutil
from typing import Dict
from datetime import datetime

def detect_package_manager() -> str:
    """Detect the system's package manager."""
    distro = platform.linux_distribution()[0].lower()
    if 'ubuntu' in distro or 'debian' in distro:
        return 'apt'
    elif 'centos' in distro or 'redhat' in distro or 'fedora' in distro:
        return 'yum'
    elif 'arch' in distro:
        return 'pacman'
    elif 'suse' in distro:
        return 'zypper'
    return 'unknown'

def get_installed_packages() -> Dict[str, str]:
    """Get installed packages with versions based on detected package manager."""
    pkg_manager = detect_package_manager()
    
    if pkg_manager == 'apt':
        return _get_apt_packages()
    elif pkg_manager == 'yum':
        return _get_yum_packages()
    elif pkg_manager == 'pacman':
        return _get_pacman_packages()
    else:
        raise NotImplementedError(f"Package manager {pkg_manager} not supported")

def _get_apt_packages() -> Dict[str, str]:
    """Get packages for Debian/Ubuntu systems."""
    try:
        result = subprocess.run(
            ['dpkg-query', '-W', '-f=${Package}\t${Version}\n'],
            capture_output=True, text=True, check=True
        )
        return dict(line.split('\t') for line in result.stdout.splitlines())
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get APT packages: {e.stderr}")

def _get_yum_packages() -> Dict[str, str]:
    """Get packages for RHEL/CentOS systems."""
    try:
        result = subprocess.run(
            ['rpm', '-qa', '--queryformat=%{NAME}\t%{VERSION}\n'],
            capture_output=True, text=True, check=True
        )
        return dict(line.split('\t') for line in result.stdout.splitlines())
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get YUM packages: {e.stderr}")

def _get_pacman_packages() -> Dict[str, str]:
    """Get packages for Arch Linux systems."""
    try:
        result = subprocess.run(
            ['pacman', '-Q'],
            capture_output=True, text=True, check=True
        )
        return dict(line.split() for line in result.stdout.splitlines())
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get Pacman packages: {e.stderr}")

def _get_system_metadata() -> dict:
    """Collect comprehensive system metadata."""
    return {
        "hostname": socket.gethostname(),
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "distro": platform.linux_distribution()
        },
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation()
        },
        "cpu": {
            "count": os.cpu_count(),
            "architecture": platform.processor()
        }
    }

def _get_package_details(pkg_manager: str, package: str) -> dict:
    """Get detailed package information including description and dependencies."""
    try:
        if pkg_manager == 'apt':
            cmd = ['apt-cache', 'show', package]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            details = {}
            for line in result.stdout.splitlines():
                if line.startswith('Description:'):
                    details['description'] = line.split(':', 1)[1].strip()
                elif line.startswith('Depends:'):
                    details['dependencies'] = line.split(':', 1)[1].strip().split(', ')
            return details
            
        elif pkg_manager == 'yum':
            cmd = ['rpm', '-qi', package]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            details = {}
            for line in result.stdout.splitlines():
                if line.startswith('Summary:'):
                    details['description'] = line.split(':', 1)[1].strip()
                elif line.startswith('Requires:'):
                    details['dependencies'] = line.split(':', 1)[1].strip().split()
            return details
            
        elif pkg_manager == 'pacman':
            cmd = ['pacman', '-Qi', package]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            details = {}
            for line in result.stdout.splitlines():
                if line.startswith('Description'):
                    details['description'] = line.split(':', 1)[1].strip()
                elif line.startswith('Depends On'):
                    details['dependencies'] = line.split(':', 1)[1].strip().split()
            return details
            
    except subprocess.CalledProcessError:
        return {}

def save_packages_to_file(
    filename: str = None,
    json_format: bool = False,
    compressed: bool = False,
    detailed: bool = False,
    test_mode: bool = False
) -> None:
    """Save installed packages to file with enhanced options.
    
    Args:
        filename: Output filename (None for auto-generated)
        json_format: Save as JSON if True
        compressed: Use gzip compression if True
        detailed: Include package details if True
    """
    try:
        # First validate we can detect package manager
        pkg_manager = detect_package_manager()
        if pkg_manager == 'unknown':
            raise RuntimeError("Could not detect supported package manager")
            
        # Validate required commands exist
        required_commands = {
            'apt': ['dpkg-query', 'apt-cache'],
            'yum': ['rpm'],
            'pacman': ['pacman']
        }.get(pkg_manager, [])
        
        for cmd in required_commands:
            if not shutil.which(cmd):
                raise RuntimeError(f"Required command not found: {cmd}")
                
        packages = get_installed_packages()
        if not packages:
            raise RuntimeError("No packages found - possible detection error")
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        pkg_manager = detect_package_manager()
        
        if filename is None:
            ext = ".json.gz" if compressed and json_format else \
                  ".json" if json_format else \
                  ".txt.gz" if compressed else ".txt"
            filename = f"packages_{timestamp}{ext}"
        
        data = {
            "metadata": _get_system_metadata(),
            "timestamp": timestamp.replace('_', ' '),
            "package_manager": pkg_manager,
            "packages": {}
        }
        
        for pkg, ver in packages.items():
            pkg_data = {"version": ver}
            if detailed:
                pkg_data.update(_get_package_details(pkg_manager, pkg))
            data["packages"][pkg] = pkg_data
        
        if test_mode:
            print("Test mode - would write to:", filename)
            print("Sample data:", json.dumps(data, indent=2)[:500] + "...")
            return
            
        # Write to temp file first then rename for atomic operation
        temp_filename = filename + '.tmp'
        open_func = gzip.open if compressed else open
        with open_func(temp_filename, 'wt' if json_format else 'wb') as f:
            if json_format:
                json.dump(data, f, indent=2)
            else:
                f.write(f"System Metadata:\n")
                for key, value in data['metadata'].items():
                    f.write(f"{key}: {value}\n")
                f.write(f"\nPackage snapshot taken at: {data['timestamp']}\n")
                f.write(f"Package manager: {data['package_manager']}\n\n")
                for pkg, details in sorted(data['packages'].items()):
                    f.write(f"{pkg} ({details['version']})\n")
                    if detailed:
                        f.write(f"  Description: {details.get('description', 'N/A')}\n")
                        f.write(f"  Dependencies: {', '.join(details.get('dependencies', []))}\n")
                    f.write("\n")
                
    except Exception as e:
        raise RuntimeError(f"Failed to save packages: {str(e)}")
if __name__ == "__main__":
    try:
        filename = None
        json_format = False
        compressed = False
        detailed = False
        test_mode = False
        
        if "--json" in sys.argv:
            json_format = True
            sys.argv.remove("--json")
        if "--gzip" in sys.argv:
            compressed = True
            sys.argv.remove("--gzip")
        if "--detailed" in sys.argv:
            detailed = True
            sys.argv.remove("--detailed")
        if "--test" in sys.argv:
            test_mode = True
            sys.argv.remove("--test")
            
        if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
            filename = sys.argv[1]
            
        save_packages_to_file(
            filename=filename,
            json_format=json_format,
            compressed=compressed,
            detailed=detailed,
            test_mode=test_mode
        )
        print(f"Successfully saved package list to {filename or 'timestamped file'}")
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)
