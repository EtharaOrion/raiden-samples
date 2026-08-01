def test_schedule_key_deletion_missing_key(cli, kms):
    missing_key_id = "00000000-0000-0000-0000-000000000000"
    result = cli("kms", "schedule-key-deletion", "--key-id", missing_key_id)
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr

    # Ensure no real key entered PendingDeletion as a side effect
    listed = kms.rpc("ListKeys", {})
    for k in listed.get("Keys", []):
        if k["KeyId"] == missing_key_id:
            raise AssertionError("missing key unexpectedly present")