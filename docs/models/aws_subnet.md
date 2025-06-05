# AWSSubnet

A subnet is a range of IP addresses in your VPC. You launch AWS resources, such as Amazon EC2 instances, into your subnets. A subnet must reside in a single Availability Zone and is associated with a route table.

For more information, see [Subnets for your VPC](https://docs.aws.amazon.com/vpc/latest/userguide/configure-subnets.html) in the Amazon VPC User Guide.

## Attributes

Represents an AWS Subnet within NetBox.

*   **`name`**: A user-defined descriptive name for the Subnet. (**Required**)
*   **`subnet_id`**: The unique AWS Subnet ID (e.g., `subnet-0123456789abcdef0`) (optional).
*   **`aws_vpc`**: The [`AWSVPC`](./aws_vpc.md) this Subnet belongs to. (**Required**)
*   **`cidr_block`**: The IPv4 CIDR block for the Subnet, linked to an `ipam.Prefix` (optional).
*   **`availability_zone`**: The AWS Availability Zone of the Subnet (e.g., `us-east-1a`) (optional).
*   **`availability_zone_id`**: The ID of the Availability Zone (e.g., `use1-az1`) (optional).
*   **`state`**: The current state of the Subnet (e.g., `planned`, `available`, `pending`). (**Required**, defaults to `available`)
*   **`map_public_ip_on_launch`**: Whether instances in this subnet get a public IP on launch by default. (**Required**, defaults to `False`)
