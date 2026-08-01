def test_re_encrypt_with_sm2pke_source_algorithm(cli, kms):
    import base64
    import json

    source_key = kms.rpc(
        "CreateKey",
        {"Description": "source key for re-encrypt test"},
    )["KeyMetadata"]
    destination_key = kms.rpc(
        "CreateKey",
        {"Description": "destination key for re-encrypt test"},
    )["KeyMetadata"]

    plaintext = base64.b64encode(b"plaintext re-encrypted with SM2PKE option").decode("ascii")
    encrypted = kms.rpc(
        "Encrypt",
        {
            "KeyId": source_key["KeyId"],
            "Plaintext": plaintext,
        },
    )

    result = cli(
        "kms",
        "re-encrypt",
        "--ciphertext-blob",
        encrypted["CiphertextBlob"],
        "--destination-key-id",
        destination_key["KeyId"],
        "--source-encryption-algorithm",
        "SM2PKE",
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["KeyId"] == destination_key["Arn"]

    decrypted = kms.rpc(
        "Decrypt",
        {"CiphertextBlob": output["CiphertextBlob"]},
    )
    assert decrypted["Plaintext"] == plaintext
    assert decrypted["KeyId"] == destination_key["Arn"]