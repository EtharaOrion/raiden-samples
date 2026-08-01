def test_delete_group_happy_path(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "delete-group-test-pool"})["UserPool"]
    pool_id = pool["Id"]
    group_name = "group-to-delete"

    created = cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": "Temporary test group",
        },
    )["Group"]
    assert created["GroupName"] == group_name
    assert created["UserPoolId"] == pool_id

    result = cli(
        "cognito-idp",
        "delete-group",
        "--group-name",
        group_name,
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0

    groups = cognito.rpc("ListGroups", {"UserPoolId": pool_id})["Groups"]
    assert all(group["GroupName"] != group_name for group in groups)