def test_encrypt_happy_path(cli, kms):
    import base64
    import json

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "key for encrypt happy-path test",
            "KeyUsage": "ENCRYPT_DECRYPT",
            "KeySpec": "SYMMETRIC_DEFAULT",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    plaintext_bytes = b"black-box KMS encryption test"
    plaintext_blob = base64.b64encode(plaintext_bytes).decode("ascii")

    result = cli(
        "kms",
        "encrypt",
        "--key-id",
        key_id,
        "--plaintext",
        plaintext_blob,
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert isinstance(output["CiphertextBlob"], str)
    assert output["CiphertextBlob"]

    decrypted = kms.rpc(
        "Decrypt",
        {"CiphertextBlob": output["CiphertextBlob"]},
    )
    assert base64.b64decode(decrypted["Plaintext"]) == plaintext_bytes
    assert decrypted["KeyId"] == output["KeyId"]