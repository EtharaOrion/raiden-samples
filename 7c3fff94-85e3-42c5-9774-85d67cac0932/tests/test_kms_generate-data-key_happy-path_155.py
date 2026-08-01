def test_generate_data_key_happy_path(cli, kms):
    import base64
    import json

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "generate-data-key happy path",
            "KeyUsage": "ENCRYPT_DECRYPT",
            "KeySpec": "SYMMETRIC_DEFAULT",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms",
        "generate-data-key",
        "--key-id",
        key_id,
        "--key-spec",
        "AES_256",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert base64.b64decode(output["Plaintext"], validate=True)
    assert len(base64.b64decode(output["Plaintext"], validate=True)) == 32
    assert base64.b64decode(output["CiphertextBlob"], validate=True)

    decrypted = kms.rpc(
        "Decrypt",
        {"CiphertextBlob": output["CiphertextBlob"]},
    )
    assert decrypted["Plaintext"] == output["Plaintext"]
    assert decrypted["KeyId"] in {
        key_id,
        created["KeyMetadata"]["Arn"],
    }