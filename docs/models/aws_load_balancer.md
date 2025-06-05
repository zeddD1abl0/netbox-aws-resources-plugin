# AWSLoadBalancer

Elastic Load Balancing automatically distributes incoming application traffic across multiple targets, such as Amazon EC2 instances, containers, IP addresses, and Lambda functions. It can handle the varying load of your application traffic in a single Availability Zone or across multiple Availability Zones.

This plugin supports Application Load Balancers (ALB) and Network Load Balancers (NLB).

For more information, see the [Elastic Load Balancing User Guide](https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/what-is-load-balancing.html).

## Attributes

Represents an AWS Elastic Load Balancer (Application or Network) within NetBox.

*   **`name`**: The name of the Load Balancer. (**Required**)
*   **`arn`**: The Amazon Resource Name (ARN) of the Load Balancer (optional, unique).
*   **`aws_account`**: The [`AWSAccount`](./aws_account.md) this Load Balancer belongs to. (**Required**)
*   **`vpc`**: The [`AWSVPC`](./aws_vpc.md) this Load Balancer is deployed in. (**Required**)
*   **`subnets`**: Many-to-many relationship with [`AWSSubnet`](./aws_subnet.md) instances associated with the Load Balancer (optional).
*   **`type`**: The type of Load Balancer (e.g., `application`, `network`). (**Required**)
*   **`scheme`**: The scheme of the Load Balancer (e.g., `internal`, `internet-facing`). (**Required**)
*   **`dns_name`**: The DNS name of the Load Balancer (optional).
*   **`state`**: The state of the Load Balancer (e.g., `planned`, `active`, `provisioning`, `failed`). (**Required**)
*   **`region`**: The AWS region where the Load Balancer is located. (**Required** - automatically set from the selected `vpc`).
