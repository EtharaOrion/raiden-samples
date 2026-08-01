def test_sign_maximum_raw_message_succeeds(cli, kms):
    import base64
    import json

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "asymmetric key for maximum-length RAW signing test",
            "KeyUsage": "SIGN_VERIFY",
            "KeySpec": "RSA_2048",
        },
    )
    metadata = created["KeyMetadata"]
    key_id = metadata["KeyId"]

    message = base64.b64encode(b"x" * 4096).decode("ascii")
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
        "--message-type",
        "RAW",
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["SigningAlgorithm"] == algorithm
    assert output["KeyId"] in {key_id, metadata["Arn"]}
    assert isinstance(output["Signature"], str)
    assert base64.b64decode(output["Signature"], validate=True)

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
    assert verified["KeyId"] in {key_id, metadata["Arn"]}