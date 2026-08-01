def test_disable_key_happy_path(cli, kms):
    create = kms.rpc("CreateKey", {"Description": "disable-key test"})
    key_id = create["KeyMetadata"]["KeyId"]

    assert kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]["Enabled"] is True

    result = cli("kms", "disable-key", "--key-id", key_id)
    assert result.returncode == 0

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["Enabled"] is False