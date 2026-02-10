#!/usr/bin/env python3
"""
HN Job Posting Comparison Script

This script compares two JSON files containing HackerNews job postings
and identifies entries that are new or have been updated.

Usage:
    python compare_jobs.py --original path/to/original.json --updated path/to/updated.json [--output path/to/output.json] [--log path/to/logfile.log]
"""

import json
import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple


def setup_logging(log_file: str) -> None:
    """Configure logging to both file and console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def load_json_file(file_path: str) -> List[Dict]:
    """
    Load and parse a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        List of job entry dictionaries

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    logging.info(f"Loading JSON file: {file_path}")

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array in {file_path}, got {type(data).__name__}")

    logging.info(f"Loaded {len(data)} entries from {file_path}")
    return data


def validate_entry(entry: Dict, file_name: str, index: int) -> Tuple[bool, str]:
    """
    Validate that an entry has required fields.

    Args:
        entry: Job entry dictionary
        file_name: Name of the file being validated
        index: Index of the entry in the array

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(entry, dict):
        return False, f"Entry at index {index} in {file_name} is not a dictionary"

    if 'id' not in entry:
        return False, f"Entry at index {index} in {file_name} is missing 'id' field"

    if 'text' not in entry:
        return False, f"Entry at index {index}[id: {entry['id']}] in {file_name} is missing 'text' field"

    return True, ""


def build_lookup_dict(entries: List[Dict], file_name: str) -> Dict[int, Dict]:
    """
    Build a lookup dictionary from entries using 'id' as key.

    Args:
        entries: List of job entry dictionaries
        file_name: Name of the file for logging purposes

    Returns:
        Dictionary mapping id to entry
    """
    lookup = {}
    invalid_count = 0
    duplicate_count = 0
    deleted_count = 0

    for idx, entry in enumerate(entries):
        # Skip entries marked as deleted before validation (deleted entries may not have required fields like 'text')
        if isinstance(entry, dict) and entry.get('deleted', False) == True:
            deleted_count += 1
            continue

        is_valid, error_msg = validate_entry(entry, file_name, idx)

        if not is_valid:
            logging.warning(error_msg)
            invalid_count += 1
            continue

        entry_id = entry['id']

        if entry_id in lookup:
            logging.warning(f"Duplicate id {entry_id} found in {file_name} at index {idx}")
            duplicate_count += 1
            continue

        lookup[entry_id] = entry

    if invalid_count > 0:
        logging.warning(f"Skipped {invalid_count} invalid entries in {file_name}")

    if duplicate_count > 0:
        logging.warning(f"Skipped {duplicate_count} duplicate entries in {file_name}")

    if deleted_count > 0:
        logging.info(f"Skipped {deleted_count} deleted entries in {file_name}")

    return lookup


def compare_entries(original_entries: List[Dict], updated_entries: List[Dict]) -> Dict:
    """
    Compare two sets of job entries and identify new and updated entries.

    Args:
        original_entries: List of entries from the original file
        updated_entries: List of entries from the updated file

    Returns:
        Dictionary containing comparison results
    """
    logging.info("Building lookup dictionary from original entries...")
    original_lookup = build_lookup_dict(original_entries, "original")

    logging.info("Building lookup dictionary from updated entries...")
    updated_lookup = build_lookup_dict(updated_entries, "updated")

    new_entries = []
    updated_entries_list = []
    unchanged_count = 0

    logging.info("Comparing entries...")

    for entry_id, updated_entry in updated_lookup.items():
        if entry_id not in original_lookup:
            # New entry
            new_entries.append(updated_entry)
        else:
            # Check if text has changed
            original_text = original_lookup[entry_id].get('text', '')
            updated_text = updated_entry.get('text', '')

            if original_text != updated_text:
                # Text has been updated
                updated_entries_list.append(updated_entry)
            else:
                # No change
                unchanged_count += 1

    logging.info(f"Comparison complete:")
    logging.info(f"  - New entries: {len(new_entries)}")
    logging.info(f"  - Updated entries: {len(updated_entries_list)}")
    logging.info(f"  - Unchanged entries: {unchanged_count}")

    return {
        'new_entries': new_entries,
        'updated_entries': updated_entries_list,
        'summary': {
            'total_original': len(original_lookup),
            'total_updated': len(updated_lookup),
            'new_entries': len(new_entries),
            'updated_entries': len(updated_entries_list),
            'unchanged_entries': unchanged_count
        }
    }


def save_results(results: Dict, output_file: str, original_file: str, updated_file: str) -> None:
    """
    Save comparison results to a JSON file.

    Args:
        results: Dictionary containing comparison results
        output_file: Path to the output file
        original_file: Path to the original input file
        updated_file: Path to the updated input file
    """
    output_data = {
        'comparison_date': datetime.now(timezone.utc).isoformat(),
        'original_file': original_file,
        'updated_file': updated_file,
        'summary': results['summary'],
        'new_entries': results['new_entries'],
        'updated_entries': results['updated_entries']
    }

    logging.info(f"Saving results to {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    logging.info(f"Results saved successfully to {output_file}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Compare two JSON files containing HackerNews job postings and identify new or updated entries.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--original',
        required=True,
        help='Path to the original JSON file'
    )

    parser.add_argument(
        '--updated',
        required=True,
        help='Path to the updated JSON file'
    )

    parser.add_argument(
        '--output',
        default='updated_entries.json',
        help='Path to the output JSON file (default: updated_entries.json)'
    )

    parser.add_argument(
        '--log',
        default='comparison.log',
        help='Path to the log file (default: comparison.log)'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log)

    logging.info("="*60)
    logging.info("HN Job Posting Comparison Script")
    logging.info("="*60)

    try:
        # Load both JSON files
        original_entries = load_json_file(args.original)
        updated_entries = load_json_file(args.updated)

        # Compare entries
        results = compare_entries(original_entries, updated_entries)

        # Save results
        save_results(results, args.output, args.original, args.updated)

        # Print summary to console
        print("\n" + "="*60)
        print("COMPARISON SUMMARY")
        print("="*60)
        print(f"Original entries: {results['summary']['total_original']}")
        print(f"Updated entries:  {results['summary']['total_updated']}")
        print(f"New entries:      {results['summary']['new_entries']}")
        print(f"Updated entries:  {results['summary']['updated_entries']}")
        print(f"Unchanged:        {results['summary']['unchanged_entries']}")
        print("="*60)
        print(f"\nResults saved to: {args.output}")
        print(f"Log saved to:     {args.log}")

        logging.info("Comparison completed successfully")
        return 0

    except FileNotFoundError as e:
        logging.error(f"File error: {e}")
        return 1

    except json.JSONDecodeError as e:
        logging.error(f"JSON parsing error: {e}")
        return 1

    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
