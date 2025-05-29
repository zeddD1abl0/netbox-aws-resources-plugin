# AWSVPC

An Amazon Virtual Private Cloud (VPC) is a virtual network dedicated to your AWS account. It is logically isolated from other virtual networks in the AWS Cloud. You can launch your AWS resources, such as Amazon EC2 instances, into your VPC.

For more information, see the [Amazon VPC User Guide](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html).

## Attributes

Represents an AWS Virtual Private Cloud within NetBox.

*   **`name`**: A user-defined descriptive name for the VPC. (**Required**)
*   **`vpc_id`**: The unique AWS VPC ID (e.g., `vpc-0123456789abcdef0`) (optional).
*   **`aws_account`**: The [`AWSAccount`](./aws_account.md) this VPC belongs to. (**Required**)
*   **`region`**: The AWS region where the VPC is located. (**Required**)
*   **`cidr_block`**: The primary IPv4 CIDR block for the VPC, linked to an `ipam.Prefix`. (**Required**)
*   **`state`**: The current state of the VPC (e.g., `available`, `pending`). (**Required**, defaults to `available`)
*   **`is_default`**: Whether this is the default VPC for the account/region. (**Required**, defaults to `False`)
