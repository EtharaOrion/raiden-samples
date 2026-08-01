def test_put_key_policy_rejects_unknown_flag_without_mutation(cli, kms):
    import json

    created = kms.rpc("CreateKey", {"Description": "invalid-args policy test"})
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc(
        "GetKeyPolicy",
        {"KeyId": key_id, "PolicyName": "default"},
    )["Policy"]

    replacement_policy = json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowKMSAccess",
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "kms:*",
                    "Resource": "*",
                }
            ],
        }
    )

    result = cli(
        "kms",
        "put-key-policy",
        "--key-id",
        key_id,
        "--policy",
        replacement_policy,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = kms.rpc(
        "GetKeyPolicy",
        {"KeyId": key_id, "PolicyName": "default"},
    )["Policy"]
    assert json.loads(after) == json.loads(before)