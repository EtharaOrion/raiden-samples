def test_schedule_key_deletion_happy_path(cli, kms, tmp_path):
    create = kms.rpc("CreateKey", {"Description": "to-be-deleted"})
    key_id = create["KeyMetadata"]["KeyId"]

    assert kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]["KeyState"] == "Enabled"

    result = cli(
        "kms", "schedule-key-deletion",
        "--key-id", key_id,
        "--pending-window-in-days", "7",
    )
    assert result.returncode == 0

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyState"] == "PendingDeletion"