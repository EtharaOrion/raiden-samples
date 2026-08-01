def test_list_aliases_rejects_empty_key_id(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "list-aliases empty key-id test"})
    key_id = key["KeyMetadata"]["KeyId"]
    alias_name = "alias/list-aliases-empty-key-id"
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    before = kms.rpc("ListAliases", {"KeyId": key_id})
    before_aliases = {
        (alias["AliasName"], alias.get("TargetKeyId"))
        for alias in before["Aliases"]
    }
    assert (alias_name, key_id) in before_aliases

    result = cli("kms", "list-aliases", "--key-id", "")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Parameter validation failed" in result.stderr

    after = kms.rpc("ListAliases", {"KeyId": key_id})
    after_aliases = {
        (alias["AliasName"], alias.get("TargetKeyId"))
        for alias in after["Aliases"]
    }
    assert after_aliases == before_aliases
    assert (alias_name, key_id) in after_aliases