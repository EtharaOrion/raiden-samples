def test_encrypt_invalid_unknown_argument(cli, kms):
    key = kms.rpc("CreateKey", {})["KeyMetadata"]
    key_id = key["KeyId"]

    import base64
    plaintext = base64.b64encode(b"secret data").decode()

    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", plaintext,
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert "argument" in result.stderr.lower() or "unknown" in result.stderr.lower() \
        or "usage" in result.stderr.lower()

    # State unchanged: the key still exists and is usable for a real encrypt round trip
    md = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert md["KeyId"] == key_id

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext})
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert dec["Plaintext"] == plaintext