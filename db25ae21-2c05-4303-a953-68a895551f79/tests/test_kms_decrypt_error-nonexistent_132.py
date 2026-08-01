def test_decrypt_nonexistent_ciphertext(cli, kms, tmp_path):
    import base64

    # Build a syntactically valid base64 blob that does not correspond to any
    # real ciphertext produced by this backend.
    bogus = base64.b64encode(b"this-is-not-a-valid-kms-ciphertext-blob").decode()

    result = cli("kms", "decrypt", "--ciphertext-blob", bogus)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    stderr = result.stderr
    assert (
        "NotFoundException" in stderr
        or "InvalidCiphertextException" in stderr
    ), stderr

    # Sanity: the backend still functions for a legitimate round-trip, proving
    # the failure above was a genuine rejection, not a broken service.
    key = kms.rpc("CreateKey", {})["KeyMetadata"]
    key_id = key["KeyId"]
    pt = base64.b64encode(b"hello world").decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt})
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert dec["Plaintext"] == pt