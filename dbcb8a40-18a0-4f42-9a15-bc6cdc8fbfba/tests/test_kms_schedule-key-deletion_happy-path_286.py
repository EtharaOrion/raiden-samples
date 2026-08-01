def test_schedule_key_deletion_sets_pending_deletion(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "to-be-deleted"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "schedule-key-deletion",
        "--key-id", key_id,
        "--pending-window-in-days", "7",
    )
    assert result.returncode == 0

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyState"] == "PendingDeletion"