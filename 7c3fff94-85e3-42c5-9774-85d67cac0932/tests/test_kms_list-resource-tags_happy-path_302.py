def test_list_resource_tags_returns_tags_for_key(cli, kms):
    import json

    created = kms.rpc("CreateKey", {"Description": "list-resource-tags test"})
    key_id = created["KeyMetadata"]["KeyId"]

    expected_tag = {"TagKey": "environment", "TagValue": "test"}
    kms.rpc("TagResource", {"KeyId": key_id, "Tags": [expected_tag]})

    result = cli("kms", "list-resource-tags", "--key-id", key_id)

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert expected_tag in output["Tags"]

    state = kms.rpc("ListResourceTags", {"KeyId": key_id})
    assert expected_tag in state["Tags"]