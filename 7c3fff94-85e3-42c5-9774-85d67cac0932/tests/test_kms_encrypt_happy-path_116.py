def test_encrypt_happy_path_round_trip(cli, kms):
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
    plaintext = b"black-box KMS encryption test"
    encoded_plaintext = base64.b64encode(plaintext).decode("ascii")

    result = cli(
        "kms",
        "encrypt",
        "--key-id",
        key_id,
        "--plaintext",
        encoded_plaintext,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert isinstance(output["CiphertextBlob"], str)
    assert output["CiphertextBlob"]

    decrypted = kms.rpc(
        "Decrypt",
        {"CiphertextBlob": output["CiphertextBlob"]},
    )
    assert base64.b64decode(decrypted["Plaintext"]) == plaintext
    assert decrypted["KeyId"] in {key_id, created["KeyMetadata"]["Arn"]}