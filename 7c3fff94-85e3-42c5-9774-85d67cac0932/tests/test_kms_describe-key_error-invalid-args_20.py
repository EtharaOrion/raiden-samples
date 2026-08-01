def test_describe_key_rejects_empty_key_id(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "empty-key-id validation sentinel"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "describe-key", "--key-id", "")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Invalid length" in result.stderr

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["Description"] == "empty-key-id validation sentinel"
    assert metadata["Enabled"] is True
    assert metadata["KeyState"] == "Enabled"