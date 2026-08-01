def test_list_keys_happy_path_includes_created_keys(cli, kms):
    import json
    import uuid

    suffix = uuid.uuid4().hex
    first = kms.rpc("CreateKey", {"Description": "list-keys-a-" + suffix})
    second = kms.rpc("CreateKey", {"Description": "list-keys-b-" + suffix})
    first_id = first["KeyMetadata"]["KeyId"]
    second_id = second["KeyMetadata"]["KeyId"]

    result = cli("kms", "list-keys")
    assert result.returncode == 0, result.stderr

    output = json.loads(result.stdout)
    assert isinstance(output["Keys"], list)
    listed_ids = {key["KeyId"] for key in output["Keys"]}
    assert first_id in listed_ids
    assert second_id in listed_ids
