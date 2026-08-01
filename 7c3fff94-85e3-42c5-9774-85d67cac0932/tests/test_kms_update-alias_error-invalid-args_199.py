def test_update_alias_missing_target_key_id(cli, kms, tmp_path):
    key = kms.rpc("CreateKey", {"Description": "update-alias missing target test"})
    key_id = key["KeyMetadata"]["KeyId"]
    alias_name = f"alias/update-missing-target-{key_id}"

    kms.rpc("CreateAlias", {
        "AliasName": alias_name,
        "TargetKeyId": key_id,
    })
    assert kms.rpc("DescribeKey", {"KeyId": alias_name})["KeyMetadata"]["KeyId"] == key_id

    result = cli(
        "kms",
        "update-alias",
        "--alias-name",
        alias_name,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--target-key-id" in result.stderr
    assert kms.rpc("DescribeKey", {"KeyId": alias_name})["KeyMetadata"]["KeyId"] == key_id