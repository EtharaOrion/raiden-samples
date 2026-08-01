def test_generate_data_key_without_plaintext_happy_path(cli, kms):
    import base64
    import json

    created = kms.rpc(
        "CreateKey",
        {"Description": "generate-data-key-without-plaintext test"},
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

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert "Plaintext" not in output
    assert isinstance(output["CiphertextBlob"], str)
    assert output["CiphertextBlob"]

    decrypted = kms.rpc(
        "Decrypt",
        {"CiphertextBlob": output["CiphertextBlob"]},
    )
    assert len(base64.b64decode(decrypted["Plaintext"], validate=True)) == 32

    metadata = kms.rpc("DescribeKey", {"KeyId": decrypted["KeyId"]})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["Enabled"] is True