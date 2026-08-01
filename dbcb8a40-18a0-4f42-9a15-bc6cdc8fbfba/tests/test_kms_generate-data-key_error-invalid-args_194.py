def test_generate_data_key_disabled_key_error(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "gdk-disabled-test"})
    key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc("DisableKey", {"KeyId": key_id})

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["Enabled"] is False

    result = cli(
        "kms", "generate-data-key",
        "--key-id", key_id,
        "--key-spec", "AES_256",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "DisabledException" in result.stderr

    # key still describable and remains disabled
    after = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert after["KeyMetadata"]["Enabled"] is False