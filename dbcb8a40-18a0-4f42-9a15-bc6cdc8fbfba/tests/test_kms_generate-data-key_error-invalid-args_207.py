def test_generate_data_key_pending_deletion_invalid_state(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "gen-data-key-invalid-state"})
    key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc("ScheduleKeyDeletion", {"KeyId": key_id, "PendingWindowInDays": 7})

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyState"] == "PendingDeletion"

    result = cli("kms", "generate-data-key", "--key-id", key_id, "--key-spec", "AES_256")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "KMSInvalidStateException" in result.stderr

    # key still exists in PendingDeletion state
    after = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert after["KeyMetadata"]["KeyState"] == "PendingDeletion"