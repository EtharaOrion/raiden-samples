def test_disable_key_sets_key_state_to_disabled(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "disable-key happy-path test"})
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert before["Enabled"] is True
    assert before["KeyState"] == "Enabled"

    result = cli("kms", "disable-key", "--key-id", key_id)
    assert result.returncode == 0

    after = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert after["KeyId"] == key_id
    assert after["Enabled"] is False
    assert after["KeyState"] == "Disabled"