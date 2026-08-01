def test_admin_get_user_uses_user_attribute_key_names(cli, cognito):
    import datetime
    import json
    import uuid

    pool_id = cognito.rpc(
        "CreateUserPool", {"PoolName": "pool-adminget-" + uuid.uuid4().hex[:8]}
    )["UserPool"]["Id"]
    created = cognito.rpc(
        "AdminCreateUser",
        {"UserPoolId": pool_id,
         "Username": "user-%s@example.com" % uuid.uuid4().hex[:10],
         "MessageAction": "SUPPRESS"},
    )
    uid = created["User"]["Username"]

    result = cli("cognito-idp", "admin-get-user",
                 "--user-pool-id", pool_id, "--username", uid)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)

    # AdminGetUser reports attributes under UserAttributes; AdminCreateUser
    # reports the same data under Attributes.
    assert "UserAttributes" in out
    assert "Attributes" not in out

    assert out["Username"] == uid
    assert out["Enabled"] is True
    assert out["UserStatus"] == "FORCE_CHANGE_PASSWORD"
    for field in ("UserCreateDate", "UserLastModifiedDate"):
        parsed = datetime.datetime.fromisoformat(out[field])
        assert parsed.tzinfo is not None, (field, out[field])
