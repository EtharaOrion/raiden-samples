def test_list_resource_tags_rejects_empty_key_id(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "empty-key-id validation"})
    key_id = created["KeyMetadata"]["KeyId"]
    tag = {"TagKey": "purpose", "TagValue": "validation-state"}
    kms.rpc("TagResource", {"KeyId": key_id, "Tags": [tag]})

    result = cli("kms", "list-resource-tags", "--key-id", "")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Parameter validation" in result.stderr or "Invalid length" in result.stderr

    state = kms.rpc("ListResourceTags", {"KeyId": key_id})
    assert tag in state["Tags"]