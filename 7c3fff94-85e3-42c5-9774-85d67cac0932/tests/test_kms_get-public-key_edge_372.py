def test_get_public_key_with_grant_token(cli, kms):
    import base64
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

    result = cli(
        "kms",
        "get-public-key",
        "--key-id",
        key_id,
        "--grant-tokens",
        "xxxxxxxxxx",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["KeySpec"] == "RSA_2048"
    assert output["KeyUsage"] == "SIGN_VERIFY"
    assert "RSASSA_PKCS1_V1_5_SHA_256" in output["SigningAlgorithms"]
    assert base64.b64decode(output["PublicKey"], validate=True)

    observed = kms.rpc("GetPublicKey", {"KeyId": key_id})
    assert observed["KeyId"] == output["KeyId"]
    assert observed["KeySpec"] == "RSA_2048"
    assert observed["KeyUsage"] == "SIGN_VERIFY"
    assert observed["PublicKey"] == output["PublicKey"]
    assert set(observed["SigningAlgorithms"]) == set(output["SigningAlgorithms"])