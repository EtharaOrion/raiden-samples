def test_get_key_policy_accepts_max_length_policy_name(cli, kms):
    import json

    created = kms.rpc("CreateKey", {"Description": "get-key-policy edge test"})
    key_id = created["KeyMetadata"]["KeyId"]
    policy_name = "x" * 128

    result = cli(
        "kms",
        "get-key-policy",
        "--key-id",
        key_id,
        "--policy-name",
        policy_name,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)

    observed = kms.rpc(
        "GetKeyPolicy",
        {"KeyId": key_id, "PolicyName": policy_name},
    )
    assert json.loads(output["Policy"]) == json.loads(observed["Policy"])

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["KeyState"] == "Enabled"