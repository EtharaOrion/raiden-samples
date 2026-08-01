def test_schedule_key_deletion_rejects_empty_key_id(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"Description": "key must remain active after invalid deletion request"},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert before["KeyState"] == "Enabled"
    assert before["Enabled"] is True

    result = cli("kms", "schedule-key-deletion", "--key-id", "")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Parameter validation failed" in result.stderr

    after = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert after["KeyId"] == key_id
    assert after["KeyState"] == "Enabled"
    assert after["Enabled"] is True