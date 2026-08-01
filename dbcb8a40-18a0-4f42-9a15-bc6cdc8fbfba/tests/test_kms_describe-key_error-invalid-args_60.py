def test_describe_key_invalid_args(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "seed key for invalid args test"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "describe-key",
        "--key-id", key_id,
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "attribute-definitions" in result.stderr or "Unknown options" in result.stderr

    # Key should still exist and be describable via the backend.
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id