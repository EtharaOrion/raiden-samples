def test_generate_data_key_aes_128_round_trip(cli, kms, tmp_path):
    import base64
    import json

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "generate-data-key AES_128 test",
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
        "AES_128",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    plaintext = base64.b64decode(output["Plaintext"], validate=True)
    assert len(plaintext) == 16

    decrypted = kms.rpc(
        "Decrypt",
        {"CiphertextBlob": output["CiphertextBlob"]},
    )
    assert base64.b64decode(decrypted["Plaintext"], validate=True) == plaintext
    assert decrypted["KeyId"] in (key_id, created["KeyMetadata"]["Arn"])