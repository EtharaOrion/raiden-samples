def test_admin_add_user_to_group_happy_path(cli, cognito):
    import uuid

    pool_name = f"aautg-{uuid.uuid4().hex}"
    pool_id = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]["Id"]

    group_name = f"grp-{uuid.uuid4().hex[:8]}"
    cognito.rpc("CreateGroup", {"UserPoolId": pool_id, "GroupName": group_name})

    username = f"user-{uuid.uuid4().hex[:12]}@example.com"
    created = cognito.rpc(
        "AdminCreateUser",
        {"UserPoolId": pool_id, "Username": username, "MessageAction": "SUPPRESS"},
    )
    uid = created["User"]["Username"]

    result = cli(
        "cognito-idp",
        "admin-add-user-to-group",
        "--user-pool-id",
        pool_id,
        "--username",
        uid,
        "--group-name",
        group_name,
    )
    assert result.returncode == 0, result.stderr

    groups_for_user = cognito.rpc(
        "AdminListGroupsForUser",
        {"UserPoolId": pool_id, "Username": uid},
    ).get("Groups", [])
    assert any(g["GroupName"] == group_name for g in groups_for_user)

    users_in_group = cognito.rpc(
        "ListUsersInGroup",
        {"UserPoolId": pool_id, "GroupName": group_name},
    ).get("Users", [])
    assert any(u["Username"] == uid for u in users_in_group)
