def test_encrypt_asymmetric_rsa_oaep_roundtrip(cli, kms, tmp_path):
    import json, base64

    # Seed: create an asymmetric ENCRYPT_DECRYPT key that supports RSAES_OAEP_SHA_1
    create = kms.rpc("CreateKey", {
        "KeyUsage": "ENCRYPT_DECRYPT",
        "KeySpec": "RSA_2048",
        "Description": "encrypt-oaep-test",
    })
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"secret-oaep-data"
    b64_plain = base64.b64encode(plaintext).decode()

    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", b64_plain,
        "--encryption-algorithm", "RSAES_OAEP_SHA_1",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext = out["CiphertextBlob"]
    assert ciphertext

    # Independent read: decrypt the ciphertext via kms and assert round trip
    dec = kms.rpc("Decrypt", {
        "KeyId": key_id,
        "CiphertextBlob": ciphertext,
        "EncryptionAlgorithm": "RSAES_OAEP_SHA_1",
    })
    assert base64.b64decode(dec["Plaintext"]) == plaintext