def test_create_group_happy_path(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "create-group-test-pool"})
    pool_id = pool["UserPool"]["Id"]
    group_name = "test-group"

    result = cli(
        "cognito-idp",
        "create-group",
        "--group-name",
        group_name,
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0

    group = cognito.rpc(
        "GetGroup",
        {
            "GroupName": group_name,
            "UserPoolId": pool_id,
        },
    )["Group"]
    assert group["GroupName"] == group_name
    assert group["UserPoolId"] == pool_id