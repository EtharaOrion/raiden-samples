def test_enable_key_restores_enabled_state(cli, kms):
    create = kms.rpc("CreateKey", {"Description": "enable-key test"})
    key_id = create["KeyMetadata"]["KeyId"]

    kms.rpc("DisableKey", {"KeyId": key_id})
    disabled = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert disabled["KeyMetadata"]["Enabled"] is False

    result = cli("kms", "enable-key", "--key-id", key_id)
    assert result.returncode == 0

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["Enabled"] is True
    assert described["KeyMetadata"]["KeyState"] == "Enabled"