def test_list_keys_includes_created_key(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "list-keys-test"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "list-keys")
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    assert "Keys" in payload
    listed_ids = {k["KeyId"] for k in payload["Keys"]}
    assert key_id in listed_ids

    # Confirm the listed key is real via an independent read
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id