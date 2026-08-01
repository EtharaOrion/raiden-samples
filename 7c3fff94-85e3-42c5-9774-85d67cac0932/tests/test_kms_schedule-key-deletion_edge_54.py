def test_schedule_key_deletion_default_pending_window(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"Description": "key scheduled for deletion with the default waiting period"},
    )
    key_id = created["KeyMetadata"]["KeyId"]
    assert created["KeyMetadata"]["KeyState"] == "Enabled"

    result = cli("kms", "schedule-key-deletion", "--key-id", key_id)

    assert result.returncode == 0

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    metadata = described["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["KeyState"] == "PendingDeletion"
    assert metadata["Enabled"] is False
    assert "DeletionDate" in metadata