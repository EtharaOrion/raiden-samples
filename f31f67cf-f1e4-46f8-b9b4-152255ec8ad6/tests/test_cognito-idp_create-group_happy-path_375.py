def test_create_group_happy_path(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "create-group-test-pool"})
    user_pool_id = pool["UserPool"]["Id"]
    group_name = "string_v4"

    result = cli(
        "cognito-idp",
        "create-group",
        "--group-name",
        group_name,
        "--user-pool-id",
        user_pool_id,
    )

    assert result.returncode == 0

    group = cognito.rpc(
        "GetGroup",
        {"GroupName": group_name, "UserPoolId": user_pool_id},
    )["Group"]
    assert group["GroupName"] == group_name
    assert group["UserPoolId"] == user_pool_id