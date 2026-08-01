def test_encrypt_nonexistent_key(cli, kms, tmp_path):
    import base64, json

    # Use a well-formed but nonexistent key id (fresh UUID never created)
    missing_key_id = "00000000-1111-2222-3333-444455556666"

    # Confirm the key does not exist in kms state
    try:
        resp = kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        raise AssertionError("expected key to be absent, got: %r" % resp)
    except Exception:
        pass

    plaintext = base64.b64encode(b"secret data").decode()

    result = cli("kms", "encrypt", "--key-id", missing_key_id, "--plaintext", plaintext)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr

    # Verify no key was created as a side-effect
    try:
        resp = kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        raise AssertionError("key should still be absent, got: %r" % resp)
    except Exception:
        pass