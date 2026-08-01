def test_verify_valid_rsa_pss_signature(cli, kms, tmp_path):
    import base64
    import json

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "key for verify happy-path test",
            "KeyUsage": "SIGN_VERIFY",
            "KeySpec": "RSA_2048",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    message = b"message authenticated by KMS"
    message_b64 = base64.b64encode(message).decode("ascii")
    signed = kms.rpc(
        "Sign",
        {
            "KeyId": key_id,
            "Message": message_b64,
            "MessageType": "RAW",
            "SigningAlgorithm": "RSASSA_PSS_SHA_256",
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
        "RSASSA_PSS_SHA_256",
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["SignatureValid"] is True
    assert output["SigningAlgorithm"] == "RSASSA_PSS_SHA_256"

    independently_verified = kms.rpc(
        "Verify",
        {
            "KeyId": key_id,
            "Message": message_b64,
            "MessageType": "RAW",
            "Signature": signed["Signature"],
            "SigningAlgorithm": "RSASSA_PSS_SHA_256",
        },
    )
    assert independently_verified["SignatureValid"] is True
    assert independently_verified["KeyId"]

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id
    assert described["KeyMetadata"]["KeyUsage"] == "SIGN_VERIFY"