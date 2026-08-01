def test_admin_get_user_happy_path(cli, cognito):
    import json
    import uuid

    pool_name = f"agu-{uuid.uuid4().hex}"
    pool_id = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]["Id"]

    username = f"user-{uuid.uuid4().hex[:12]}@example.com"
    created = cognito.rpc(
        "AdminCreateUser",
        {"UserPoolId": pool_id, "Username": username, "MessageAction": "SUPPRESS"},
    )
    uid = created["User"]["Username"]

    result = cli(
        "cognito-idp",
        "admin-get-user",
        "--user-pool-id",
        pool_id,
        "--username",
        username,
    )
    assert result.returncode == 0, result.stderr

    output = json.loads(result.stdout)
    assert output["Username"] == uid
    assert output["Enabled"] is True

    persisted = cognito.rpc(
        "AdminGetUser",
        {"UserPoolId": pool_id, "Username": username},
    )
    assert persisted["Username"] == uid
    assert persisted["Enabled"] is True
