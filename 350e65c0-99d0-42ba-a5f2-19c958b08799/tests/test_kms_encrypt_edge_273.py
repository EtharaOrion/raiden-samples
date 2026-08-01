def test_encrypt_asymmetric_rsa_oaep_roundtrip(cli, kms, tmp_path):
    import json, base64

    # Prerequisite: create an asymmetric ENCRYPT_DECRYPT key
    create = kms.rpc("CreateKey", {
        "KeyUsage": "ENCRYPT_DECRYPT",
        "KeySpec": "RSA_2048",
        "Description": "asym-encrypt-test",
    })
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"top-secret-payload"
    pt_b64 = base64.b64encode(plaintext).decode()

    # Encrypt using the CLI with RSAES_OAEP_SHA_256
    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", pt_b64,
        "--encryption-algorithm", "RSAES_OAEP_SHA_256",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext = out["CiphertextBlob"]
    assert ciphertext

    # Independent read: decrypt the produced blob and verify round trip
    dec = kms.rpc("Decrypt", {
        "CiphertextBlob": ciphertext,
        "KeyId": key_id,
        "EncryptionAlgorithm": "RSAES_OAEP_SHA_256",
    })
    assert base64.b64decode(dec["Plaintext"]) == plaintext