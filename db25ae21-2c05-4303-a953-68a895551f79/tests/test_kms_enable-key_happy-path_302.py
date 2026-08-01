def test_enable_key_reenables_disabled_key(cli, kms):
    key_id = kms.rpc("CreateKey", {})["KeyMetadata"]["KeyId"]
    kms.rpc("DisableKey", {"KeyId": key_id})
    assert kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]["Enabled"] is False

    result = cli("kms", "enable-key", "--key-id", key_id)
    assert result.returncode == 0

    md = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert md["Enabled"] is True
    assert md["KeyState"] == "Enabled"