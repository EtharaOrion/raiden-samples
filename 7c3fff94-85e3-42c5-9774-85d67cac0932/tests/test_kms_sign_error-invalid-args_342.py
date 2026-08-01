def test_sign_missing_required_message(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {
            "KeyUsage": "SIGN_VERIFY",
            "KeySpec": "RSA_2048",
            "Description": "sign missing-message argument test",
        },
    )
    baseline = created["KeyMetadata"]
    key_id = baseline["KeyId"]

    result = cli(
        "kms",
        "sign",
        "--key-id",
        key_id,
        "--signing-algorithm",
        "RSASSA_PKCS1_V1_5_SHA_256",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--message" in result.stderr

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["KeyUsage"] == "SIGN_VERIFY"
    assert metadata["KeySpec"] == "RSA_2048"
    assert metadata["KeyState"] == baseline["KeyState"]
    assert metadata["Enabled"] == baseline["Enabled"]