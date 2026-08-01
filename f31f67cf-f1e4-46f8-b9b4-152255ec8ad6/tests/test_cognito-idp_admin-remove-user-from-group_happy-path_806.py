def test_admin_remove_user_from_group_happy_path(cli, cognito):
    import uuid

    pool_name = f"arufg-{uuid.uuid4().hex}"
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
        {"UserPoolId": pool_id, "Username": uid, "GroupName": group_name},
    )

    before = cognito.rpc(
        "AdminListGroupsForUser",
        {"UserPoolId": pool_id, "Username": uid},
    ).get("Groups", [])
    assert any(g["GroupName"] == group_name for g in before)

    result = cli(
        "cognito-idp",
        "admin-remove-user-from-group",
        "--user-pool-id",
        pool_id,
        "--username",
        uid,
        "--group-name",
        group_name,
    )
    assert result.returncode == 0, result.stderr

    after = cognito.rpc(
        "AdminListGroupsForUser",
        {"UserPoolId": pool_id, "Username": uid},
    ).get("Groups", [])
    assert all(g["GroupName"] != group_name for g in after)

    users_in_group = cognito.rpc(
        "ListUsersInGroup",
        {"UserPoolId": pool_id, "GroupName": group_name},
    ).get("Users", [])
    assert all(u["Username"] != uid for u in users_in_group)
