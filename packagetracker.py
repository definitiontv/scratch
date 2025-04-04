import subprocess
import platform
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

def save_packages_to_file(filename: str = "currentpackages.txt") -> None:
    """Save currently installed packages to file with timestamp.
    
    Args:
        filename: Output file name (default: currentpackages.txt)
    """
    try:
        packages = get_installed_packages()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(filename, "w") as f:
            f.write(f"Package snapshot taken at: {timestamp}\n")
            f.write(f"System: {platform.system()} {platform.release()}\n")
            f.write(f"Package manager: {detect_package_manager()}\n\n")
            for pkg, ver in sorted(packages.items()):
                f.write(f"{pkg}: {ver}\n")
                
    except Exception as e:
        raise RuntimeError(f"Failed to save packages: {str(e)}")
if __name__ == "__main__":
    try:
        save_packages_to_file()
        print("Successfully saved package list to currentpackages.txt")
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)
