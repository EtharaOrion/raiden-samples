def test_generate_data_key_without_plaintext_happy_path(cli, kms):
    import base64
    import json

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "generate-data-key-without-plaintext test",
            "KeyUsage": "ENCRYPT_DECRYPT",
            "KeySpec": "SYMMETRIC_DEFAULT",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms",
        "generate-data-key-without-plaintext",
        "--key-id",
        key_id,
        "--key-spec",
        "AES_256",
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert isinstance(output["CiphertextBlob"], str)
    assert output["CiphertextBlob"]
    assert "Plaintext" not in output

    decrypted = kms.rpc(
        "Decrypt",
        {"CiphertextBlob": output["CiphertextBlob"]},
    )
    plaintext = base64.b64decode(decrypted["Plaintext"], validate=True)
    assert len(plaintext) == 32
    assert decrypted["KeyId"].endswith(key_id)