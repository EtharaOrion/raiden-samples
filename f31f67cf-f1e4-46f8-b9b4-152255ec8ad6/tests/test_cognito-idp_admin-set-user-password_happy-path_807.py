def test_admin_set_user_password_happy_path(cli, cognito):
    import uuid

    pool_name = f"asup-{uuid.uuid4().hex}"
    pool_id = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]["Id"]

    username = f"user-{uuid.uuid4().hex[:12]}@example.com"
    created = cognito.rpc(
        "AdminCreateUser",
        {"UserPoolId": pool_id, "Username": username, "MessageAction": "SUPPRESS"},
    )
    uid = created["User"]["Username"]

    result = cli(
        "cognito-idp",
        "admin-set-user-password",
        "--user-pool-id",
        pool_id,
        "--username",
        username,
        "--password",
        "NewP@ssw0rd!123",
        "--permanent",
    )
    assert result.returncode == 0, result.stderr

    after = cognito.rpc(
        "AdminGetUser",
        {"UserPoolId": pool_id, "Username": username},
    )
    assert after["Username"] == uid
    assert after["UserStatus"] == "CONFIRMED"
