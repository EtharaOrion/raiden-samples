def test_create_key_happy_path(cli, kms):
    import json

    before = kms.rpc("ListKeys", {})
    existing_key_ids = {key["KeyId"] for key in before["Keys"]}

    result = cli("kms", "create-key")

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    created = output["KeyMetadata"]
    key_id = created["KeyId"]

    assert key_id not in existing_key_ids

    described = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert described["KeyId"] == key_id
    assert described["Arn"] == created["Arn"]
    assert described["Enabled"] is True
    assert described["KeyState"] == "Enabled"
    assert described["KeyUsage"] == "ENCRYPT_DECRYPT"
    assert described["KeySpec"] == "SYMMETRIC_DEFAULT"