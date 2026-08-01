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
    metadata = created["KeyMetadata"]
    key_id = metadata["KeyId"]

    plaintext = b"black-box KMS encryption test"
    plaintext_blob = base64.b64encode(plaintext).decode("ascii")

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
    assert base64.b64decode(decrypted["Plaintext"]) == plaintext
    assert decrypted["KeyId"] in {metadata["KeyId"], metadata["Arn"]}