def test_list_keys_entries_carry_key_arn(cli, kms):
    import json
    import re

    created = kms.rpc("CreateKey", {"Description": "list-arn-shape"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "list-keys", "--limit", "1000")
    assert result.returncode == 0, result.stderr

    keys = json.loads(result.stdout)["Keys"]
    assert keys
    for entry in keys:
        assert re.fullmatch(
            r"arn:aws:kms:[a-z0-9-]+:\d{12}:key/" + re.escape(entry["KeyId"]),
            entry["KeyArn"],
        )

    match = [k for k in keys if k["KeyId"] == key_id]
    assert len(match) == 1
