def test_admin_create_user_happy_path(cli, cognito):
    import json
    import uuid

    pool_name = f"acu-{uuid.uuid4().hex}"
    pool_id = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]["Id"]

    username = f"user-{uuid.uuid4().hex[:12]}@example.com"
    result = cli(
        "cognito-idp",
        "admin-create-user",
        "--user-pool-id",
        pool_id,
        "--username",
        username,
        "--message-action",
        "SUPPRESS",
    )
    assert result.returncode == 0, result.stderr

    output = json.loads(result.stdout)
    uid = output["User"]["Username"]
    assert isinstance(uid, str) and uid

    fetched = cognito.rpc(
        "AdminGetUser",
        {"UserPoolId": pool_id, "Username": username},
    )
    assert fetched["Username"] == uid
    assert fetched["Enabled"] is True

    listed = cognito.rpc("ListUsers", {"UserPoolId": pool_id}).get("Users", [])
    assert any(u["Username"] == uid for u in listed)
