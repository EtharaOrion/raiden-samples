def test_schedule_key_deletion_happy_path(cli, kms, tmp_path):
    created = kms.rpc("CreateKey", {"Description": "to-delete"})
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert before["KeyMetadata"]["KeyState"] != "PendingDeletion"

    result = cli("kms", "schedule-key-deletion", "--key-id", key_id,
                 "--pending-window-in-days", "7")
    assert result.returncode == 0

    after = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert after["KeyMetadata"]["KeyState"] == "PendingDeletion"