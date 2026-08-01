def test_generate_data_key_without_plaintext_rejects_unknown_flag(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"Description": "invalid-argument prerequisite key"},
    )
    metadata = created["KeyMetadata"]
    key_id = metadata["KeyId"]

    result = cli(
        "kms",
        "generate-data-key-without-plaintext",
        "--key-id",
        key_id,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    resulting_metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert resulting_metadata["KeyId"] == key_id
    assert resulting_metadata["Arn"] == metadata["Arn"]
    assert resulting_metadata["Enabled"] is True
    assert resulting_metadata["KeyState"] == "Enabled"