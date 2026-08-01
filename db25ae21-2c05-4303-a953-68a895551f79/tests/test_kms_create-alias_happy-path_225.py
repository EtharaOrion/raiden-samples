def test_create_alias_happy_path(cli, kms, tmp_path):
    create_resp = kms.rpc("CreateKey", {"Description": "alias target key"})
    key_id = create_resp["KeyMetadata"]["KeyId"]

    alias_name = "alias/HappyPathAlias"

    # ensure alias doesn't already exist
    existing = kms.rpc("ListAliases", {})
    assert alias_name not in [a["AliasName"] for a in existing.get("Aliases", [])]

    result = cli(
        "kms", "create-alias",
        "--alias-name", alias_name,
        "--target-key-id", key_id,
    )
    assert result.returncode == 0

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    match = [a for a in aliases if a["AliasName"] == alias_name]
    assert len(match) == 1
    assert match[0].get("TargetKeyId") == key_id

    # alias resolves to the target key via DescribeKey
    described = kms.rpc("DescribeKey", {"KeyId": alias_name})
    assert described["KeyMetadata"]["KeyId"] == key_id