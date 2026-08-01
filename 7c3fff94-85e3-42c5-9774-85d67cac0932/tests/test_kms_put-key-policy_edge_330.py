def test_put_key_policy_updates_default_policy(cli, kms):
    import json

    created = kms.rpc("CreateKey", {"Description": "put-key-policy prerequisite"})
    metadata = created["KeyMetadata"]
    key_id = metadata["KeyId"]

    original = kms.rpc(
        "GetKeyPolicy",
        {"KeyId": key_id, "PolicyName": "default"},
    )
    original_policy = json.loads(original["Policy"])

    arn_parts = metadata["Arn"].split(":")
    root_principal = f"arn:{arn_parts[1]}:iam::{arn_parts[4]}:root"
    expected_policy = {
        "Version": "2012-10-17",
        "Id": "put-key-policy-edge",
        "Statement": [
            {
                "Sid": "AllowAccountAdministration",
                "Effect": "Allow",
                "Principal": {"AWS": root_principal},
                "Action": "kms:*",
                "Resource": "*",
            }
        ],
    }
    assert original_policy != expected_policy

    result = cli(
        "kms",
        "put-key-policy",
        "--key-id",
        key_id,
        "--policy",
        json.dumps(expected_policy),
        "--policy-name",
        "default",
    )
    assert result.returncode == 0

    updated = kms.rpc(
        "GetKeyPolicy",
        {"KeyId": key_id, "PolicyName": "default"},
    )
    assert json.loads(updated["Policy"]) == expected_policy