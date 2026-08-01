def test_disable_key_happy_path(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "to-disable"})
    key_id = created["KeyMetadata"]["KeyId"]

    # Precondition: key is enabled
    pre = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert pre["KeyMetadata"]["Enabled"] is True

    result = cli("kms", "disable-key", "--key-id", key_id)
    assert result.returncode == 0

    post = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert post["KeyMetadata"]["Enabled"] is False