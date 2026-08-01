def test_get_key_policy_non_default_policy_name(cli, kms):
    import json

    created = kms.rpc("CreateKey", {"Description": "get-key-policy edge test"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms",
        "get-key-policy",
        "--key-id",
        key_id,
        "--policy-name",
        "x",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert isinstance(output["Policy"], str)

    stored = kms.rpc(
        "GetKeyPolicy",
        {"KeyId": key_id, "PolicyName": "default"},
    )
    assert json.loads(output["Policy"]) == json.loads(stored["Policy"])

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id