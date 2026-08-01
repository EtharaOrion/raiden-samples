def test_sign_rejects_unknown_flag(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {
            "Description": "sign invalid-arguments test",
            "KeyUsage": "SIGN_VERIFY",
            "KeySpec": "RSA_2048",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms",
        "sign",
        "--key-id",
        key_id,
        "--message",
        "aGVsbG8=",
        "--signing-algorithm",
        "RSASSA_PKCS1_V1_5_SHA_256",
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["Description"] == "sign invalid-arguments test"
    assert metadata["KeyUsage"] == "SIGN_VERIFY"
    assert metadata["KeyState"] == "Enabled"
    assert metadata["Enabled"] is True