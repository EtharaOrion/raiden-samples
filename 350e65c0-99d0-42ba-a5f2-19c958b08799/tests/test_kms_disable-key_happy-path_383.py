def test_disable_key_happy_path(cli, kms, tmp_path):
    create = kms.rpc("CreateKey", {"Description": "to-disable"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Ensure it starts enabled
    before = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert before["KeyMetadata"]["Enabled"] is True

    result = cli("kms", "disable-key", "--key-id", key_id)
    assert result.returncode == 0

    after = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert after["KeyMetadata"]["Enabled"] is False