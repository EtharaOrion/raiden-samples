def test_cancel_key_deletion_invalid_args(cli, kms, tmp_path):
    # Seed a valid key so the only problem is the bogus flag
    created = kms.rpc("CreateKey", {})
    key_id = created["KeyMetadata"]["KeyId"]

    # --attribute-definitions is not a valid flag for cancel-key-deletion
    result = cli(
        "kms", "cancel-key-deletion",
        "--key-id", key_id,
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert "Unknown options" in result.stderr or "argument" in result.stderr.lower()

    # State must be unchanged: key was never scheduled for deletion
    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc["KeyMetadata"]["KeyState"] != "PendingDeletion"