package main

import (
	"bufio"
	"encoding/csv"
	"flag"
	"fmt"
	"io"
	"os"
	"strings"
)

const version = "1.0.0"

type multiStringFlag []string

func (m *multiStringFlag) String() string {
	return strings.Join(*m, ",")
}

func (m *multiStringFlag) Set(value string) error {
	*m = append(*m, value)
	return nil
}

func normalizeHeader(s string) string {
	return strings.TrimSpace(strings.ToLower(s))
}

func parseBoolString(value string) bool {
	v := strings.TrimSpace(strings.ToLower(value))
	switch v {
	case "true", "1", "yes", "y", "t":
		return true
	case "false", "0", "no", "n", "f", "":
		return false
	default:
		return false
	}
}

func supportedTypeMap() map[string][]string {
	return map[string][]string{
		"url":      {"URL"},
		"domain":   {"DOMAIN"},
		"wildcard": {"WILDCARD"},
		"cidr":     {"CIDR", "IP_ADDRESS", "IP"},
		"android":  {"GOOGLE_PLAY_APP_ID", "ANDROID_APP_APK"},
		"ios":      {"APPLE_APP_STORE_ID", "IOS_APP_IPA"},
	}
}

func listTypes() {
	fmt.Println("Supported types:")
	fmt.Println("  wildcard  Wildcard subdomain entries")
	fmt.Println("  domain    Apex/root domains")
	fmt.Println("  url       Specific endpoints, paths, or APIs")
	fmt.Println("  cidr      Network ranges and standalone IPs")
	fmt.Println("  android   Google Play IDs and APK targets")
	fmt.Println("  ios       App Store IDs and IPA targets")
}

func parseCSV(path string) ([]map[string]string, []string, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, nil, err
	}
	defer f.Close()

	r := csv.NewReader(f)
	header, err := r.Read()
	if err != nil {
		return nil, nil, err
	}

	normalizedHeader := make([]string, len(header))
	for i, h := range header {
		normalizedHeader[i] = normalizeHeader(h)
	}

	records := make([]map[string]string, 0)
	for {
		row, err := r.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			return nil, nil, err
		}

		if len(row) < len(normalizedHeader) {
			padded := make([]string, len(normalizedHeader))
			copy(padded, row)
			row = padded
		}

		record := make(map[string]string, len(normalizedHeader))
		for i, key := range normalizedHeader {
			record[key] = row[i]
		}
		records = append(records, record)
	}

	return records, normalizedHeader, nil
}

func uniqueInOrder(values []string) []string {
	seen := make(map[string]bool)
	result := make([]string, 0)
	for _, v := range values {
		if v == "" {
			continue
		}
		if !seen[v] {
			seen[v] = true
			result = append(result, v)
		}
	}
	return result
}

func main() {
	var inScope bool
	var outScope bool
	var showCounts bool
	var listTypesFlag bool
	var showVersion bool
	var outputFile string

	var assetTypes multiStringFlag

	flag.BoolVar(&inScope, "in-scope", false, "Filter for In-Scope targets only")
	flag.BoolVar(&outScope, "out-of-scope", false, "Filter for Out-of-Scope targets only")
	flag.Var(&assetTypes, "type", "Filter by specific asset types like wildcard, domain, url, cidr, android, ios")
	flag.Var(&assetTypes, "t", "Filter by specific asset types like wildcard, domain, url, cidr, android, ios")

	flag.BoolVar(&listTypesFlag, "list-types", false, "Show supported asset types and exit")
	flag.BoolVar(&showCounts, "show-counts", false, "Print the number of matched targets to stderr")
	flag.BoolVar(&showVersion, "version", false, "Show version and exit")
	flag.StringVar(&outputFile, "output", "", "Output file path (prints to terminal if omitted)")
	flag.StringVar(&outputFile, "o", "", "Output file path (prints to terminal if omitted)")

	flag.Usage = func() {
		fmt.Fprintf(flag.CommandLine.Output(), "Usage: h1scope [options] <csv>\n\n")
		flag.PrintDefaults()
	}

	flag.Parse()

	if showVersion {
		fmt.Printf("h1scope %s\n", version)
		os.Exit(0)
	}

	if listTypesFlag {
		listTypes()
		os.Exit(0)
	}

	args := flag.Args()
	if len(args) == 0 {
		fmt.Fprintln(os.Stderr, "the following arguments are required: csv")
		flag.Usage()
		os.Exit(2)
	}

	csvPath := args[0]

	if inScope && outScope {
		fmt.Fprintln(os.Stderr, "only one of --in-scope or --out-of-scope can be used")
		os.Exit(2)
	}

	records, headers, err := parseCSV(csvPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "[-] Error reading CSV file: %v\n", err)
		os.Exit(1)
	}

	required := []string{"identifier", "asset_type", "eligible_for_submission"}
	for _, col := range required {
		found := false
		for _, h := range headers {
			if h == col {
				found = true
				break
			}
		}
		if !found {
			fmt.Fprintf(os.Stderr, "[-] Error: CSV missing one of the required columns: %v\n", required)
			fmt.Fprintf(os.Stderr, "Found columns: %v\n", headers)
			os.Exit(1)
		}
	}

	filtered := make([]map[string]string, 0)

	for _, row := range records {
		eligible := parseBoolString(row["eligible_for_submission"])
		instruction := strings.TrimSpace(row["instruction"])

		switch {
		case inScope:
			if eligible && !strings.Contains(strings.ToLower(instruction), "out of scope") {
				filtered = append(filtered, row)
			}
		case outScope:
			if !eligible || strings.Contains(strings.ToLower(instruction), "out of scope") {
				filtered = append(filtered, row)
			}
		default:
			filtered = append(filtered, row)
		}
	}

	if len(assetTypes) > 0 {
		targetTypes := make(map[string]bool)
		typeMap := supportedTypeMap()

		for _, t := range assetTypes {
			tLower := strings.TrimSpace(strings.ToLower(t))
			if values, ok := typeMap[tLower]; ok {
				for _, v := range values {
					targetTypes[strings.ToUpper(v)] = true
				}
			} else {
				targetTypes[strings.ToUpper(strings.TrimSpace(t))] = true
			}
		}

		keep := make([]map[string]string, 0)
		for _, row := range filtered {
			raw := strings.TrimSpace(row["asset_type"])
			assetValue := strings.ToUpper(raw)
			if targetTypes[assetValue] {
				keep = append(keep, row)
			}
		}
		filtered = keep
	}

	uniqueIdentifiers := make([]string, 0)
	seen := make(map[string]bool)

	for _, row := range filtered {
		identifier := strings.TrimSpace(row["identifier"])
		if identifier == "" {
			continue
		}
		if !seen[identifier] {
			seen[identifier] = true
			uniqueIdentifiers = append(uniqueIdentifiers, identifier)
		}
	}

	// Write output
	if outputFile != "" {
		f, err := os.Create(outputFile)
		if err != nil {
			fmt.Fprintf(os.Stderr, "[-] Error writing output file: %v\n", err)
			os.Exit(1)
		}
		defer f.Close()

		w := bufio.NewWriter(f)
		for _, item := range uniqueIdentifiers {
			_, err := w.WriteString(item + "\n")
			if err != nil {
				fmt.Fprintf(os.Stderr, "[-] Error writing output: %v\n", err)
				os.Exit(1)
			}
		}
		w.Flush()

		fmt.Printf("[+] Successfully wrote %d targets to %s\n", len(uniqueIdentifiers), outputFile)
	} else {
		for _, item := range uniqueIdentifiers {
			fmt.Println(item)
		}
	}

	if showCounts {
		fmt.Fprintf(os.Stderr, "[+] Matched %d targets\n", len(uniqueIdentifiers))
	}
}
