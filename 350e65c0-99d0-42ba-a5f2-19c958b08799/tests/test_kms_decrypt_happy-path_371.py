def test_decrypt_round_trip_happy_path(cli, kms, tmp_path):
    import base64, json

    # Seed: create a symmetric key and encrypt a known plaintext.
    key = kms.rpc("CreateKey", {"Description": "decrypt-happy"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"top-secret-message"
    pt_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    blob = enc["CiphertextBlob"]

    # Run the command under test.
    result = cli("kms", "decrypt", "--ciphertext-blob", blob)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    decrypted = base64.b64decode(out["Plaintext"])
    assert decrypted == plaintext

    # Independent read-back: decrypt via raw RPC yields the same plaintext.
    dec = kms.rpc("Decrypt", {"CiphertextBlob": blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext