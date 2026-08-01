def test_schedule_key_deletion_minimum_window(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "key scheduled for deletion"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms",
        "schedule-key-deletion",
        "--key-id",
        key_id,
        "--pending-window-in-days",
        "7",
    )

    assert result.returncode == 0
    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["KeyState"] == "PendingDeletion"
    assert metadata["Enabled"] is False