def test_put_key_policy_happy_path_round_trip(cli, kms):
    import json
    import uuid

    created = kms.rpc(
        "CreateKey",
        {"Description": "put-key-policy-happy-" + uuid.uuid4().hex},
    )
    metadata = created["KeyMetadata"]
    key_id = metadata["KeyId"]

    arn_parts = metadata["Arn"].split(":")
    root_principal = "arn:" + arn_parts[1] + ":iam::" + arn_parts[4] + ":root"
    policy = {
        "Version": "2012-10-17",
        "Id": "put-key-policy-happy-" + uuid.uuid4().hex,
        "Statement": [
            {
                "Sid": "AllowAccountAdmin",
                "Effect": "Allow",
                "Principal": {"AWS": root_principal},
                "Action": "kms:*",
                "Resource": "*",
            }
        ],
    }

    result = cli(
        "kms",
        "put-key-policy",
        "--key-id",
        key_id,
        "--policy-name",
        "default",
        "--policy",
        json.dumps(policy),
    )
    assert result.returncode == 0, result.stderr

    stored = kms.rpc(
        "GetKeyPolicy",
        {"KeyId": key_id, "PolicyName": "default"},
    )
    assert json.loads(stored["Policy"]) == policy
