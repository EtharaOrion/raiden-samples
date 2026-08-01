def test_disable_key_invalid_state(cli, kms):
    # Seed a key and schedule it for deletion so it is in PendingDeletion state
    created = kms.rpc("CreateKey", {"Description": "invalid-state test"})
    key_id = created["KeyMetadata"]["KeyId"]

    sched = kms.rpc("ScheduleKeyDeletion", {"KeyId": key_id, "PendingWindowInDays": 7})
    assert sched  # request succeeded

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyState"] == "PendingDeletion"

    # Attempt to disable a key that is in an incompatible (PendingDeletion) state
    result = cli("kms", "disable-key", "--key-id", key_id)
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "KMSInvalidStateException" in result.stderr

    # State must remain PendingDeletion (disable did not take effect)
    after = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert after["KeyMetadata"]["KeyState"] == "PendingDeletion"