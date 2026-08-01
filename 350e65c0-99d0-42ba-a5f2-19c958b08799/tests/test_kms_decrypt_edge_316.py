def test_decrypt_sm2pke_roundtrip(cli, kms, tmp_path):
    import base64, json

    key = kms.rpc("CreateKey", {"Description": "sm2-decrypt-edge"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"secret-payload-sm2"
    pt_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    ciphertext_b64 = enc["CiphertextBlob"]

    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", ciphertext_b64,
        "--encryption-algorithm", "SM2PKE",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert base64.b64decode(out["Plaintext"]) == plaintext

    # independent read via kms
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or key_id in dec["KeyId"]