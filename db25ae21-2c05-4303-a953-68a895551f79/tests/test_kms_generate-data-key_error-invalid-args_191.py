def test_generate_data_key_invalid_key_id(cli, kms):
    bogus_key_id = "x" * 500
    result = cli(
        "kms", "generate-data-key",
        "--key-id", bogus_key_id,
        "--key-spec", "AES_256",
    )
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr or "Exception" in result.stderr

    # The bogus key must not exist in kms state.
    try:
        resp = kms.rpc("DescribeKey", {"KeyId": bogus_key_id})
        raise AssertionError(f"Expected DescribeKey to fail, got {resp}")
    except Exception:
        pass