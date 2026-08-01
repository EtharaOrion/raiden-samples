def test_disable_key_happy_path(cli, kms):
    create = kms.rpc("CreateKey", {"Description": "disable-key-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Ensure key starts enabled
    pre = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert pre["KeyMetadata"]["Enabled"] is True

    result = cli("kms", "disable-key", "--key-id", key_id)
    assert result.returncode == 0

    post = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert post["KeyMetadata"]["Enabled"] is False