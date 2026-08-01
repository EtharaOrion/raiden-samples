def test_admin_list_groups_for_user_happy_path(cli, cognito):
    import json
    import uuid

    pool_name = f"algfu-{uuid.uuid4().hex}"
    pool_id = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]["Id"]

    group_name = f"grp-{uuid.uuid4().hex[:8]}"
    cognito.rpc(
        "CreateGroup",
        {"UserPoolId": pool_id, "GroupName": group_name, "Description": "membership target"},
    )

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

    result = cli(
        "cognito-idp",
        "admin-list-groups-for-user",
        "--username",
        uid,
        "--user-pool-id",
        pool_id,
    )
    assert result.returncode == 0, result.stderr

    output = json.loads(result.stdout)
    assert any(g["GroupName"] == group_name for g in output.get("Groups", []))

    persisted = cognito.rpc(
        "AdminListGroupsForUser",
        {"UserPoolId": pool_id, "Username": uid},
    ).get("Groups", [])
    assert any(g["GroupName"] == group_name for g in persisted)
