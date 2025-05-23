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

### Using the Bash Wrapper (`packagetracker.sh`)

The `packagetracker.sh` script provides a convenient bash wrapper around the `packagetracker.py` script.

**How to run:**

```bash
./packagetracker.sh [options] [filename]
```

**Options:**

The wrapper supports several options to control output format and content, such as `--json`, `--gzip`, and `--detailed`. These options are passed directly to the underlying `packagetracker.py` script. For a full list of options and their descriptions, run:

```bash
./packagetracker.sh --help
```

**Arguments:**

*   `filename`: Optional. The name of the output file. If not specified, a timestamped filename will be used by `packagetracker.py`.

**Examples:**

*   Save package list to a JSON file using the wrapper:

    ```bash
    ./packagetracker.sh --json packages.json
    ```

*   Run in test mode using the wrapper:

    ```bash
    ./packagetracker.sh --test
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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
