def test_verify_missing_required_message(cli, kms, tmp_path):
    import base64

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "verify missing message test",
            "KeyUsage": "SIGN_VERIFY",
            "KeySpec": "RSA_2048",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    algorithm = "RSASSA_PKCS1_V1_5_SHA_256"
    message = base64.b64encode(b"message requiring verification").decode("ascii")
    signed = kms.rpc(
        "Sign",
        {
            "KeyId": key_id,
            "Message": message,
            "MessageType": "RAW",
            "SigningAlgorithm": algorithm,
        },
    )

    signature_path = tmp_path / "signature.bin"
    signature_path.write_bytes(base64.b64decode(signed["Signature"]))

    result = cli(
        "kms",
        "verify",
        "--key-id",
        key_id,
        "--signature",
        f"fileb://{signature_path}",
        "--signing-algorithm",
        algorithm,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--message" in result.stderr

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["KeyUsage"] == "SIGN_VERIFY"
    assert metadata["KeyState"] == "Enabled"
    assert metadata["Enabled"] is True