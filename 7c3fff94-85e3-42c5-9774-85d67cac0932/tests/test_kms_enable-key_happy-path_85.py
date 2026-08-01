def test_enable_key_enables_disabled_key(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "key for enable-key test"})
    key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc("DisableKey", {"KeyId": key_id})
    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert before["Enabled"] is False
    assert before["KeyState"] == "Disabled"

    result = cli("kms", "enable-key", "--key-id", key_id)
    assert result.returncode == 0

    after = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert after["KeyId"] == key_id
    assert after["Enabled"] is True
    assert after["KeyState"] == "Enabled"