def test_decrypt_roundtrip_returns_original_plaintext(cli, kms):
    import base64, json

    # Seed prerequisite state: create a key and encrypt a plaintext
    key = kms.rpc("CreateKey", {"Description": "decrypt-happy-path"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"top-secret-message"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext_b64})
    ciphertext_blob = enc["CiphertextBlob"]  # base64 string

    # Run the command under test
    result = cli("kms", "decrypt", "--ciphertext-blob", ciphertext_blob)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    # Decrypted plaintext must match the original input
    returned_plaintext = base64.b64decode(out["Plaintext"])
    assert returned_plaintext == plaintext

    # KeyId in response should reference our key
    assert key_id in out["KeyId"]

    # Independent state read: verify the key still exists and is enabled
    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc["KeyMetadata"]["KeyId"] == key_id
    assert desc["KeyMetadata"]["Enabled"] is True