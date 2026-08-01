def test_generate_data_key_missing_key_not_found(cli, kms):
    # Use a non-existent key id; GenerateDataKey must fail with a NotFound category
    fake_key_id = "00000000-1111-2222-3333-444444444444"

    # Sanity: ensure the key really does not exist
    describe_failed = False
    try:
        kms.rpc("DescribeKey", {"KeyId": fake_key_id})
    except Exception:
        describe_failed = True
    assert describe_failed, "precondition: fake key must not exist"

    result = cli(
        "kms", "generate-data-key",
        "--key-id", fake_key_id,
        "--key-spec", "AES_256",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr

    # State assertion: the key still does not exist after the failed call
    still_missing = False
    try:
        kms.rpc("DescribeKey", {"KeyId": fake_key_id})
    except Exception:
        still_missing = True
    assert still_missing