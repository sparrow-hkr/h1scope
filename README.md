# h1scope

`h1scope` is a Go command-line tool that extracts target identifiers from a HackerOne scope CSV export. It can filter by scope and asset type, then print a unique target list or write it to a file.

## Build

Install Go, clone the repository, and build the executable:

```bash
git clone https://github.com/sparrow-hkr/h1scope.git
cd h1scope
go build -o h1scope main.go
```

The program uses only the Go standard library. There is no `go.mod` file or third-party dependency to install.

Check the build with:

```bash
./h1scope --version
./h1scope --help
```

You can also run it without building an executable:

```bash
go run main.go --list-types
```

## Usage

```text
h1scope [options] <csv>
```

Put options **before** the CSV path. The Go flag parser stops reading options at the first positional argument.

| Option | Behavior |
| --- | --- |
| `--in-scope` | Include targets eligible for submission unless their instruction contains `out of scope`. |
| `--out-of-scope` | Include targets that are ineligible for submission or whose instruction contains `out of scope`. |
| `-t TYPE`, `--type TYPE` | Include a specific asset type. Repeat the option to include multiple types. |
| `-o FILE`, `--output FILE` | Write identifiers to a file instead of standard output. |
| `--show-counts` | Print the number of unique matching identifiers to standard error. |
| `--list-types` | Show the supported type families; no CSV file is needed. |
| `--version` | Show the version; no CSV file is needed. |
| `-h`, `--help` | Show command help. |

`--in-scope` and `--out-of-scope` cannot be used together. With neither option, all rows are eligible for the asset type filter.

### Asset types

| Type | CSV `asset_type` values |
| --- | --- |
| `wildcard` | `WILDCARD` |
| `domain` | `DOMAIN` |
| `url` | `URL` |
| `cidr` | `CIDR`, `IP_ADDRESS`, `IP` |
| `android` | `GOOGLE_PLAY_APP_ID`, `ANDROID_APP_APK` |
| `ios` | `APPLE_APP_STORE_ID`, `IOS_APP_IPA` |

Type matching ignores letter case. A value outside this table is matched directly against the CSV `asset_type` value, so you can filter for another asset type present in your export. Each `-t` or `--type` option takes **one** value: use `-t wildcard -t domain`, not `-t wildcard domain`.

### Examples

Print in-scope wildcard targets:

```bash
./h1scope --in-scope -t wildcard program_scope.csv
```

Print in-scope wildcards and domains:

```bash
./h1scope --in-scope -t wildcard -t domain program_scope.csv
```

Write out-of-scope identifiers to a file and report the count:

```bash
./h1scope --out-of-scope --show-counts -o excluded.txt program_scope.csv
```

Print CIDR and IP targets for use in a pipeline:

```bash
./h1scope --in-scope -t cidr program_scope.csv
```

When `-o` is omitted, identifiers go to standard output, one per line. Duplicate identifiers and empty identifiers are omitted; the first occurrence determines output order. With `-o`, the file receives the identifiers and a completion message goes to standard output. `--show-counts` writes its count to standard error.

## CSV format

The first row must contain these columns:

- `identifier`
- `asset_type`
- `eligible_for_submission`

Column names are matched without regard to case or surrounding spaces. The optional `instruction` column is checked for the phrase `out of scope`, ignoring case. For `eligible_for_submission`, `true`, `1`, `yes`, `y`, and `t` count as true; other values count as false.

For example:

```csv
identifier,asset_type,eligible_for_submission,instruction
*.example.com,WILDCARD,true,
example.com,DOMAIN,true,
old.example.com,DOMAIN,false,Out of scope
```
