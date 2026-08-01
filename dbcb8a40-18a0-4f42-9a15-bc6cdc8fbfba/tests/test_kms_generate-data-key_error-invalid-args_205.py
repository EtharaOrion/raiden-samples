def test_generate_data_key_nonexistent_key_errors(cli, kms, tmp_path):
    # Use a valid-looking but nonexistent key id so the service rejects the request.
    missing_key_id = "00000000-1111-2222-3333-444444444444"

    # Sanity: ensure this key does not exist in the backend.
    listed = kms.rpc("ListKeys", {})
    existing_ids = {k["KeyId"] for k in listed.get("Keys", [])}
    assert missing_key_id not in existing_ids

    result = cli(
        "kms",
        "generate-data-key",
        "--key-id",
        missing_key_id,
        "--key-spec",
        "AES_256",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr

    # Confirm the backend still has no such key (no state was created).
    listed_after = kms.rpc("ListKeys", {})
    ids_after = {k["KeyId"] for k in listed_after.get("Keys", [])}
    assert missing_key_id not in ids_after