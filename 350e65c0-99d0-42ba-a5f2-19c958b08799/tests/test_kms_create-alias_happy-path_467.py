def test_create_alias_happy_path(cli, kms):
    key = kms.rpc("CreateKey", {})["KeyMetadata"]
    key_id = key["KeyId"]
    alias_name = "alias/my-happy-alias-v16"

    # ensure alias not pre-existing
    existing = kms.rpc("ListAliases", {}).get("Aliases", [])
    assert not any(a.get("AliasName") == alias_name for a in existing)

    result = cli("kms", "create-alias",
                 "--alias-name", alias_name,
                 "--target-key-id", key_id)
    assert result.returncode == 0

    aliases = kms.rpc("ListAliases", {}).get("Aliases", [])
    match = [a for a in aliases if a.get("AliasName") == alias_name]
    assert len(match) == 1
    assert match[0].get("TargetKeyId") == key_id

    # alias resolves to the key via DescribeKey
    described = kms.rpc("DescribeKey", {"KeyId": alias_name})["KeyMetadata"]
    assert described["KeyId"] == key_id