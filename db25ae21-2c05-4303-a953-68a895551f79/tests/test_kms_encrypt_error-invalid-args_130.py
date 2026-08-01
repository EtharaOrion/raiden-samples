def test_encrypt_empty_plaintext_invalid(cli, kms, tmp_path):
    created = kms.rpc("CreateKey", {"Description": "encrypt-empty-plaintext"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", "")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Error" in result.stderr or "Exception" in result.stderr or "Invalid" in result.stderr

    # Key remains intact and usable — assert via a valid encrypt round trip
    import base64
    pt = base64.b64encode(b"hello").decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt})
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert dec["Plaintext"] == pt