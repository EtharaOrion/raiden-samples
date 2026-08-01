def test_encrypt_happy_path_roundtrip(cli, kms, tmp_path):
    import json, base64

    # Prerequisite: create a symmetric ENCRYPT_DECRYPT key
    create = kms.rpc("CreateKey", {"Description": "encrypt-happy-path"})
    key_id = create["KeyMetadata"]["KeyId"]
    assert create["KeyMetadata"]["KeyUsage"] == "ENCRYPT_DECRYPT"

    plaintext = b"super-secret-payload"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    result = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", plaintext_b64)
    assert result.returncode == 0

    out = json.loads(result.stdout)
    ciphertext_blob = out["CiphertextBlob"]
    assert ciphertext_blob
    # the ciphertext must differ from the plaintext bytes
    assert ciphertext_blob != plaintext_b64

    # Independent read: decrypt the produced blob and assert the round trip
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(decrypt["Plaintext"]) == plaintext
    assert decrypt["KeyId"].endswith(key_id) or decrypt["KeyId"] == key_id