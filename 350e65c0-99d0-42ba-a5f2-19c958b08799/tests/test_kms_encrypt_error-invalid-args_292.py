def test_encrypt_nonexistent_key_returns_error(cli, kms, tmp_path):
    import json, base64

    # Use a well-formed but non-existent key id so encrypt must fail.
    missing_key_id = "00000000-1111-2222-3333-444444444444"

    # Sanity: ensure this key really does not exist in the backend.
    try:
        kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        exists = True
    except Exception:
        exists = False
    assert not exists, "precondition: key must not exist"

    plaintext = base64.b64encode(b"secret data").decode()

    result = cli(
        "kms", "encrypt",
        "--key-id", missing_key_id,
        "--plaintext", plaintext,
    )

    assert result.returncode != 0
    assert "NotFoundException" in result.stderr

    # Confirm the key still does not exist (no side effect created).
    try:
        kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        exists_after = True
    except Exception:
        exists_after = False
    assert not exists_after