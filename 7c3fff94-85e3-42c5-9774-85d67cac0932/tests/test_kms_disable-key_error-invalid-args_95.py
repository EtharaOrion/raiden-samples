def test_disable_key_rejects_unknown_flag_without_disabling_key(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "invalid disable-key arguments test"})
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert before["Enabled"] is True
    assert before["KeyState"] == "Enabled"

    result = cli(
        "kms",
        "disable-key",
        "--key-id",
        key_id,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert after["KeyId"] == key_id
    assert after["Enabled"] is True
    assert after["KeyState"] == "Enabled"