def test_disable_key_pending_deletion_invalid_state(cli, kms):
    create = kms.rpc("CreateKey", {"Description": "invalid state disable test"})
    key_id = create["KeyMetadata"]["KeyId"]

    sched = kms.rpc("ScheduleKeyDeletion", {"KeyId": key_id, "PendingWindowInDays": 7})
    assert sched is not None

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyState"] == "PendingDeletion"

    result = cli("kms", "disable-key", "--key-id", key_id)
    assert result.returncode != 0
    assert "KMSInvalidStateException" in result.stderr

    after = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert after["KeyMetadata"]["KeyState"] == "PendingDeletion"