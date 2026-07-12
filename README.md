# h1scope

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey.svg)]()

`h1scope` is a lightweight command-line tool for parsing HackerOne scope exports and turning them into clean, filtered target lists.

It is designed for bug hunters, security researchers, and recon pipelines that need quick access to:

- in-scope or out-of-scope targets
- wildcard domains
- apex domains
- URLs
- CIDR blocks and IPs
- Android and iOS app targets

The tool reads a HackerOne CSV export, filters rows by scope and asset type, and prints the matching identifiers to standard output or writes them to a file.

## Highlights

- Scope filtering with `--in-scope` and `--out-of-scope`
- Multiple asset types with `-t` / `--type`
- Strict wildcard matching for `-t wildcard`
- Output to stdout for piping, or `-o` for file export
- `--list-types` to show supported asset families
- `--show-counts` to print the number of matched rows
- `--version` and `--sersion` for version output

## Installation

### Requirements

- Python 3.7 or newer
- `pip`

### Clone the repository

```bash
git clone https://github.com/sparrow-hkr/h1scope.git
cd h1scope
```

### Install dependencies

```bash
pip install pandas
```

### Make the script executable

```bash
chmod +x main.py
```

### Optional: install as a local command

```bash
sudo ln -s "$(pwd)/main.py" /usr/local/bin/h1scope
```

### Verify the tool

```bash
python3 main.py --help
```

## Usage

```text
usage: h1scope [-h] [--in-scope | --out-of-scope] [-t TYPE [TYPE ...]]
               [--list-types] [--show-counts] [--version] [-o OUTPUT]
               [csv]

positional arguments:
  csv                   Path to the HackerOne exported .csv file

options:
  -h, --help            show this help message and exit
  --in-scope            Filter for In-Scope targets only
  --out-of-scope        Filter for Out-of-Scope targets only
  -t, --type TYPE [TYPE ...]
                        Filter by specific asset types
  --list-types          Show supported asset types and exit
  --show-counts         Print the number of matched targets to stderr
  --version, --sersion  Show version and exit
  -o, --output OUTPUT   Output file path
```

## Supported Asset Types

Use `--list-types` to see the current supported families:

```bash
h1scope --list-types
```

Supported values:

- `wildcard` - wildcard subdomain entries
- `domain` - apex or root domains
- `url` - endpoints, paths, or APIs
- `cidr` - network ranges and standalone IPs
- `android` - Google Play IDs and APK targets
- `ios` - App Store IDs and IPA targets

## Output Behavior

By default, the tool prints matching identifiers to `stdout`, which makes it easy to pipe into other tools.

Example:

```bash
h1scope program_scope.csv --in-scope -t wildcard | subfinder
```

If you pass `-o`, the results are written to a file instead:

```bash
h1scope program_scope.csv --in-scope -t wildcard -o wildcards.txt
```

If you also pass `--show-counts`, the count is printed to `stderr` so it does not interfere with piping.

## Examples

### 1. Show all in-scope wildcard targets

```bash
h1scope program_scope.csv --in-scope -t wildcard
```

### 2. Export in-scope wildcard targets to a file

```bash
h1scope program_scope.csv --in-scope -t wildcard -o wildcards.txt
```

### 3. Combine multiple asset types

```bash
h1scope program_scope.csv --in-scope -t wildcard domain url
```

This returns any row matching one of the requested types.

### 4. Pipe wildcard targets into subfinder

```bash
h1scope program_scope.csv --in-scope -t wildcard | subfinder
```

### 5. Pipe network targets into naabu

```bash
h1scope program_scope.csv --in-scope -t cidr | naabu -p -
```

### 6. Export all out-of-scope entries

```bash
h1scope program_scope.csv --out-of-scope -o do_not_touch.txt
```

### 7. Show the matched row count

```bash
h1scope program_scope.csv --in-scope -t wildcard --show-counts
```

### 8. Show the version

```bash
h1scope --version
```

## Type Matching Notes

The `-t` / `--type` flag accepts multiple values separated by spaces.

Important behavior:

- type matching is exact by asset family
- `-t wildcard` returns wildcard rows only
- multiple values are combined with OR logic
- unrecognized values are matched literally in uppercase form

Examples:

```bash
h1scope program_scope.csv --in-scope -t wildcard domain
h1scope program_scope.csv --in-scope -t url cidr
```

## Tips for Better Results

- Use `--in-scope` when you want active targets only
- Use `--out-of-scope` when you want to track exclusions
- Use `-t wildcard` for subdomain recon pipelines
- Use `-t cidr` for infrastructure scanning workflows
- Use `--show-counts` when you want a quick sanity check on the number of matches

## CSV Requirements

The exporter expects these columns in the HackerOne CSV:

- `identifier`
- `asset_type`
- `eligible_for_submission`

If `instruction` is present, it is used to help detect out-of-scope rows.

## Common Workflows

### Recon pipeline

```bash
h1scope program_scope.csv --in-scope -t wildcard | subfinder | httpx -silent
```

### Port scanning

```bash
h1scope program_scope.csv --in-scope -t cidr | naabu -p -
```

### Full scope export

```bash
h1scope program_scope.csv --in-scope -o entire_scope.txt
```

## Troubleshooting

### The tool prints an error about missing columns

Make sure the CSV is a HackerOne scope export and contains the required columns listed above.

### `--list-types` works without a CSV

This is intentional. It is a helper command and does not require an input file.

### `--show-counts` does not change the output stream

This is also intentional. The count is written to `stderr` so you can still pipe results cleanly.

## License

Distributed under the MIT License. See `LICENSE` for details.
