def test_list_users_in_group_happy_path(cli, cognito):
    import json
    import uuid

    pool_name = f"luig-{uuid.uuid4().hex}"
    pool_id = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]["Id"]

    group_name = f"grp-{uuid.uuid4().hex[:8]}"
    cognito.rpc("CreateGroup", {"UserPoolId": pool_id, "GroupName": group_name})

    username = f"user-{uuid.uuid4().hex[:12]}@example.com"
    created = cognito.rpc(
        "AdminCreateUser",
        {"UserPoolId": pool_id, "Username": username, "MessageAction": "SUPPRESS"},
    )
    uid = created["User"]["Username"]
    cognito.rpc(
        "AdminAddUserToGroup",
        {"UserPoolId": pool_id, "Username": username, "GroupName": group_name},
    )

    result = cli(
        "cognito-idp",
        "list-users-in-group",
        "--user-pool-id",
        pool_id,
        "--group-name",
        group_name,
    )
    assert result.returncode == 0, result.stderr

    output = json.loads(result.stdout)
    assert any(u["Username"] == uid for u in output.get("Users", []))

    persisted = cognito.rpc(
        "ListUsersInGroup",
        {"UserPoolId": pool_id, "GroupName": group_name},
    ).get("Users", [])
    assert any(u["Username"] == uid for u in persisted)
