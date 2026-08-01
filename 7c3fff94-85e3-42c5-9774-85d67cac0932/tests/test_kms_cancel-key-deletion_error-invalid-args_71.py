def test_cancel_key_deletion_rejects_empty_key_id(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "empty-key-id validation sentinel"})
    key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc("ScheduleKeyDeletion", {"KeyId": key_id, "PendingWindowInDays": 7})
    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert before["KeyState"] == "PendingDeletion"

    result = cli("kms", "cancel-key-deletion", "--key-id", "")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Invalid length" in result.stderr

    after = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert after["KeyId"] == key_id
    assert after["KeyState"] == "PendingDeletion"
    assert after["Enabled"] is False