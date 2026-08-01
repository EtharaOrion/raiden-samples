def test_generate_random_rejects_zero_number_of_bytes(cli, kms, tmp_path):
    created = kms.rpc(
        "CreateKey",
        {"Description": "generate-random invalid-args sentinel"},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms",
        "generate-random",
        "--number-of-bytes",
        "0",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "parameter validation failed" in result.stderr.lower()
    assert "invalid value" in result.stderr.lower()

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["Description"] == "generate-random invalid-args sentinel"
    assert metadata["Enabled"] is True