def test_enable_key_rejects_empty_key_id(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "empty-key-id validation sentinel"})
    key_id = created["KeyMetadata"]["KeyId"]
    kms.rpc("DisableKey", {"KeyId": key_id})

    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert before["Enabled"] is False
    assert before["KeyState"] == "Disabled"

    result = cli("kms", "enable-key", "--key-id", "")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Invalid length for parameter KeyId" in result.stderr

    after = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert after["KeyId"] == key_id
    assert after["Enabled"] is False
    assert after["KeyState"] == "Disabled"