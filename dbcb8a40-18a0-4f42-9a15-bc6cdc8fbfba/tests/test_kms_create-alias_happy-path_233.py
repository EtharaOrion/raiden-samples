def test_create_alias_happy_path(cli, kms):
    create = kms.rpc("CreateKey", {})
    key_id = create["KeyMetadata"]["KeyId"]

    import uuid
    alias_name = "alias/test-" + uuid.uuid4().hex

    result = cli("kms", "create-alias", "--alias-name", alias_name, "--target-key-id", key_id)
    assert result.returncode == 0

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    match = [a for a in aliases if a["AliasName"] == alias_name]
    assert len(match) == 1
    assert match[0].get("TargetKeyId") == key_id

    described = kms.rpc("DescribeKey", {"KeyId": alias_name})
    assert described["KeyMetadata"]["KeyId"] == key_id