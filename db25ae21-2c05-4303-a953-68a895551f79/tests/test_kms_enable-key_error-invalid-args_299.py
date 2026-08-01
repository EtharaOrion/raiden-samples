def test_enable_key_invalid_args(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "invalid-args-test"})
    key_id = created["KeyMetadata"]["KeyId"]
    kms.rpc("DisableKey", {"KeyId": key_id})

    result = cli(
        "kms", "enable-key",
        "--key-id", key_id,
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr or "attribute-definitions" in result.stderr

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["Enabled"] is False