def test_create_key_happy_path(cli, kms):
    import json

    existing = kms.rpc("ListKeys", {})
    existing_key_ids = {item["KeyId"] for item in existing["Keys"]}

    result = cli("kms", "create-key")

    assert result.returncode == 0
    output = json.loads(result.stdout)
    created_metadata = output["KeyMetadata"]
    key_id = created_metadata["KeyId"]

    assert key_id not in existing_key_ids

    described = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert described["KeyId"] == key_id
    assert described["Arn"] == created_metadata["Arn"]
    assert described["Enabled"] is True
    assert described["KeyState"] == "Enabled"
    assert described["KeyUsage"] == "ENCRYPT_DECRYPT"
    assert described["KeySpec"] == "SYMMETRIC_DEFAULT"