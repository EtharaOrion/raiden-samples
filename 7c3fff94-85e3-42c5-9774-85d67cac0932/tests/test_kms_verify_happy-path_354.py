def test_verify_valid_signature(cli, kms, tmp_path):
    import base64
    import json

    algorithm = "RSASSA_PKCS1_V1_5_SHA_256"
    message = b"message whose signature should verify"

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "asymmetric key for verify test",
            "KeyUsage": "SIGN_VERIFY",
            "KeySpec": "RSA_2048",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    signed = kms.rpc(
        "Sign",
        {
            "KeyId": key_id,
            "Message": base64.b64encode(message).decode("ascii"),
            "MessageType": "RAW",
            "SigningAlgorithm": algorithm,
        },
    )

    message_path = tmp_path / "message.bin"
    signature_path = tmp_path / "signature.bin"
    message_path.write_bytes(message)
    signature_path.write_bytes(base64.b64decode(signed["Signature"]))

    result = cli(
        "kms",
        "verify",
        "--key-id",
        key_id,
        "--message",
        f"fileb://{message_path}",
        "--signature",
        f"fileb://{signature_path}",
        "--signing-algorithm",
        algorithm,
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["SignatureValid"] is True
    assert output["SigningAlgorithm"] == algorithm

    verified = kms.rpc(
        "Verify",
        {
            "KeyId": key_id,
            "Message": base64.b64encode(message).decode("ascii"),
            "MessageType": "RAW",
            "Signature": signed["Signature"],
            "SigningAlgorithm": algorithm,
        },
    )
    assert verified["SignatureValid"] is True
    assert verified["SigningAlgorithm"] == algorithm

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["KeyUsage"] == "SIGN_VERIFY"
    assert metadata["Enabled"] is True