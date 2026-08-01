def test_schedule_key_deletion_empty_key_id_errors(cli, kms):
    # Establish a valid key first to ensure the error is due to the empty key-id, not lack of state
    created = kms.rpc("CreateKey", {"Description": "seed key for empty key-id test"})
    key_id = created["KeyMetadata"]["KeyId"]
    assert key_id

    # Run the command under test with an empty --key-id
    result = cli("kms", "schedule-key-deletion", "--key-id", "")

    # Must fail
    assert result.returncode != 0
    # Must surface an error category in stderr
    stderr = result.stderr
    assert ("Exception" in stderr) or ("ValidationError" in stderr) or ("Invalid" in stderr)

    # The seeded key must be untouched (not scheduled for deletion)
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyState"] != "PendingDeletion"