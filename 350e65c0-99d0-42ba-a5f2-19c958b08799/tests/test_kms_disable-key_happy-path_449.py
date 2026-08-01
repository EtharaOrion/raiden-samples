def test_disable_key_happy_path(cli, kms):
    create = kms.rpc("CreateKey", {"Description": "disable-key-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Ensure it starts enabled
    kms.rpc("EnableKey", {"KeyId": key_id})
    assert kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]["Enabled"] is True

    result = cli("kms", "disable-key", "--key-id", key_id)
    assert result.returncode == 0

    meta = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert meta["Enabled"] is False