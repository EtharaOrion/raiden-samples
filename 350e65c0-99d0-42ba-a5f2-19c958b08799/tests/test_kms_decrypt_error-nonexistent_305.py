def test_decrypt_error_nonexistent(cli, kms, tmp_path):
    import base64

    # Craft a syntactically valid but meaningless ciphertext blob that
    # does not correspond to any real KMS ciphertext.
    bogus_blob = base64.b64encode(b"this-is-not-a-real-kms-ciphertext-blob").decode()

    result = cli("kms", "decrypt", "--ciphertext-blob", bogus_blob)

    assert result.returncode != 0
    assert "Exception" in result.stderr or "NotFound" in result.stderr

    # Sanity check that the backend is alive and this blob truly cannot
    # be decrypted through the raw client either.
    try:
        resp = kms.rpc("Decrypt", {"CiphertextBlob": bogus_blob})
        raise AssertionError("Decrypt unexpectedly succeeded: %r" % resp)
    except AssertionError:
        raise
    except Exception:
        pass