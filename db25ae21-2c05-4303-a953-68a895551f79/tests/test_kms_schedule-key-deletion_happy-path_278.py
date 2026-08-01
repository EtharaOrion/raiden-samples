def test_schedule_key_deletion_happy_path(cli, kms):
    create = kms.rpc("CreateKey", {"Description": "to be deleted"})
    key_id = create["KeyMetadata"]["KeyId"]

    before = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert before["KeyMetadata"]["KeyState"] != "PendingDeletion"

    result = cli(
        "kms", "schedule-key-deletion",
        "--key-id", key_id,
        "--pending-window-in-days", "7",
    )
    assert result.returncode == 0

    after = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert after["KeyMetadata"]["KeyState"] == "PendingDeletion"