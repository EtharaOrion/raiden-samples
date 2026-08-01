def test_create_group_happy_path(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "create-group-happy-path-pool"},
    )["UserPool"]
    pool_id = pool["Id"]
    group_name = "test-group-v3"

    result = cli(
        "cognito-idp",
        "create-group",
        "--group-name",
        group_name,
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0, result.stderr

    group = cognito.rpc(
        "GetGroup",
        {
            "GroupName": group_name,
            "UserPoolId": pool_id,
        },
    )["Group"]
    assert group["GroupName"] == group_name
    assert group["UserPoolId"] == pool_id