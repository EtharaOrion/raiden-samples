def test_describe_key_creation_date_is_iso8601(cli, kms):
    import datetime
    import json

    created = kms.rpc("CreateKey", {"Description": "creation-date-format"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "describe-key", "--key-id", key_id)
    assert result.returncode == 0, result.stderr

    raw = json.loads(result.stdout)["KeyMetadata"]["CreationDate"]

    # The CLI renders the service's numeric timestamp as an ISO-8601 string.
    assert isinstance(raw, str), raw
    parsed = datetime.datetime.fromisoformat(raw)
    assert parsed.tzinfo is not None, raw

    epoch = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]["CreationDate"]
    assert abs(parsed.timestamp() - float(epoch)) < 2
