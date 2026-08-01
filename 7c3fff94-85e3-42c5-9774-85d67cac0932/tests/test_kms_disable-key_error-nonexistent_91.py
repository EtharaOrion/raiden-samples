def test_disable_key_nonexistent_returns_not_found(cli, kms):
    existing = kms.rpc("CreateKey", {"Description": "disable-key nonexistent control"})
    existing_key_id = existing["KeyMetadata"]["KeyId"]
    missing_key_id = "00000000-0000-0000-0000-000000000000"
    assert existing_key_id != missing_key_id
    assert existing["KeyMetadata"]["Enabled"] is True

    result = cli("kms", "disable-key", "--key-id", missing_key_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr

    metadata = kms.rpc("DescribeKey", {"KeyId": existing_key_id})["KeyMetadata"]
    assert metadata["KeyId"] == existing_key_id
    assert metadata["Enabled"] is True
    assert metadata["KeyState"] == "Enabled"