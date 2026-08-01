def test_decrypt_round_trip_happy_path(cli, kms, tmp_path):
    import base64, json

    # Seed: create a key and encrypt a known plaintext
    key = kms.rpc("CreateKey", {"Description": "decrypt-happy"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"the quick brown fox"
    pt_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    blob = enc["CiphertextBlob"]

    # Run command under test
    result = cli("kms", "decrypt", "--ciphertext-blob", blob)
    assert result.returncode == 0

    out = json.loads(result.stdout)
    decrypted = base64.b64decode(out["Plaintext"])
    assert decrypted == plaintext
    assert out["KeyId"].endswith(key_id) or key_id in out["KeyId"]

    # Independent read-back via kms: decrypting the same blob yields the plaintext
    dec = kms.rpc("Decrypt", {"CiphertextBlob": blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext