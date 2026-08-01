def test_update_group_happy_path(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "update-group-happy-path-pool"},
    )["UserPool"]
    pool_id = pool["Id"]
    group_name = "engineering"

    created_group = cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": "Existing group description",
            "Precedence": 7,
        },
    )["Group"]
    assert created_group["GroupName"] == group_name
    assert created_group["UserPoolId"] == pool_id

    result = cli(
        "cognito-idp",
        "update-group",
        "--group-name",
        group_name,
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0

    updated_group = cognito.rpc(
        "GetGroup",
        {"UserPoolId": pool_id, "GroupName": group_name},
    )["Group"]
    assert updated_group["GroupName"] == group_name
    assert updated_group["UserPoolId"] == pool_id
    assert updated_group["Description"] == "Existing group description"
    assert updated_group["Precedence"] == 7