def test_verify_valid_signature(cli, kms, tmp_path):
    import base64
    import json

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "asymmetric key for verify happy-path test",
            "KeyUsage": "SIGN_VERIFY",
            "KeySpec": "RSA_2048",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]
    algorithm = "RSASSA_PKCS1_V1_5_SHA_256"
    message = b"message authenticated by the KMS verify test"

    signed = kms.rpc(
        "Sign",
        {
            "KeyId": key_id,
            "Message": base64.b64encode(message).decode("ascii"),
            "MessageType": "RAW",
            "SigningAlgorithm": algorithm,
        },
    )

    message_file = tmp_path / "message.bin"
    signature_file = tmp_path / "signature.bin"
    message_file.write_bytes(message)
    signature_file.write_bytes(base64.b64decode(signed["Signature"]))

    result = cli(
        "kms",
        "verify",
        "--key-id",
        key_id,
        "--message",
        f"fileb://{message_file}",
        "--signature",
        f"fileb://{signature_file}",
        "--signing-algorithm",
        algorithm,
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["SignatureValid"] is True
    assert output["SigningAlgorithm"] == algorithm

    described = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert described["KeyId"] == key_id
    assert described["KeyUsage"] == "SIGN_VERIFY"
    assert described["Enabled"] is True

    independently_verified = kms.rpc(
        "Verify",
        {
            "KeyId": key_id,
            "Message": base64.b64encode(message).decode("ascii"),
            "MessageType": "RAW",
            "Signature": signed["Signature"],
            "SigningAlgorithm": algorithm,
        },
    )
    assert independently_verified["SignatureValid"] is True
    assert independently_verified["SigningAlgorithm"] == algorithm