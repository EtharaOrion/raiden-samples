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

    message = base64.b64encode(b"message authenticated by KMS").decode("ascii")
    algorithm = "RSASSA_PKCS1_V1_5_SHA_256"
    signed = kms.rpc(
        "Sign",
        {
            "KeyId": key_id,
            "Message": message,
            "MessageType": "RAW",
            "SigningAlgorithm": algorithm,
        },
    )
    signature = signed["Signature"]

    result = cli(
        "kms",
        "verify",
        "--key-id",
        key_id,
        "--message",
        message,
        "--signature",
        signature,
        "--signing-algorithm",
        algorithm,
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["SignatureValid"] is True
    assert output["SigningAlgorithm"] == algorithm

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["Enabled"] is True
    assert metadata["KeyUsage"] == "SIGN_VERIFY"
    assert metadata["KeySpec"] == "RSA_2048"

    independently_verified = kms.rpc(
        "Verify",
        {
            "KeyId": key_id,
            "Message": message,
            "MessageType": "RAW",
            "Signature": signature,
            "SigningAlgorithm": algorithm,
        },
    )
    assert independently_verified["SignatureValid"] is True
    assert independently_verified["SigningAlgorithm"] == algorithm