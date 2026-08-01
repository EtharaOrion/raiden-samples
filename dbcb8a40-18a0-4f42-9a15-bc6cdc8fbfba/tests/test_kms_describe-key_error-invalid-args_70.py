def test_describe_key_nonexistent_returns_not_found(cli, kms):
    missing_key_id = "00000000-1111-2222-3333-444444444444"

    # Ensure the key does not exist in backend state
    listed = kms.rpc("ListKeys", {})
    existing_ids = {k["KeyId"] for k in listed.get("Keys", [])}
    assert missing_key_id not in existing_ids

    result = cli("kms", "describe-key", "--key-id", missing_key_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr

    # Confirm the key still does not exist after the failed describe
    listed_after = kms.rpc("ListKeys", {})
    existing_ids_after = {k["KeyId"] for k in listed_after.get("Keys", [])}
    assert missing_key_id not in existing_ids_after