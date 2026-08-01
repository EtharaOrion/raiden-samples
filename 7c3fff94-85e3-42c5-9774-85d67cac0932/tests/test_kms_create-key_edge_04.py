def test_create_key_encrypt_decrypt_usage(cli, kms):
    import json

    before = kms.rpc("ListKeys", {})
    existing_key_ids = {entry["KeyId"] for entry in before["Keys"]}

    result = cli("kms", "create-key", "--key-usage", "ENCRYPT_DECRYPT")

    assert result.returncode == 0
    output = json.loads(result.stdout)
    key_id = output["KeyMetadata"]["KeyId"]
    assert key_id not in existing_key_ids

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["KeyUsage"] == "ENCRYPT_DECRYPT"
    assert metadata["Enabled"] is True
    assert metadata["KeyState"] == "Enabled"