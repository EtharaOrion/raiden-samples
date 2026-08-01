def test_generate_data_key_without_plaintext_rejects_unknown_invalid_json_argument(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"Description": "key for invalid generate-data-key-without-plaintext arguments"},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms",
        "generate-data-key-without-plaintext",
        "--key-id",
        key_id,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["Enabled"] is True
    assert metadata["KeyState"] == "Enabled"