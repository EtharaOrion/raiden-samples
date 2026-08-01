def test_sign_happy_path(cli, kms):
    import base64
    import json

    key = kms.rpc(
        "CreateKey",
        {
            "Description": "asymmetric signing key",
            "KeyUsage": "SIGN_VERIFY",
            "KeySpec": "RSA_2048",
        },
    )
    key_id = key["KeyMetadata"]["KeyId"]
    message = base64.b64encode(b"message to sign").decode("ascii")
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
    output = json.loads(result.stdout)
    assert output["SigningAlgorithm"] == algorithm
    assert output["Signature"]

    verification = kms.rpc(
        "Verify",
        {
            "KeyId": key_id,
            "Message": message,
            "MessageType": "RAW",
            "Signature": output["Signature"],
            "SigningAlgorithm": algorithm,
        },
    )
    assert verification["SignatureValid"] is True
    assert verification["SigningAlgorithm"] == algorithm