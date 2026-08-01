def test_encrypt_invalid_args(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "encrypt-invalid-args"})
    key_id = key["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", "aGVsbG8=",
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert "not-a-real-flag" in result.stderr or "Unknown option" in result.stderr

    # Key state unaffected: still describable and enabled
    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc["KeyMetadata"]["KeyId"] == key_id
    assert desc["KeyMetadata"]["Enabled"] is True