def test_encrypt_asymmetric_rsa_oaep_sha1_roundtrip(cli, kms, tmp_path):
    import json, base64

    key = kms.rpc("CreateKey", {
        "KeyUsage": "ENCRYPT_DECRYPT",
        "KeySpec": "RSA_2048",
    })
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"sensitive-data-1234"
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

    dec = kms.rpc("Decrypt", {
        "CiphertextBlob": ciphertext,
        "KeyId": key_id,
        "EncryptionAlgorithm": "RSAES_OAEP_SHA_1",
    })
    assert base64.b64decode(dec["Plaintext"]) == plaintext