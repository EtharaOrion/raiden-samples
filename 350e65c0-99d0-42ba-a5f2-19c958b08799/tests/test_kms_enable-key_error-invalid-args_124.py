def test_enable_key_pending_deletion_invalid_state(cli, kms, tmp_path):
    created = kms.rpc("CreateKey", {"Description": "to be scheduled"})
    key_id = created["KeyMetadata"]["KeyId"]

    sched = kms.rpc("ScheduleKeyDeletion", {"KeyId": key_id, "PendingWindowInDays": 7})
    assert sched.get("KeyId", key_id)

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyState"] == "PendingDeletion"

    result = cli("kms", "enable-key", "--key-id", key_id)
    assert result.returncode != 0
    assert "KMSInvalidStateException" in result.stderr

    still = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert still["KeyMetadata"]["KeyState"] == "PendingDeletion"