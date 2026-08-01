def test_schedule_key_deletion_rejects_unknown_flag(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"Description": "key must remain unchanged after invalid CLI arguments"},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert before["KeyState"] == "Enabled"
    assert before["Enabled"] is True

    result = cli(
        "kms",
        "schedule-key-deletion",
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
    assert after["KeyState"] == "Enabled"
    assert after["Enabled"] is True