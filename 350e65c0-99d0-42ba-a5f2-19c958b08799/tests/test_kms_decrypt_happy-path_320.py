def test_decrypt_round_trip_recovers_plaintext(cli, kms, tmp_path):
    import json, base64

    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"hello kms decrypt round trip"
    pt_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    blob = enc["CiphertextBlob"]

    result = cli("kms", "decrypt", "--ciphertext-blob", blob)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert base64.b64decode(out["Plaintext"]) == plaintext
    assert key_id in out["KeyId"]

    # Independent verification via raw RPC round trip
    dec = kms.rpc("Decrypt", {"CiphertextBlob": blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext