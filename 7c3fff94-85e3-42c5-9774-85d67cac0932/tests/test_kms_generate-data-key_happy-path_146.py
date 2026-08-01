def test_generate_data_key_happy_path(cli, kms, tmp_path):
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
    metadata = created["KeyMetadata"]
    key_id = metadata["KeyId"]

    result = cli(
        "kms",
        "generate-data-key",
        "--key-id",
        key_id,
        "--key-spec",
        "AES_256",
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["KeyId"] in (key_id, metadata["Arn"])
    assert len(base64.b64decode(output["Plaintext"])) == 32

    decrypted = kms.rpc(
        "Decrypt",
        {"CiphertextBlob": output["CiphertextBlob"]},
    )
    assert decrypted["Plaintext"] == output["Plaintext"]
    assert decrypted["KeyId"] in (key_id, metadata["Arn"])