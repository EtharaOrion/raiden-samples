def test_create_alias_already_exists_error(cli, kms, tmp_path):
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]

    import uuid
    alias_name = "alias/dup-" + uuid.uuid4().hex

    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "create-alias", "--alias-name", alias_name,
                 "--target-key-id", key_id)

    assert result.returncode != 0
    assert "AlreadyExistsException" in result.stderr

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    matching = [a for a in aliases if a["AliasName"] == alias_name]
    assert len(matching) == 1
    assert matching[0].get("TargetKeyId") == key_id