def test_disable_key_invalid_state(cli, kms):
    # Seed: create a key, then schedule it for deletion (PendingDeletion state)
    created = kms.rpc("CreateKey", {"Description": "invalid-state-disable-test"})
    key_id = created["KeyMetadata"]["KeyId"]

    sched = kms.rpc("ScheduleKeyDeletion", {"KeyId": key_id, "PendingWindowInDays": 7})
    assert sched  # scheduled

    # Confirm precondition state
    pre = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert pre["KeyMetadata"]["KeyState"] == "PendingDeletion"

    # Command under test: attempt to disable a key in PendingDeletion -> invalid state error
    result = cli("kms", "disable-key", "--key-id", key_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "KMSInvalidStateException" in result.stderr

    # State must remain PendingDeletion (disable had no effect)
    post = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert post["KeyMetadata"]["KeyState"] == "PendingDeletion"