def test_generate_data_key_pending_deletion_invalid_state(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "gdk-invalid-state"})
    key_id = created["KeyMetadata"]["KeyId"]

    sched = kms.rpc("ScheduleKeyDeletion", {"KeyId": key_id, "PendingWindowInDays": 7})
    assert sched.get("KeyId", "").endswith(key_id) or sched.get("KeyId") == key_id

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyState"] == "PendingDeletion"

    result = cli("kms", "generate-data-key", "--key-id", key_id, "--key-spec", "AES_256")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "KMSInvalidStateException" in result.stderr

    # key still describable and still in PendingDeletion
    described_after = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described_after["KeyMetadata"]["KeyState"] == "PendingDeletion"