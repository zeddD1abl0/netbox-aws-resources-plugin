# AWSAccount

An AWS account is a container for your AWS resources. It provides a way to manage and isolate your resources, and also provides mechanisms for security, access, and billing.

For more information, see the [AWS Account Management Reference Guide](https://docs.aws.amazon.com/accounts/latest/reference/accounts-welcome.html).

## Attributes

Represents an individual AWS Account within NetBox.

*   **`account_id`**: The unique 12-digit AWS Account ID (optional).
*   **`name`**: A user-defined descriptive name for the account. (**Required**)
*   **`tenant`**: The NetBox `Tenant` this AWS Account is associated with (optional).
*   **`parent_account`**: A foreign key to another [`AWSAccount`](./aws_account.md) instance, representing the parent in a hierarchy. If null, the account is considered a "Root" account (optional).
