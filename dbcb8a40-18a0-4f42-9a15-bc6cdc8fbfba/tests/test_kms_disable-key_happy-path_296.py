def test_disable_key_happy_path(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "disable-key happy path"})
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert before["KeyMetadata"]["Enabled"] is True

    result = cli("kms", "disable-key", "--key-id", key_id)
    assert result.returncode == 0

    after = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert after["KeyMetadata"]["Enabled"] is False
    assert after["KeyMetadata"]["KeyState"] == "Disabled"