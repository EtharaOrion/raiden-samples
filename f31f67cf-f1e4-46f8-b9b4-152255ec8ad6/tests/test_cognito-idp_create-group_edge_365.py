def test_create_group_max_length_name_succeeds(cli, cognito):
    group_name = "x" * 128
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "create-group-edge-test-pool"},
    )
    user_pool_id = pool["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "create-group",
        "--group-name",
        group_name,
        "--user-pool-id",
        user_pool_id,
    )

    assert result.returncode == 0, result.stderr

    created_group = cognito.rpc(
        "GetGroup",
        {
            "GroupName": group_name,
            "UserPoolId": user_pool_id,
        },
    )["Group"]
    assert created_group["GroupName"] == group_name
    assert created_group["UserPoolId"] == user_pool_id