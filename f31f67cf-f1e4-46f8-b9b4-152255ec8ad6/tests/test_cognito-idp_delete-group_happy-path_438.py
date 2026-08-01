def test_delete_group_removes_existing_group(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "delete-group-test-pool"})
    user_pool_id = pool["UserPool"]["Id"]
    group_name = "group-to-delete"

    created = cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": user_pool_id,
            "GroupName": group_name,
            "Description": "Group created for deletion",
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