#!/usr/bin/env python3
import argparse
import sys
import pandas as pd

VERSION = "1.0.0"

def parse_scope(csv_path, scope_type, asset_types, output_file, show_counts=False):
    try:
        # Load the CSV
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"[-] Error reading CSV file: {e}", file=sys.stderr)
        sys.exit(1)

    # Standardize column names just in case HackerOne changes casing
    df.columns = [col.lower().strip() for col in df.columns]

    # Required columns validation
    required = ['identifier', 'asset_type', 'eligible_for_submission']
    if not all(col in df.columns for col in required):
        print(f"[-] Error: CSV missing one of the required columns: {required}", file=sys.stderr)
        print(f"Found columns: {list(df.columns)}", file=sys.stderr)
        sys.exit(1)

    # 1. Scope Filtering (In-Scope vs Out-of-Scope)
    if scope_type == 'in':
        # Eligible for submission, and instruction doesn't explicitly say out of scope
        df = df[df['eligible_for_submission'] == True]
        if 'instruction' in df.columns:
            df = df[~df['instruction'].str.contains('out of scope', case=False, na=False)]
    elif scope_type == 'out':
        # Either not eligible, or explicitly marked out of scope in instructions
        condition = (df['eligible_for_submission'] == False)
        if 'instruction' in df.columns:
            condition |= df['instruction'].str.contains('out of scope', case=False, na=False)
        df = df[condition]

    # 2. Asset Type Filtering
    if asset_types:
        # Map user-friendly flags to standard HackerOne asset_type strings.
        # Keep the matching exact so `-t wildcard` only returns wildcard rows.
        type_mapping = {
            'url': ['URL'],
            'domain': ['DOMAIN'],
            'wildcard': ['WILDCARD'],
            'cidr': ['CIDR', 'IP_ADDRESS', 'IP'],
            'android': ['GOOGLE_PLAY_APP_ID', 'ANDROID_APP_APK'],
            'ios': ['APPLE_APP_STORE_ID', 'IOS_APP_IPA']
        }
        
        target_types = []
        for t in asset_types:
            t_lower = t.lower()
            if t_lower in type_mapping:
                target_types.extend(type_mapping[t_lower])
            else:
                # Fallback to literal matching if user types something specific
                target_types.append(t.upper())
        
        # Apply the type filter using normalized casing for resilient matching.
        asset_type_values = df['asset_type'].fillna('').astype(str).str.upper()
        df = df[asset_type_values.isin(target_types)]

    # Extract clean list of identifiers
    results = df['identifier'].dropna().unique()

    # 3. Output handling
    if output_file:
        with open(output_file, 'w') as f:
            for item in results:
                f.write(f"{item}\n")
        print(f"[+] Successfully wrote {len(results)} targets to {output_file}")
    else:
        # Print directly to stdout (useful for piping into other tools)
        for item in results:
            print(item)

    if show_counts:
        print(f"[+] Matched {len(results)} targets", file=sys.stderr)


def list_types():
    types = [
        ('wildcard', 'Wildcard subdomain entries'),
        ('domain', 'Apex/root domains'),
        ('url', 'Specific endpoints, paths, or APIs'),
        ('cidr', 'Network ranges and standalone IPs'),
        ('android', 'Google Play IDs and APK targets'),
        ('ios', 'App Store IDs and IPA targets'),
    ]

    print("Supported types:")
    for name, description in types:
        print(f"  {name:<9} {description}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="h1scope",
        description="HackerOne CSV Scope Parser for Recon Pipelines"
    )
    
    # Positional positional argument
    parser.add_argument('csv', nargs='?', help="Path to the HackerOne exported .csv file")
    
    # Scope Flags
    scope_group = parser.add_mutually_exclusive_group()
    scope_group.add_argument('--in-scope', dest='scope', action='store_const', const='in', help="Filter for In-Scope targets only")
    scope_group.add_argument('--out-of-scope', dest='scope', action='store_const', const='out', help="Filter for Out-of-Scope targets only")
    
    # Asset Type Flags
    parser.add_argument('-t', '--type', nargs='+', 
                    help="Filter by specific asset types like wildcard, domain, url, cidr, android, ios (space separated)")

    # Helper Flags
    parser.add_argument('--list-types', action='store_true', help="Show supported asset types and exit")
    parser.add_argument('--show-counts', action='store_true', help="Print the number of matched targets to stderr")
    parser.add_argument('--version', '--sersion', action='version', version=f"%(prog)s {VERSION}", help="Show version and exit")
    
    # Output Flag
    parser.add_argument('-o', '--output', help="Output file path (prints to terminal if omitted)")

    args = parser.parse_args()

    if args.list_types:
        list_types()
        sys.exit(0)

    if not args.csv:
        parser.error("the following arguments are required: csv")
    
    parse_scope(args.csv, args.scope, args.type, args.output, args.show_counts)
