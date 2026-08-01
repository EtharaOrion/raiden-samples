def test_update_group_with_required_arguments_succeeds(cli, cognito):
    import json

    pool = cognito.rpc("CreateUserPool", {"PoolName": "update-group-pool"})
    user_pool_id = pool["UserPool"]["Id"]
    group_name = "string_v4"

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": user_pool_id,
            "GroupName": group_name,
            "Description": "existing group description",
            "Precedence": 4,
        },
    )

    result = cli(
        "cognito-idp",
        "update-group",
        "--group-name",
        group_name,
        "--user-pool-id",
        user_pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["Group"]["GroupName"] == group_name
    assert output["Group"]["UserPoolId"] == user_pool_id

    stored_group = cognito.rpc(
        "GetGroup",
        {
            "UserPoolId": user_pool_id,
            "GroupName": group_name,
        },
    )["Group"]
    assert stored_group["GroupName"] == group_name
    assert stored_group["UserPoolId"] == user_pool_id
    assert stored_group["Description"] == "existing group description"
    assert stored_group["Precedence"] == 4