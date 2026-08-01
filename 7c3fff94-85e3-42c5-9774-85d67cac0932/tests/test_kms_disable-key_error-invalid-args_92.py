def test_disable_key_missing_required_key_id(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "disable-key missing argument test"})
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert before["Enabled"] is True
    assert before["KeyState"] == "Enabled"

    result = cli("kms", "disable-key")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()

    after = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert after["KeyId"] == key_id
    assert after["Enabled"] is True
    assert after["KeyState"] == "Enabled"