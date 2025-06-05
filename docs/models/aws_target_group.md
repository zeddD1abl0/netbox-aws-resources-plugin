# AWSTargetGroup

A Target Group is used to route requests to one or more registered targets, such as EC2 instances, IP addresses, or other Application Load Balancers, as part of a Load Balancer. Each target group is used by one or more listeners, which are rules that check for connection requests from clients, using the protocol and port that you configure.

For more information, see the [Target Groups for your Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-target-groups.html) or [Target Groups for your Network Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/load-balancer-target-groups.html) documentation.

## Attributes

Represents an AWS Target Group within NetBox.

*   **`name`**: The name of the Target Group. (**Required**)
*   **`arn`**: The Amazon Resource Name (ARN) of the Target Group (optional, unique).
*   **`aws_account`**: The [`AWSAccount`](./aws_account.md) this Target Group belongs to. (**Required**)
*   **`region`**: The AWS region where the Target Group is located. (**Required** - automatically set from the selected `vpc`).
*   **`vpc`**: The [`AWSVPC`](./aws_vpc.md) this Target Group is associated with. (**Required**)
*   **`protocol`**: Protocol for routing traffic to targets (e.g., `HTTP`, `HTTPS`, `TCP`, `TLS`, `UDP`, `TCP_UDP`, `GENEVE`). (**Required**)
*   **`port`**: Port on which targets receive traffic. (**Required**)
*   **`target_type`**: Type of targets (e.g., `instance`, `ip`, `alb`). (**Required**)
*   **`load_balancers`**: Many-to-many relationship with [`AWSLoadBalancer`](./aws_load_balancer.md) instances associated with this Target Group (optional).
*   **`state`**: The current state of the Target Group (e.g., `active`, `creating`, `deleting`, `failed`, `initial`, `pending`, `updating`). (**Required**)

### Health Check Attributes

*   **`health_check_protocol`**: Protocol for health checks (e.g., `HTTP`, `HTTPS`, `TCP`, `TLS`, `UDP`, `TCP_UDP`, `GENEVE`) (optional).
*   **`health_check_port`**: Port for health checks (default: 'traffic-port') (optional).
*   **`health_check_path`**: Destination for HTTP/HTTPS health checks (optional).
*   **`health_check_interval_seconds`**: Approximate interval between health checks in seconds (optional).
*   **`health_check_timeout_seconds`**: Timeout for a health check response in seconds (optional).
*   **`healthy_threshold_count`**: Number of consecutive successful health checks to become healthy (optional).
*   **`unhealthy_threshold_count`**: Number of consecutive failed health checks to become unhealthy (optional).
*   **`health_check_matcher`**: For HTTP/HTTPS health checks, the codes to use when checking for a successful response from a target (e.g., `200`, `200-299`) (optional, not explicitly in model but good to note conceptually).
