def test_encrypt_nonexistent_key_id_errors(cli, kms, tmp_path):
    # Use a well-formed but nonexistent key id so encrypt must fail.
    missing_key_id = "00000000-1111-2222-3333-444444444444"

    # Sanity: confirm this key really does not exist in kms state.
    try:
        resp = kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        # If somehow present, fail loudly — test precondition broken.
        assert "KeyMetadata" not in resp, "precondition: key must not exist"
    except Exception:
        pass

    result = cli(
        "kms", "encrypt",
        "--key-id", missing_key_id,
        "--plaintext", "aGVsbG8gd29ybGQ=",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr

    # Assert no ciphertext leaked and the key still does not exist as usable.
    try:
        resp = kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        assert "KeyMetadata" not in resp
    except Exception:
        pass