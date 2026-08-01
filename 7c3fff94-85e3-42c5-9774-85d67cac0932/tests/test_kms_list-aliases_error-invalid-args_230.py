def test_list_aliases_rejects_empty_marker(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "empty marker validation"})
    key_id = key["KeyMetadata"]["KeyId"]
    alias_name = "alias/list-aliases-empty-marker"
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    before = kms.rpc("ListAliases", {})["Aliases"]
    assert any(
        alias["AliasName"] == alias_name and alias.get("TargetKeyId") == key_id
        for alias in before
    )

    result = cli("kms", "list-aliases", "--marker", "")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert (
        "Invalid length" in result.stderr
        or "Parameter validation failed" in result.stderr
        or "InvalidMarkerException" in result.stderr
    )

    after = kms.rpc("ListAliases", {})["Aliases"]
    assert any(
        alias["AliasName"] == alias_name and alias.get("TargetKeyId") == key_id
        for alias in after
    )
    assert {
        (alias["AliasName"], alias.get("TargetKeyId")) for alias in after
    } == {
        (alias["AliasName"], alias.get("TargetKeyId")) for alias in before
    }