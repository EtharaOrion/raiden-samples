def test_sign_asymmetric_key_signature_verifies(cli, kms):
    import base64
    import json

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "asymmetric signing key",
            "KeyUsage": "SIGN_VERIFY",
            "KeySpec": "RSA_2048",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    message = base64.b64encode(b"message signed by kms").decode("ascii")
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
    assert isinstance(output["Signature"], str)
    assert output["Signature"]

    verified = kms.rpc(
        "Verify",
        {
            "KeyId": key_id,
            "Message": message,
            "MessageType": "RAW",
            "Signature": output["Signature"],
            "SigningAlgorithm": algorithm,
        },
    )
    assert verified["SignatureValid"] is True
    assert verified["SigningAlgorithm"] == algorithm