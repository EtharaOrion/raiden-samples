def test_schedule_key_deletion_sets_pending_deletion(cli, kms):
    created = kms.rpc("CreateKey", {
        "Description": "key scheduled for deletion",
        "KeyUsage": "ENCRYPT_DECRYPT",
        "KeySpec": "SYMMETRIC_DEFAULT",
    })
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert before["KeyState"] == "Enabled"
    assert before["Enabled"] is True

    result = cli("kms", "schedule-key-deletion", "--key-id", key_id)
    assert result.returncode == 0

    after = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert after["KeyId"] == key_id
    assert after["KeyState"] == "PendingDeletion"
    assert after["Enabled"] is False