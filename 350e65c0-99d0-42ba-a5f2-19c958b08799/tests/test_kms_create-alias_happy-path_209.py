def test_create_alias_happy_path(cli, kms, tmp_path):
    created = kms.rpc("CreateKey", {"Description": "alias target"})
    key_id = created["KeyMetadata"]["KeyId"]

    alias_name = "alias/happy-path-alias-v5"

    result = cli(
        "kms", "create-alias",
        "--alias-name", alias_name,
        "--target-key-id", key_id,
    )
    assert result.returncode == 0, result.stderr

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    match = [a for a in aliases if a["AliasName"] == alias_name]
    assert match, f"alias {alias_name} not found in {aliases}"
    assert match[0].get("TargetKeyId") == key_id

    described = kms.rpc("DescribeKey", {"KeyId": alias_name})
    assert described["KeyMetadata"]["KeyId"] == key_id