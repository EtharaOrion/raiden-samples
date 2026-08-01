def test_decrypt_round_trip(cli, kms, tmp_path):
    import json, base64

    key = kms.rpc("CreateKey", {"Description": "decrypt-test"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"hello-decrypt-happy-path"
    pt_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    blob_b64 = enc["CiphertextBlob"]

    result = cli("kms", "decrypt", "--ciphertext-blob", blob_b64)
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert base64.b64decode(out["Plaintext"]) == plaintext

    # Independent verification via kms
    dec = kms.rpc("Decrypt", {"CiphertextBlob": blob_b64})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id