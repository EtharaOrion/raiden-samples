def test_generate_data_key_error_nonexistent(cli, kms):
    missing_key_id = "00000000-1111-2222-3333-444444444444"

    # Ensure the key genuinely does not exist
    keys = kms.rpc("ListKeys", {}).get("Keys", [])
    assert all(k.get("KeyId") != missing_key_id for k in keys)

    result = cli(
        "kms", "generate-data-key",
        "--key-id", missing_key_id,
        "--key-spec", "AES_256",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr

    # Confirm the key still does not exist in kms state
    keys_after = kms.rpc("ListKeys", {}).get("Keys", [])
    assert all(k.get("KeyId") != missing_key_id for k in keys_after)