def test_schedule_key_deletion_sets_pending_state(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "to-delete"})
    key_id = created["KeyMetadata"]["KeyId"]

    pre = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert pre["KeyMetadata"]["KeyState"] != "PendingDeletion"

    result = cli("kms", "schedule-key-deletion", "--key-id", key_id,
                 "--pending-window-in-days", "7")
    assert result.returncode == 0

    post = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert post["KeyMetadata"]["KeyState"] == "PendingDeletion"