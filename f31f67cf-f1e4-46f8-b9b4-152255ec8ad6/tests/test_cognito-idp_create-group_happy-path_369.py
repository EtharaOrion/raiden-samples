def test_create_group_happy_path(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "create-group-happy-path-pool"},
    )["UserPool"]
    pool_id = pool["Id"]
    group_name = "string_v2"

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
            "UserPoolId": pool_id,
            "GroupName": group_name,
        },
    )["Group"]
    assert group["GroupName"] == group_name
    assert group["UserPoolId"] == pool_id