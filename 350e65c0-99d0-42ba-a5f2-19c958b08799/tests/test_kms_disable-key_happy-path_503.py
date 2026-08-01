def test_disable_key_happy_path(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "disable-key-test"})
    key_id = created["KeyMetadata"]["KeyId"]

    assert kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]["Enabled"] is True

    result = cli("kms", "disable-key", "--key-id", key_id)
    assert result.returncode == 0

    meta = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert meta["Enabled"] is False
    assert meta["KeyState"] == "Disabled"