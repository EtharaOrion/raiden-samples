def test_encrypt_nonexistent_key_id_rejected(cli, kms, tmp_path):
    import base64, json

    # Use a well-formed but nonexistent key id — encrypt must fail.
    missing_key_id = "00000000-1111-2222-3333-444444444444"

    # Sanity: this key does not exist in the backend.
    try:
        kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        assert False, "precondition failed: key unexpectedly exists"
    except Exception:
        pass

    plaintext = base64.b64encode(b"secret-data").decode("ascii")

    result = cli("kms", "encrypt", "--key-id", missing_key_id,
                 "--plaintext", plaintext)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr or "KeyUnavailable" in result.stderr

    # Ensure no key was created as a side effect.
    try:
        kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        assert False, "key should still not exist after failed encrypt"
    except Exception:
        pass