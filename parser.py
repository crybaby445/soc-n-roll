#!/usr/bin/env python3
import argparse
import csv
import json
import sys
import xml.etree.ElementTree as ET

NS = "http://schemas.microsoft.com/win/2004/08/events/event"

FIELDS = {
    "UtcTime", "Image", "CommandLine", "User",
    "IntegrityLevel", "ParentImage", "ParentCommandLine", "Hashes",
}


def parse_event(root):
    system = root.find(f"{{{NS}}}System")
    event_data = root.find(f"{{{NS}}}EventData")

    if system is None or event_data is None:
        return None

    event_id_el = system.find(f"{{{NS}}}EventID")
    computer_el = system.find(f"{{{NS}}}Computer")

    if event_id_el is None or event_id_el.text != "1":
        return None

    record = {
        "EventID": int(event_id_el.text),
        "Computer": computer_el.text if computer_el is not None else None,
    }

    for data in event_data.findall(f"{{{NS}}}Data"):
        name = data.get("Name")
        if name in FIELDS:
            record[name] = data.text

    return record


def matches_filters(record, args):
    if args.image and args.image.lower() not in (record.get("Image") or "").lower():
        return False
    if args.user and args.user.lower() != (record.get("User") or "").lower():
        return False
    if args.integrity and args.integrity.lower() != (record.get("IntegrityLevel") or "").lower():
        return False
    if args.cmdline and args.cmdline.lower() not in (record.get("CommandLine") or "").lower():
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Parse Sysmon Event ID 1 XML to JSON")
    parser.add_argument("file", help="Path to Sysmon XML file")
    parser.add_argument("--image", help="Filter: Image path contains value (case-insensitive)")
    parser.add_argument("--user", help="Filter: User exact match (case-insensitive)")
    parser.add_argument("--integrity", choices=["high", "medium", "low", "system"],
                        type=str.lower, help="Filter: IntegrityLevel exact match")
    parser.add_argument("--cmdline", help="Filter: CommandLine contains value (case-insensitive)")
    parser.add_argument("--format", choices=["json", "jsonl", "csv"], default="json",
                        help="Output format (default: json)")
    # This stats feature is for quick triage to understand what's in a file before deep analysis
    parser.add_argument("--stats", action="store_true",
                        help="Output statistics instead of events")
    args = parser.parse_args()

    try:
        tree = ET.parse(args.file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    except ET.ParseError as e:
        print(f"Error: invalid XML: {e}", file=sys.stderr)
        sys.exit(1)

    root = tree.getroot()

    # Support both a single <Event> and a wrapper element containing multiple <Event> elements
    if root.tag == f"{{{NS}}}Event":
        events = [root]
    else:
        events = root.findall(f"{{{NS}}}Event")

    results = [r for e in events if (r := parse_event(e)) is not None]

    if not results:
        print("Error: no Event ID 1 records found", file=sys.stderr)
        sys.exit(1)

    results = [r for r in results if matches_filters(r, args)]

    if not results:
        print("Error: no events matched filters", file=sys.stderr)
        sys.exit(1)

    if args.stats:
        by_integrity: dict = {}
        for r in results:
            level = r.get("IntegrityLevel") or "Unknown"
            by_integrity[level] = by_integrity.get(level, 0) + 1
        stats = {
            "total_events": len(results),
            "unique_processes": len({r.get("Image") for r in results}),
            "unique_users": len({r.get("User") for r in results}),
            "events_by_integrity_level": by_integrity,
        }
        print(json.dumps(stats, indent=2))
        return

    if args.format == "jsonl":
        for r in results:
            print(json.dumps(r))
    elif args.format == "csv":
        # Collect all keys in a stable, consistent order across records
        fieldnames = list(dict.fromkeys(k for r in results for k in r))
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
    else:
        output = results[0] if len(results) == 1 else results
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
