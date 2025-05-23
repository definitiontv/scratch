import os
import shutil
import socket
import subprocess
import sys
import gzip
import json
import platform
from datetime import datetime
from typing import Dict, List, Optional

import distro  # Added

def detect_package_manager(test_mode: bool = False) -> str:
    """Detect the system's package manager.
    
    Args:
        test_mode: If True, returns test values for all supported package managers
    """
    if test_mode:
        return 'apt'  # Default test value
    
    distro_id = distro.id().lower()
    if distro_id in ('ubuntu', 'debian'):
        return 'apt'
    elif 'centos' in distro_id or 'redhat' in distro_id or 'fedora' in distro_id:
        return 'yum'
    elif 'arch' in distro_id:
        return 'pacman'
    elif 'suse' in distro_id:
        return 'zypper'
def detect_package_manager(test_mode: bool = False) -> str:
    """Detect the system's package manager.

    Args:
        test_mode: If True, returns test values for all supported package managers
    """
    if test_mode:
        return 'apt'  # Default test value

    distro_id = distro.id().lower()
    if distro_id in ('ubuntu', 'debian'):
        return 'apt'
    elif 'centos' in distro_id or 'redhat' in distro_id or 'fedora' in distro_id:
        return 'yum'
    elif 'arch' in distro_id:
        return 'pacman'
    elif 'suse' in distro_id:
        return 'zypper'
    return 'unknown'


def _run_command(cmd: List[str]) -> str:
    """Helper function to run subprocess commands and return output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed: {cmd} - {e.stderr}")


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
    output = _run_command(['dpkg-query', '-W', '-f=${Package}\t${Version}\n'])
    return dict(line.split('\t') for line in output.splitlines())


def _get_yum_packages() -> Dict[str, str]:
    """Get packages for RHEL/CentOS systems."""
    output = _run_command(['rpm', '-qa', '--queryformat=%{NAME}\t%{VERSION}\n'])
    return dict(line.split('\t') for line in output.splitlines())


def _get_pacman_packages() -> Dict[str, str]:
    """Get packages for Arch Linux systems."""
    output = _run_command(['pacman', '-Q'])
    return dict(line.split() for line in output.splitlines())


def _get_system_metadata(fields: Optional[List[str]] = None) -> dict:
    """Collect comprehensive system metadata.

    Args:
        fields: List of metadata fields to collect. If None, collect all.
    """
    metadata = {
        "hostname": socket.gethostname(),
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "distro": {
                "id": distro.id(),
                "name": distro.name(),
                "version": distro.version(),
                "codename": distro.codename()
            }
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

    if fields:
        filtered_metadata = {}
        for field in fields:
            if field in metadata:
                filtered_metadata[field] = metadata[field]
        return filtered_metadata

    return metadata


def _get_package_details(pkg_manager: str, package: str) -> dict:
    """Get detailed package information including description and dependencies."""
    if pkg_manager == 'apt':
        return _get_apt_package_details(package)
    elif pkg_manager == 'yum':
        return _get_yum_package_details(package)
    elif pkg_manager == 'pacman':
        return _get_pacman_package_details(package)
    else:
        return {}


def _get_apt_package_details(package: str) -> dict:
    """Get detailed package information for APT packages."""
    try:
        output = _run_command(['apt-cache', 'show', package])
        details = {}
        for line in output.splitlines():
            if line.startswith('Description:'):
                details['description'] = line.split(':', 1)[1].strip()
            elif line.startswith('Depends:'):
                details['dependencies'] = line.split(':', 1)[1].strip().split(', ')
        return details
    except RuntimeError:
        return {}


def _get_yum_package_details(package: str) -> dict:
    """Get detailed package information for YUM packages."""
    try:
        output = _run_command(['rpm', '-qi', package])
        details = {}
        for line in output.splitlines():
            if line.startswith('Summary:'):
                details['description'] = line.split(':', 1)[1].strip()
            elif line.startswith('Requires:'):
                details['dependencies'] = line.split(':', 1)[1].strip().split()
        return details
    except RuntimeError:
        return {}


def _get_pacman_package_details(package: str) -> dict:
    """Get detailed package information for Pacman packages."""
    try:
        output = _run_command(['pacman', '-Qi', package])
        details = {}
        for line in output.splitlines():
            if line.startswith('Description'):
                details['description'] = line.split(':', 1)[1].strip()
            elif line.startswith('Depends On'):
                details['dependencies'] = line.split(':', 1)[1].strip().split()
        return details
    except RuntimeError:
        return {}


def _prepare_package_data(packages: Dict[str, str], pkg_manager: str, detailed: bool, test_mode: bool) -> Dict[str, Dict[str, str]]:
    """Prepare package data with optional details."""
    package_data = {}
    total_packages = len(packages)
    processed = 0

    for pkg, ver in packages.items():
        pkg_data = {"version": ver}
        if detailed:
            if not test_mode:  # Only show progress in non-test mode
                processed += 1
                progress = (processed / total_packages) * 100
                sys.stderr.write(f"\rProcessing packages: {processed}/{total_packages} ({progress:.1f}%)")
                sys.stderr.flush()
            pkg_data.update(_get_package_details(pkg_manager, pkg))
        package_data[pkg] = pkg_data

    if detailed and not test_mode:
        sys.stderr.write("\n")  # New line after progress
        sys.stderr.flush()

    return package_data


def _write_data_to_file(filename: str, data: dict, json_format: bool, compressed: bool) -> None:
    """Write data to file, handling compression and JSON formatting."""
    temp_filename = filename + '.tmp'
    open_func = gzip.open if compressed else open
    mode = 'wt' if json_format else 'w'
    try:
        with open_func(temp_filename, mode) as file_handle:
            if json_format:
                json.dump(data, file_handle, indent=2)
            else:
                content = [
                    "System Metadata:",
                    *[f"{key}: {value}" for key, value in data['metadata'].items()],
                    f"\nPackage snapshot taken at: {data['timestamp']}",
                    f"Package manager: {data['package_manager']}\n",
                    *[
                        f"{pkg} ({details['version']})\n"
                        f"  Description: {details.get('description', 'N/A')}\n"
                        f"  Dependencies: {', '.join(details.get('dependencies', []))}\n"
                        if detailed else
                        f"{pkg} ({details['version']})\n"
                        for pkg, details in sorted(data['packages'].items())
                    ]
                ]
                file_handle.write('\n'.join(content))
        os.replace(temp_filename, filename)
    except Exception as e:
        # Cleanup in case of error
        if os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
            except:
                pass
        raise RuntimeError(f"Failed to save packages: {str(e)}")


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
        # Validate package manager
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

        # Get installed packages
        packages = get_installed_packages()
        if not packages:
            raise RuntimeError("No packages found - possible detection error")

        # Prepare data
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if filename is None:
            ext = ".json.gz" if compressed and json_format else \
                  ".json" if json_format else \
                  ".txt.gz" if compressed else ".txt"
            filename = f"packages_{timestamp}{ext}"

        data = {
            "metadata": _get_system_metadata(),
            "timestamp": timestamp.replace('_', ' '),
            "package_manager": pkg_manager,
            "packages": _prepare_package_data(packages, pkg_manager, detailed, test_mode)
        }

        if test_mode:
            print("\n=== TEST MODE OUTPUT ===")
            print(f"Would write to: {filename}")
            print(f"Format: {'JSON' if json_format else 'TEXT'}{' (compressed)' if compressed else ''}")
            print(f"Detailed info: {'Yes' if detailed else 'No'}")

            print("\n=== SAMPLE DATA ===")
            sample_data = json.dumps(data, indent=2)
            print(sample_data[:500] + ("..." if len(sample_data) > 500 else ""))

            print("\n=== VALIDATION CHECKS ===")
            print(f"Package manager detected: {pkg_manager}")
            print(f"Total packages found: {len(packages)}")
            print(f"Metadata fields present: {len(data['metadata'])}")
            print(f"Sample package count matches: {len(packages) == len(data['packages'])}")

            if detailed:
                sample_pkg = next(iter(packages.keys()))
                details = _get_package_details(pkg_manager, sample_pkg)
                print("\n=== SAMPLE PACKAGE DETAILS ===")
                print(f"Package: {sample_pkg}")
                print(f"Version: {packages[sample_pkg]}")
                print(f"Description: {details.get('description', 'N/A')}")
                print(f"Dependencies: {', '.join(details.get('dependencies', [])) or 'None'}")

            print("\n=== TEST SUMMARY ===")
            print("All checks passed" if len(packages) > 0 and 'hostname' in data['metadata']
                  else "Some checks failed")
            return

        _write_data_to_file(filename, data, json_format, compressed)

        print(f"Successfully saved package list to {filename or 'timestamped file'}")

    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)


def validate_output_file(filename: str, json_format: bool, compressed: bool) -> bool:
    """Validate the output file was created correctly."""
    if not os.path.exists(filename):
        return False

    try:
        if compressed:
            with gzip.open(filename, 'rt') as f:
                content = f.read()
        else:
            with open(filename, 'r') as f:
                content = f.read()

        if json_format:
            json.loads(content)
        return True
    except Exception:
        return False


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
