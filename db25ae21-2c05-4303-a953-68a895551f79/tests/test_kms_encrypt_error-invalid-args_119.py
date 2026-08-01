def test_encrypt_missing_key_not_found(cli, kms, tmp_path):
    # Use a well-formed but nonexistent key id so Encrypt is rejected.
    missing_key_id = "00000000-1111-2222-3333-444444444444"

    # Sanity: ensure this key does not exist in the backend.
    try:
        kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        exists = True
    except Exception:
        exists = False
    assert not exists, "precondition failed: key unexpectedly exists"

    result = cli(
        "kms", "encrypt",
        "--key-id", missing_key_id,
        "--plaintext", "aGVsbG8gd29ybGQ=",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr

    # Confirm no key was created as a side effect.
    try:
        kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        still_exists = True
    except Exception:
        still_exists = False
    assert not still_exists