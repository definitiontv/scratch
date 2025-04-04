# Package Tracker

This script, `packagetracker.py`, is designed to collect information about installed packages on a Linux system and save it to a file. It supports multiple package managers, including APT, YUM, and Pacman.

## Features

*   Detects the system's package manager automatically.
*   Collects package names and versions.
*   Optionally collects detailed package information (description, dependencies).
*   Saves output in JSON or plain text format.
*   Supports gzip compression for output files.
*   Includes system metadata in the output (hostname, OS version, Python version, etc.).

## Usage

```
python packagetracker.py [options] [filename]
```

### Options

*   `--json`: Save output in JSON format.
*   `--gzip`: Compress output using gzip.
*   `--detailed`: Include detailed package information.
*   `--test`: Run in test mode (no file is written, but output is printed to the console).

### Arguments

*   `filename`: The name of the output file. If not specified, a timestamped filename will be used.

### Examples

*   Save package list to a JSON file:

    ```
    python packagetracker.py --json packages.json
    ```

*   Save package list to a compressed JSON file with detailed information:

    ```
    python packagetracker.py --json --gzip --detailed packages.json.gz
    ```

*   Run in test mode:

    ```
    python packagetracker.py --test
    ```

## Dependencies

*   `python3`
*   `distro` package: `pip install distro`

## Supported Package Managers

*   APT (Debian, Ubuntu)
*   YUM (CentOS, RHEL, Fedora)
*   Pacman (Arch Linux)
*   zypper (SUSE)

## Notes

*   The script requires appropriate permissions to run package manager commands (e.g., `dpkg-query`, `rpm`, `pacman`).
*   The `--detailed` option may take a long time to run, as it needs to query detailed information for each package.

## License

[Specify the license here]
