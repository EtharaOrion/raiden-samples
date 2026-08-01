def test_decrypt_round_trip_happy_path(cli, kms):
    import json, base64

    create = kms.rpc("CreateKey", {"Description": "decrypt-happy"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"hello decrypt world"
    pt_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    blob = enc["CiphertextBlob"]

    result = cli("kms", "decrypt", "--ciphertext-blob", blob)
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert base64.b64decode(out["Plaintext"]) == plaintext

    # independent read-back through raw kms
    dec = kms.rpc("Decrypt", {"CiphertextBlob": blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or key_id in dec["KeyId"]