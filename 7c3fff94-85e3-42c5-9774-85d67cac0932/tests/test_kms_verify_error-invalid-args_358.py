def test_verify_missing_signature_rejected(cli, kms, tmp_path):
    created = kms.rpc(
        "CreateKey",
        {
            "Description": "verify missing signature test",
            "KeyUsage": "SIGN_VERIFY",
            "KeySpec": "RSA_2048",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]
    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]

    message_file = tmp_path / "message.bin"
    message_file.write_bytes(b"message requiring a signature")

    result = cli(
        "kms",
        "verify",
        "--key-id",
        key_id,
        "--message",
        f"fileb://{message_file}",
        "--signing-algorithm",
        "RSASSA_PKCS1_V1_5_SHA_256",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    stderr = result.stderr.lower()
    assert "required" in stderr
    assert "--signature" in stderr

    after = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert after["KeyId"] == before["KeyId"]
    assert after["KeyUsage"] == "SIGN_VERIFY"
    assert after["KeySpec"] == "RSA_2048"
    assert after["Enabled"] is True
    assert after["KeyState"] == before["KeyState"] == "Enabled"