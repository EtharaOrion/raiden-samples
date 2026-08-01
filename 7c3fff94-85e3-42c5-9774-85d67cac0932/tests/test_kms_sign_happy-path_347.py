def test_sign_happy_path(cli, kms):
    import base64
    import json

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "asymmetric key for sign test",
            "KeyUsage": "SIGN_VERIFY",
            "KeySpec": "RSA_2048",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]
    message = base64.b64encode(b"message signed by the CLI").decode("ascii")
    algorithm = "RSASSA_PKCS1_V1_5_SHA_256"

    result = cli(
        "kms",
        "sign",
        "--key-id",
        key_id,
        "--message",
        message,
        "--signing-algorithm",
        algorithm,
    )

    assert result.returncode == 0
    response = json.loads(result.stdout)
    assert response["SigningAlgorithm"] == algorithm
    assert isinstance(response["Signature"], str)
    assert response["Signature"]

    verification = kms.rpc(
        "Verify",
        {
            "KeyId": key_id,
            "Message": message,
            "MessageType": "RAW",
            "Signature": response["Signature"],
            "SigningAlgorithm": algorithm,
        },
    )
    assert verification["SignatureValid"] is True
    assert verification["SigningAlgorithm"] == algorithm