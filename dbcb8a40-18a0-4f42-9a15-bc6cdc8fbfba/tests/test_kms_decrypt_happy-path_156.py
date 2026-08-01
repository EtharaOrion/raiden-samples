def test_decrypt_round_trip_happy_path(cli, kms, tmp_path):
    import base64, json

    key = kms.rpc("CreateKey", {"Description": "decrypt-happy-path"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"top-secret-payload-42"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext_b64})
    ciphertext_blob = enc["CiphertextBlob"]

    result = cli("kms", "decrypt", "--ciphertext-blob", ciphertext_blob)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert out["KeyId"].split("/")[-1].endswith(key_id) or key_id in out["KeyId"]

    returned_plaintext = base64.b64decode(out["Plaintext"])
    assert returned_plaintext == plaintext

    # Independent read: decrypt again via raw rpc and confirm round trip.
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext