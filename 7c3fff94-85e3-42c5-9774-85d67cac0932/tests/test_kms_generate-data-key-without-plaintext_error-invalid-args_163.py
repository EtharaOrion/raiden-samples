def test_generate_data_key_without_plaintext_rejects_empty_key_id(cli, kms, tmp_path):
    created = kms.rpc(
        "CreateKey",
        {"Description": "empty-key-id-validation-sentinel"},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms",
        "generate-data-key-without-plaintext",
        "--key-id",
        "",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Invalid length" in result.stderr

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["Description"] == "empty-key-id-validation-sentinel"
    assert metadata["KeyState"] == "Enabled"