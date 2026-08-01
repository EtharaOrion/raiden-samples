def test_disable_key_invalid_args(cli, kms):
    create = kms.rpc("CreateKey", {"Description": "test disable invalid args"})
    key_id = create["KeyMetadata"]["KeyId"]
    assert create["KeyMetadata"]["Enabled"] is True

    result = cli(
        "kms", "disable-key",
        "--key-id", key_id,
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "argument" in result.stderr.lower() or "unknown" in result.stderr.lower() or "option" in result.stderr.lower()

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["Enabled"] is True