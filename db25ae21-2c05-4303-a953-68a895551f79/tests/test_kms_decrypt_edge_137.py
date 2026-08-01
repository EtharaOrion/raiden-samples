def test_kms_decrypt_asymmetric_rsa_oaep_sha1_roundtrip(cli, kms, tmp_path):
    import json
    import base64

    key = kms.rpc("CreateKey", {
        "KeyUsage": "ENCRYPT_DECRYPT",
        "KeySpec": "RSA_2048",
    })
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"asymmetric-secret-42"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {
        "KeyId": key_id,
        "Plaintext": plaintext_b64,
        "EncryptionAlgorithm": "RSAES_OAEP_SHA_1",
    })
    ciphertext_blob = enc["CiphertextBlob"]

    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", ciphertext_blob,
        "--key-id", key_id,
        "--encryption-algorithm", "RSAES_OAEP_SHA_1",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert base64.b64decode(out["Plaintext"]) == plaintext

    # Independent state read: decrypt again via raw client and confirm round trip.
    dec = kms.rpc("Decrypt", {
        "CiphertextBlob": ciphertext_blob,
        "KeyId": key_id,
        "EncryptionAlgorithm": "RSAES_OAEP_SHA_1",
    })
    assert base64.b64decode(dec["Plaintext"]) == plaintext

    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc["KeyMetadata"]["KeyId"] == key_id