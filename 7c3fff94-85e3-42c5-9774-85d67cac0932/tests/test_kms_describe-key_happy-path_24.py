def test_describe_key_existing_key(cli, kms):
    import json

    created = kms.rpc(
        "CreateKey",
        {"Description": "describe-key happy path"},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "describe-key", "--key-id", key_id)

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["KeyMetadata"]["KeyId"] == key_id
    assert output["KeyMetadata"]["Description"] == "describe-key happy path"

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    metadata = described["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["Description"] == "describe-key happy path"
    assert metadata["Enabled"] is True
    assert metadata["KeyState"] == "Enabled"