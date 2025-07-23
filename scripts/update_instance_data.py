#!/usr/bin/env python3
import boto3
import json
import os
from pathlib import Path

# Constants
PRICING_REGION = 'us-east-1'
EC2_SERVICE_CODE = 'AmazonEC2'
RDS_SERVICE_CODE = 'AmazonRDS'

# This is a mapping of region names used by the pricing API.
# A more comprehensive list can be found at https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html
LOCATION_MAP = {
    'us-east-1': 'US East (N. Virginia)',
    'us-east-2': 'US East (Ohio)',
    'us-west-1': 'US West (N. California)',
    'us-west-2': 'US West (Oregon)',
    'ca-central-1': 'Canada (Central)',
    'eu-west-1': 'EU (Ireland)',
    'eu-central-1': 'EU (Frankfurt)',
    'eu-west-2': 'EU (London)',
    'ap-northeast-1': 'Asia Pacific (Tokyo)',
    'ap-northeast-2': 'Asia Pacific (Seoul)',
    'ap-southeast-1': 'Asia Pacific (Singapore)',
    'ap-southeast-2': 'Asia Pacific (Sydney)',
    'ap-south-1': 'Asia Pacific (Mumbai)',
    'sa-east-1': 'South America (Sao Paulo)',
}


def get_pricing_client():
    """Initializes and returns a boto3 pricing client."""
    return boto3.client('pricing', region_name=PRICING_REGION)


def get_ec2_price(pricing_client, instance_type, region):
    """Fetches the on-demand price for a given EC2 instance type and region."""
    location = LOCATION_MAP.get(region)
    if not location:
        return None

    try:
        response = pricing_client.get_products(
            ServiceCode=EC2_SERVICE_CODE,
            Filters=[
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': location},
                {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
                {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
                {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
                {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},
            ]
        )
        for price_item in response.get('PriceList', []):
            price_data = json.loads(price_item)
            for term, details in price_data.get('terms', {}).get('OnDemand', {}).items():
                for price_dimension in details.get('priceDimensions', {}).values():
                    if 'per Hour' in price_dimension.get('description', ''):
                        return float(price_dimension['pricePerUnit']['USD'])
    except Exception as e:
        print(f"Error fetching EC2 price for {instance_type} in {region}: {e}")
    return None


def get_rds_price(pricing_client, instance_class, engine, region):
    """Fetches the on-demand price for a given RDS instance class, engine, and region."""
    location = LOCATION_MAP.get(region)
    if not location:
        return None

    try:
        response = pricing_client.get_products(
            ServiceCode=RDS_SERVICE_CODE,
            Filters=[
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': location},
                {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_class},
                {'Type': 'TERM_MATCH', 'Field': 'databaseEngine', 'Value': engine},
                {'Type': 'TERM_MATCH', 'Field': 'deploymentOption', 'Value': 'Single-AZ'},
            ]
        )
        for price_item in response.get('PriceList', []):
            price_data = json.loads(price_item)
            for term, details in price_data.get('terms', {}).get('OnDemand', {}).items():
                for price_dimension in details.get('priceDimensions', {}).values():
                    if 'per Hour' in price_dimension.get('description', ''):
                        return float(price_dimension['pricePerUnit']['USD'])
    except Exception as e:
        print(f"Error fetching RDS price for {instance_class} in {region}: {e}")
    return None


def main():
    """Main function to fetch and save instance data."""
    output_data = {'ec2': {}, 'rds': {}}
    pricing_client = get_pricing_client()

    # --- Fetch EC2 Data ---
    print("Fetching EC2 instance types...")
    ec2_client = boto3.client('ec2', region_name=PRICING_REGION)
    paginator = ec2_client.get_paginator('describe_instance_types')
    for page in paginator.paginate():
        for itype in page['InstanceTypes']:
            instance_type = itype['InstanceType']
            print(f"  Processing EC2 type: {instance_type}")
            price = get_ec2_price(pricing_client, instance_type, PRICING_REGION)
            output_data['ec2'][instance_type] = {
                'vcpu': itype.get('VCpuInfo', {}).get('DefaultVCpus'),
                'memory_mb': itype.get('MemoryInfo', {}).get('SizeInMiB'),
                'price_usd_per_hour': price,
            }

    # --- Fetch RDS Data ---
    print("\nFetching RDS instance types...")
    rds_client = boto3.client('rds', region_name=PRICING_REGION)
    # We check a few common engines to get a representative list of instance classes
    for engine in ['mysql', 'postgres']:
        print(f"  Checking RDS engine: {engine}")
        paginator = rds_client.get_paginator('describe_orderable_db_instance_options')
        for page in paginator.paginate(Engine=engine):
            for option in page['OrderableDBInstanceOptions']:
                instance_class = option['DBInstanceClass']
                if instance_class not in output_data['rds']:
                    print(f"    Processing RDS type: {instance_class}")
                    price = get_rds_price(pricing_client, instance_class, 'MySQL', PRICING_REGION) # Pricing API uses 'MySQL', 'PostgreSQL'
                    output_data['rds'][instance_class] = {
                        'vcpu': option.get('Vcpu'),
                        'memory_gb': option.get('MemoryGiB'),
                        'price_usd_per_hour': price,
                    }

    # --- Save Data to File ---
    script_dir = Path(__file__).parent
    output_path = script_dir.parent / 'netbox_aws_resources_plugin' / 'data' / 'instance_data.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nWriting data to {output_path}")
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2, sort_keys=True)

    print("\nDone.")

if __name__ == '__main__':
    main()
