# h1scope

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey.svg)]()

`h1scope` is a fast, lightweight command-line utility designed for bug hunters and security teams to instantly parse, filter, and extract clean target lists from HackerOne program scope exports (`.csv`).

Stop manually cleaning up spreadsheets or wrestling with unreliable text-parsing one-liners. Seamlessly pipe in-scope wildcards, domains, CIDRs, and mobile apps directly into your automation pipelines (like `subfinder`, `naabu`, `httpx`, or `nuclei`).

---

## Features

* **Scope Separation**: Instantly split targets into `--in-scope` or `--out-of-scope`.
* **Granular Asset Filtering**: Filter by specific technical layers using the `-t` / `--type` flag:
  * `domain` / `wildcard` (perfect for subdomain recon)
  * `url` (for web vulnerability scanners)
  * `cidr` / `ip` (for network scanning and infrastructure mapping)
  * `android` / `ios` (for mobile app reversing targets)
* **Pipeline Ready**: Outputs to standard output (`stdout`) by default so you can pipe it directly into your favorite tools, or use `-o` to save directly to a file.
* **Robust Parsing**: Built on top of `pandas` to accurately handle nested commas, markdown formatting, and quotes within HackerOne instructions without breaking your bash terminal.

---

## Installation

### Prerequisites
Make sure you have Python 3.7+ and `pip` installed.

### 1. Clone the Repository
```bash
git clone https://github.com/sparrow-hkr/h1scope.git
cd h1scope
```
### Install Dependencies
```bash
pip install pandas
```
### Make Executable (Linux/macOS)
```bash
chmod +x h1scope.py
```
### Optional: link to your local bin to run as a global command
```bash
sudo ln -s "$(pwd)/h1scope.py" /usr/local/bin/h1scope
```
### or uses tool inside git repo
```bash
python3 mani.py --help
```
## Usage
```text
positional arguments:
  csv                   Path to the HackerOne exported .csv file

options:
  -h, --help            show this help message and exit
  --in-scope            Filter for In-Scope targets only
  --out-of-scope        Filter for Out-of-Scope targets only
  -t, --type {url,domain,wildcard,cidr,android,ios} [{url,domain,wildcard,cidr,android,ios} ...]
                        Filter by specific asset types (space separated)
  -o, --output OUTPUT   Output file path (prints to terminal if omitted)
  ```
## Examples

### 1. Extract In-Scope Wildcards
Extract only the wildcard domains from a program's scope and save them to a file ready for subfinder:

```bash
h1scope program_scope.csv --in-scope -t wildcard -o wildcards.txt
```

### 2. Live Automation Piping (The Recon Pipeline)
Stream in-scope web assets directly into subfinder and httpx without saving intermediary text files:

```bash
h1scope program_scope.csv --in-scope -t wildcard domain | subfinder | httpx -silent -o live_subs.txt
```

### 3. Map Network Infrastructure
Filter for target IP addresses and CIDR blocks to pass directly into nmap or naabu:

```bash
h1scope program_scope.csv --in-scope -t cidr | naabu -p - -o open_ports.txt
```

### 4 Full Scope Dump (Everything In-Scope)
If you want to grab absolutely every valid asset type in the document without filtering by technology layer, simply omit the -t flag entirely:

```bash
h1scope scope.csv --in-scope -o entire_scope.txt
```

### 5. Identify Banned/Out-of-Scope Targets
Keep track of what you are not allowed to touch during a live engagement to prevent out-of-scope penalties:

```bash
h1scope program_scope.csv --out-of-scope -o do_not_touch.txt
```

## The `--type` Flag Reference Guide

The `-t` (or `--type`) flag accepts multiple space-separated values. You can combine them in any order depending on what your recon tools require.

### Supported Filter Values

| Value | Targets Extracted | Best Used For |
| :--- | :--- | :--- |
| **`wildcard`** | Subdomain scopes (e.g., `*.example.com`) | Subdomain discovery (`subfinder`, `amass`) |
| **`domain`** | Root/Apex domains (e.g., `example.com`) | Target mapping & vertical scanning |
| **`url`** | Specific endpoints, paths, or APIs | Web scanning (`httpx`, `nuclei`, `dirsearch`) |
| **`cidr`** | Network ranges and standalone IPs | Port scanning & infra mapping (`nmap`, `naabu`) |
| **`android`** | Google Play IDs and `.apk` targets | Mobile reversing & static analysis |
| **`ios`** | App Store IDs and `.ipa` targets | iOS application penetration testing |

> 💡 **Pro-Tip (Raw Fallback):** `h1scope` automatically handles raw HackerOne categories. If a program uses unconventional types, you can pass them directly in lowercase (e.g., `-t source_code` for GitHub repos, or `-t hardware` for IoT targets).

# License
Distributed under the MIT License. See LICENSE for more information.
```
```
---

## Connect with Me

If you have questions, feature requests, or just want to talk shop about bug bounties and recon pipelines, feel free to reach out!

- **Twitter/X:** [@chandra_na49882](https://x.com/chandra_na49882)
- **LinkedIn:** [Your Name](https://linkedin.com/in/YOUR_USERNAME)
