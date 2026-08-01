def test_update_group_sets_zero_precedence(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "update-group-zero-precedence-pool"},
    )["UserPool"]
    pool_id = pool["Id"]
    group_name = "zero-precedence-group"

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Precedence": 7,
        },
    )

    result = cli(
        "cognito-idp",
        "update-group",
        "--group-name",
        group_name,
        "--user-pool-id",
        pool_id,
        "--precedence",
        "0",
    )

    assert result.returncode == 0

    updated_group = cognito.rpc(
        "GetGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
        },
    )["Group"]
    assert updated_group["GroupName"] == group_name
    assert updated_group["UserPoolId"] == pool_id
    assert updated_group["Precedence"] == 0