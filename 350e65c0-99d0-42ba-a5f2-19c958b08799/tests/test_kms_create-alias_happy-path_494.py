def test_create_alias_happy_path(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "alias-target"})
    key_id = key["KeyMetadata"]["KeyId"]

    alias_name = "alias/test-happy-alias-v22"

    # ensure alias not already present
    existing = kms.rpc("ListAliases", {}).get("Aliases", [])
    assert not any(a["AliasName"] == alias_name for a in existing)

    result = cli(
        "kms", "create-alias",
        "--alias-name", alias_name,
        "--target-key-id", key_id,
    )
    assert result.returncode == 0

    aliases = kms.rpc("ListAliases", {}).get("Aliases", [])
    match = [a for a in aliases if a["AliasName"] == alias_name]
    assert len(match) == 1
    assert match[0].get("TargetKeyId") == key_id

    # alias should resolve to the same key via DescribeKey
    described = kms.rpc("DescribeKey", {"KeyId": alias_name})
    assert described["KeyMetadata"]["KeyId"] == key_id