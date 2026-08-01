def test_cancel_key_deletion_invalid_state(cli, kms):
    # Seed: create a key that is NOT pending deletion (KeyState will be Enabled)
    create = kms.rpc("CreateKey", {"Description": "cancel-deletion-invalid-state"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Sanity: key is not pending deletion
    before = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert before["KeyMetadata"]["KeyState"] != "PendingDeletion"

    # Attempt to cancel deletion on a key that isn't scheduled for deletion -> invalid state
    result = cli("kms", "cancel-key-deletion", "--key-id", key_id)
    assert result.returncode != 0
    assert "KMSInvalidStateException" in result.stderr

    # State unchanged: key still exists and is not pending deletion
    after = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert after["KeyMetadata"]["KeyState"] != "PendingDeletion"