def test_list_users_happy_path(cli, cognito):
    import json
    import uuid

    pool_name = f"lu-{uuid.uuid4().hex}"
    pool_id = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]["Id"]

    username = f"user-{uuid.uuid4().hex[:12]}@example.com"
    created = cognito.rpc(
        "AdminCreateUser",
        {"UserPoolId": pool_id, "Username": username, "MessageAction": "SUPPRESS"},
    )
    uid = created["User"]["Username"]

    result = cli(
        "cognito-idp",
        "list-users",
        "--user-pool-id",
        pool_id,
    )
    assert result.returncode == 0, result.stderr

    output = json.loads(result.stdout)
    assert any(u["Username"] == uid for u in output.get("Users", []))

    persisted = cognito.rpc("ListUsers", {"UserPoolId": pool_id}).get("Users", [])
    assert any(u["Username"] == uid for u in persisted)
