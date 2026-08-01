def test_encrypt_missing_required_plaintext(cli, kms, tmp_path):
    # Seed a valid key so the only problem is the missing --plaintext arg
    created = kms.rpc("CreateKey", {"Description": "encrypt-missing-plaintext"})
    key_id = created["KeyMetadata"]["KeyId"]

    # Invoke encrypt WITHOUT the required --plaintext
    result = cli("kms", "encrypt", "--key-id", key_id)

    # Parameter error: must fail
    assert result.returncode != 0
    assert "plaintext" in result.stderr.lower()

    # The key remains untouched/usable (state assertion via round trip)
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id
    assert described["KeyMetadata"]["Enabled"] is True

    import base64
    pt = base64.b64encode(b"round-trip-data").decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt})
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert dec["Plaintext"] == pt