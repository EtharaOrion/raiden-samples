def test_get_public_key_asymmetric_happy_path(cli, kms):
    import json

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "asymmetric key for get-public-key test",
            "KeyUsage": "SIGN_VERIFY",
            "KeySpec": "RSA_2048",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "get-public-key", "--key-id", key_id)

    assert result.returncode == 0
    output = json.loads(result.stdout)

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["KeySpec"] == "RSA_2048"
    assert metadata["KeyUsage"] == "SIGN_VERIFY"
    assert metadata["Enabled"] is True

    observed = kms.rpc("GetPublicKey", {"KeyId": key_id})
    assert output["KeyId"] == observed["KeyId"]
    assert output["PublicKey"] == observed["PublicKey"]
    assert output["KeySpec"] == observed["KeySpec"] == "RSA_2048"
    assert output["KeyUsage"] == observed["KeyUsage"] == "SIGN_VERIFY"
    assert output["SigningAlgorithms"] == observed["SigningAlgorithms"]
    assert "RSASSA_PKCS1_V1_5_SHA_256" in observed["SigningAlgorithms"]