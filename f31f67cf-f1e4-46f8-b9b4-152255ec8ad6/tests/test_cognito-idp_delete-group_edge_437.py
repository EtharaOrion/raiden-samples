def test_delete_group_max_length_name(cli, cognito):
    group_name = "x" * 128

    pool = cognito.rpc("CreateUserPool", {"PoolName": "delete-group-edge-pool"})
    user_pool_id = pool["UserPool"]["Id"]

    created = cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": user_pool_id,
            "GroupName": group_name,
        },
    )
    assert created["Group"]["GroupName"] == group_name
    assert created["Group"]["UserPoolId"] == user_pool_id

    result = cli(
        "cognito-idp",
        "delete-group",
        "--group-name",
        group_name,
        "--user-pool-id",
        user_pool_id,
    )
    assert result.returncode == 0

    groups = cognito.rpc("ListGroups", {"UserPoolId": user_pool_id})
    assert group_name not in {group["GroupName"] for group in groups["Groups"]}