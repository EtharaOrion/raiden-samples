def test_encrypt_missing_key_not_found(cli, kms, tmp_path):
    # Use a well-formed but non-existent key id so Encrypt must fail.
    missing_key_id = "00000000-1111-2222-3333-444444444444"

    # Sanity: ensure this key really does not exist in the backend.
    try:
        kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        raise AssertionError("precondition failed: key unexpectedly exists")
    except Exception:
        pass

    result = cli(
        "kms", "encrypt",
        "--key-id", missing_key_id,
        "--plaintext", "aGVsbG8=",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr

    # State assertion: the key still does not exist after the failed call.
    try:
        kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        raise AssertionError("key should not exist after failed encrypt")
    except Exception:
        pass