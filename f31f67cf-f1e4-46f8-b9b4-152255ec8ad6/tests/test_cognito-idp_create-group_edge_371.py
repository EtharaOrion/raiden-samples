def test_create_group_special_character_name(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "create-group-special-character-test"},
    )["UserPool"]
    pool_id = pool["Id"]
    group_name = "<value>"

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