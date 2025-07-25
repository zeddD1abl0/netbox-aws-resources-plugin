#!/usr/bin/env python3
import requests
import json
import sys
from pathlib import Path

# Constants
# We fetch from a single region; instance specs (vCPU/RAM) are consistent globally.
# Pricing will be considered an estimate.
EC2_PRICING_URL = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/us-east-1/index.json"
RDS_PRICING_URL = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/us-east-1/index.json"

# The output path is relative to the project root, inside the plugin's directory
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "netbox_aws_resources_plugin" / "data"
OUTPUT_FILE = OUTPUT_DIR / "instance_data.json"


def fetch_and_process_data(service_name, url):
    """Fetches and processes pricing data for a given AWS service."""
    print(f"Fetching data for {service_name.upper()} from {url}...")
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    print(f"Processing data for {service_name.upper()}...")
    processed_data = {}

    products = data.get("products", {})
    terms = data.get("terms", {}).get("OnDemand", {})

    for sku, product in products.items():
        # Skip products without the necessary attributes
        if "instanceType" not in product.get("attributes", {}):
            continue

        attributes = product["attributes"]
        instance_type = attributes.get("instanceType")

        # For EC2, we only care about Linux, shared-tenancy instances
        if service_name == "ec2":
            if attributes.get("operatingSystem") != "Linux" or attributes.get("tenancy") != "Shared":
                continue

        # For RDS, we can add filters here if needed, e.g., for specific engines

        # Get specs
        vcpu = attributes.get("vcpu")
        memory = attributes.get("memory", "0 GiB").replace(" GiB", "")

        # Find the price
        price = 0.0
        if sku in terms:
            term_details = list(terms[sku].values())[0]
            price_dimensions = list(term_details.get("priceDimensions", {}).values())[0]
            price = float(price_dimensions.get("pricePerUnit", {}).get("USD", 0.0))

        if instance_type and vcpu and memory:
            try:
                processed_data[instance_type] = {
                    "vcpu": int(vcpu),
                    "ram_gb": int(float(memory)),
                    "price_usd_hourly": price,
                }
            except (ValueError, TypeError):
                # Skip if vCPU or RAM cannot be parsed as numbers
                continue

    print(f"Found {len(processed_data)} instance types for {service_name.upper()}.")
    return processed_data


def main():
    """Main function to fetch and save instance data."""
    try:
        # Ensure the output directory exists
        print(f"Ensuring output directory exists: {OUTPUT_DIR}")
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        output_data = {
            "ec2": fetch_and_process_data("ec2", EC2_PRICING_URL),
            "rds": fetch_and_process_data("rds", RDS_PRICING_URL),
        }

        # Save data to file
        print(f"Saving instance data to {OUTPUT_FILE}...")
        with open(OUTPUT_FILE, "w") as f:
            json.dump(output_data, f, indent=2)

        print("\nSuccessfully updated AWS instance data.")

    except requests.exceptions.RequestException as e:
        print(f"\nERROR: Failed to download pricing data: {e}", file=sys.stderr)
        sys.exit(1)
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"\nERROR: Failed to parse pricing data: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        import traceback

        print(f"\nERROR: An unexpected error occurred: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
