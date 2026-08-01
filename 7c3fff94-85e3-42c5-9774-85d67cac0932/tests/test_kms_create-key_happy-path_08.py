def test_create_key_happy_path(cli, kms):
    import json

    existing_key_ids = set()
    request = {}
    while True:
        page = kms.rpc("ListKeys", request)
        existing_key_ids.update(key["KeyId"] for key in page["Keys"])
        if not page.get("Truncated"):
            break
        request = {"Marker": page["NextMarker"]}

    result = cli("kms", "create-key")

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    created = output["KeyMetadata"]
    key_id = created["KeyId"]
    key_arn = created["Arn"]

    assert key_id not in existing_key_ids

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["Arn"] == key_arn
    assert metadata["Enabled"] is True
    assert metadata["KeyState"] == "Enabled"
    assert metadata["KeyUsage"] == "ENCRYPT_DECRYPT"
    assert metadata["KeySpec"] == "SYMMETRIC_DEFAULT"