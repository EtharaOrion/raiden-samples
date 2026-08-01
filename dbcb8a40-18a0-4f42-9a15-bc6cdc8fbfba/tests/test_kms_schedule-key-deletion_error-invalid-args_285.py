def test_schedule_key_deletion_invalid_key_id(cli, kms):
    result = cli(
        "kms",
        "schedule-key-deletion",
        "--key-id",
        "nonexistent-key-id-does-not-exist",
    )
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr

    # Ensure no such key was created as a side effect
    keys = kms.rpc("ListKeys", {}).get("Keys", [])
    assert all(
        k.get("KeyId") != "nonexistent-key-id-does-not-exist" for k in keys
    )