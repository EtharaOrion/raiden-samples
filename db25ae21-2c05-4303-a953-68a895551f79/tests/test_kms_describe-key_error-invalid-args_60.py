def test_describe_key_invalid_args(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "seed"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "describe-key",
        "--key-id", key_id,
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    stderr = result.stderr.lower()
    assert "attribute-definitions" in stderr or "unknown" in stderr or "argument" in stderr

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id