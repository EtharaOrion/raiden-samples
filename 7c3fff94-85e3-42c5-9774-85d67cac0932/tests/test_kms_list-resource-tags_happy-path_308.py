def test_list_resource_tags_returns_key_tags(cli, kms):
    import json

    created = kms.rpc(
        "CreateKey",
        {"Description": "list-resource-tags happy path"},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    expected_tag = {
        "TagKey": "Environment",
        "TagValue": "integration-test",
    }
    kms.rpc("TagResource", {"KeyId": key_id, "Tags": [expected_tag]})

    result = cli("kms", "list-resource-tags", "--key-id", key_id)

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert expected_tag in output["Tags"]

    resulting_state = kms.rpc("ListResourceTags", {"KeyId": key_id})
    assert expected_tag in resulting_state["Tags"]