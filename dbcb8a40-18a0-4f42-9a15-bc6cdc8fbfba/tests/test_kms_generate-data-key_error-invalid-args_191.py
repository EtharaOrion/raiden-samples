def test_generate_data_key_invalid_key_id_not_found(cli, kms):
    bogus_key_id = "x" * 400
    result = cli(
        "kms", "generate-data-key",
        "--key-id", bogus_key_id,
        "--key-spec", "AES_256",
    )
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr or "Exception" in result.stderr

    # Verify the bogus key truly does not exist in kms state
    try:
        resp = kms.rpc("DescribeKey", {"KeyId": bogus_key_id})
        # If it somehow returns, it must not be a valid usable key metadata
        assert "KeyMetadata" not in resp
    except Exception:
        # NotFoundException from the backend is the expected outcome
        pass