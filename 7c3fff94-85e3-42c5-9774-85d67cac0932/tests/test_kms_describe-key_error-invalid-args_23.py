def test_describe_key_rejects_invalid_unknown_argument(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"Description": "describe-key invalid-argument sentinel"},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert before["Description"] == "describe-key invalid-argument sentinel"

    result = cli(
        "kms",
        "describe-key",
        "--key-id",
        key_id,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert after["KeyId"] == key_id
    assert after["Description"] == before["Description"]
    assert after["KeyState"] == before["KeyState"]