def test_describe_key_happy_path(cli, kms, tmp_path):
    import json

    description = f"describe-key-{tmp_path.name}"
    created = kms.rpc("CreateKey", {"Description": description})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "describe-key", "--key-id", key_id)

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["KeyMetadata"]["KeyId"] == key_id
    assert output["KeyMetadata"]["Description"] == description

    described = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert described["KeyId"] == key_id
    assert described["Description"] == description
    assert described["Enabled"] is True
    assert described["KeyState"] == "Enabled"
    assert described["KeyUsage"] == "ENCRYPT_DECRYPT"