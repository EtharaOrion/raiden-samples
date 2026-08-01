def test_user_pool_dates_are_iso8601(cli, cognito):
    import datetime
    import json
    import uuid

    name = "pool-dates-" + uuid.uuid4().hex[:8]
    pool_id = cognito.rpc("CreateUserPool", {"PoolName": name})["UserPool"]["Id"]

    result = cli("cognito-idp", "describe-user-pool", "--user-pool-id", pool_id)
    assert result.returncode == 0, result.stderr

    pool = json.loads(result.stdout)["UserPool"]
    for field in ("CreationDate", "LastModifiedDate"):
        value = pool[field]
        assert isinstance(value, str), (field, value)
        parsed = datetime.datetime.fromisoformat(value)
        assert parsed.tzinfo is not None, (field, value)
