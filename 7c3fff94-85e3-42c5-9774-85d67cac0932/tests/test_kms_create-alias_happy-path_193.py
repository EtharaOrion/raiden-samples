def test_create_alias_happy_path(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"Description": "Target key for create-alias happy-path test"},
    )
    key_id = created["KeyMetadata"]["KeyId"]
    alias_name = "alias/create-alias-" + key_id

    target_before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert target_before["KeyId"] == key_id

    result = cli(
        "kms",
        "create-alias",
        "--alias-name",
        alias_name,
        "--target-key-id",
        key_id,
    )
    assert result.returncode == 0

    described_via_alias = kms.rpc(
        "DescribeKey",
        {"KeyId": alias_name},
    )["KeyMetadata"]
    assert described_via_alias["KeyId"] == key_id

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    assert any(
        alias.get("AliasName") == alias_name
        and alias.get("TargetKeyId") == key_id
        for alias in aliases
    )