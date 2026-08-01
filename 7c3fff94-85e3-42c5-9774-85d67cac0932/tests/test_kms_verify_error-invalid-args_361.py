def test_verify_missing_signing_algorithm(cli, kms, tmp_path):
    import base64

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "verify missing signing algorithm test",
            "KeyUsage": "SIGN_VERIFY",
            "KeySpec": "RSA_2048",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    message = b"message signed before testing argument validation"
    encoded_message = base64.b64encode(message).decode("ascii")
    signed = kms.rpc(
        "Sign",
        {
            "KeyId": key_id,
            "Message": encoded_message,
            "MessageType": "RAW",
            "SigningAlgorithm": "RSASSA_PKCS1_V1_5_SHA_256",
        },
    )

    message_path = tmp_path / "message.bin"
    signature_path = tmp_path / "signature.bin"
    message_path.write_bytes(message)
    signature_path.write_bytes(base64.b64decode(signed["Signature"]))

    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert before["Enabled"] is True
    assert before["KeyUsage"] == "SIGN_VERIFY"

    result = cli(
        "kms",
        "verify",
        "--key-id",
        key_id,
        "--message",
        f"fileb://{message_path}",
        "--signature",
        f"fileb://{signature_path}",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--signing-algorithm" in result.stderr

    after = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert after["KeyId"] == key_id
    assert after["Enabled"] is True
    assert after["KeyState"] == before["KeyState"]
    assert after["KeyUsage"] == "SIGN_VERIFY"