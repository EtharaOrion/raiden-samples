def test_generate_data_key_disabled_key_error(cli, kms):
    create = kms.rpc("CreateKey", {"Description": "gdk disabled test"})
    key_id = create["KeyMetadata"]["KeyId"]

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

    still = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert still["KeyMetadata"]["Enabled"] is False