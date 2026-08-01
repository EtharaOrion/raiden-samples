def test_disable_key_invalid_nonexistent_key(cli, kms):
    # Use a well-formed but nonexistent key id — DisableKey must fail.
    missing_key_id = "00000000-1111-2222-3333-444444444444"

    result = cli("kms", "disable-key", "--key-id", missing_key_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr

    # Ensure no key with that id exists in state.
    listed = kms.rpc("ListKeys", {})
    ids = [k.get("KeyId") for k in listed.get("Keys", [])]
    assert missing_key_id not in ids