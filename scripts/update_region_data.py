#!/usr/bin/env python3
import requests
import json
import sys
from pathlib import Path

# Constants
REGIONS_URL = "https://raw.githubusercontent.com/sophos-iaas/aws-region-names/master/aws-region-names.json"

# The output path is relative to the project root, inside the plugin's directory
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "netbox_aws_resources_plugin" / "data"
OUTPUT_FILE = OUTPUT_DIR / "region_data.json"


def main():
    """Main function to fetch and save region data."""
    try:
        # Ensure the output directory exists
        print(f"Ensuring output directory exists: {OUTPUT_DIR}")
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        print(f"Fetching region data from {REGIONS_URL}...")
        response = requests.get(REGIONS_URL)
        response.raise_for_status()
        region_data = response.json()

        # Save data to file
        print(f"Saving region data to {OUTPUT_FILE}...")
        with open(OUTPUT_FILE, "w") as f:
            json.dump(region_data, f, indent=2)

        print(f"\nSuccessfully updated AWS region data. Found {len(region_data)} regions.")

    except requests.exceptions.RequestException as e:
        print(f"\nERROR: Failed to download region data: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"\nERROR: Failed to parse region data: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        import traceback

        print(f"\nERROR: An unexpected error occurred: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
