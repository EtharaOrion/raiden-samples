def test_generate_data_key_nonexistent_key_errors(cli, kms):
    # Ensure the bogus key id is not present in KMS state
    bogus_key_id = "00000000-0000-0000-0000-000000000000"
    listed = kms.rpc("ListKeys", {})
    assert all(k.get("KeyId") != bogus_key_id for k in listed.get("Keys", [])), \
        "precondition failed: bogus key unexpectedly exists"

    result = cli(
        "kms", "generate-data-key",
        "--key-id", bogus_key_id,
        "--key-spec", "AES_256",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr

    # Confirm the key still does not exist in KMS state
    listed_after = kms.rpc("ListKeys", {})
    assert all(k.get("KeyId") != bogus_key_id for k in listed_after.get("Keys", []))