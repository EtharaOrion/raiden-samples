def test_get_public_key_happy_path(cli, kms):
    import json

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "get-public-key happy path",
            "KeyUsage": "SIGN_VERIFY",
            "KeySpec": "RSA_2048",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "get-public-key", "--key-id", key_id)

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["PublicKey"]
    assert output["KeySpec"] == "RSA_2048"
    assert output["KeyUsage"] == "SIGN_VERIFY"
    assert "RSASSA_PKCS1_V1_5_SHA_256" in output["SigningAlgorithms"]

    independently_read = kms.rpc("GetPublicKey", {"KeyId": key_id})
    assert independently_read["PublicKey"] == output["PublicKey"]
    assert independently_read["KeySpec"] == "RSA_2048"
    assert independently_read["KeyUsage"] == "SIGN_VERIFY"

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["Enabled"] is True
    assert metadata["KeyUsage"] == "SIGN_VERIFY"
    assert metadata["KeySpec"] == "RSA_2048"