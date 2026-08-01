def test_create_alias_happy_path(cli, kms, tmp_path):
    created = kms.rpc("CreateKey", {"Description": "alias-target"})
    key_id = created["KeyMetadata"]["KeyId"]

    import uuid
    alias_name = "alias/test-" + uuid.uuid4().hex[:12]

    result = cli("kms", "create-alias",
                 "--alias-name", alias_name,
                 "--target-key-id", key_id)
    assert result.returncode == 0

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    match = [a for a in aliases if a["AliasName"] == alias_name]
    assert match, f"{alias_name} not found in {aliases}"
    assert match[0].get("TargetKeyId") == key_id