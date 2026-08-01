def test_get_group_happy_path(cli, cognito, tmp_path):
    import json

    pool_name = f"pool-{tmp_path.name}"
    group_name = "test-group"
    description = "Group retrieved by get-group"

    pool = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]
    pool_id = pool["Id"]

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": description,
            "Precedence": 7,
        },
    )

    result = cli(
        "cognito-idp",
        "get-group",
        "--group-name",
        group_name,
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["Group"]["GroupName"] == group_name
    assert output["Group"]["UserPoolId"] == pool_id
    assert output["Group"]["Description"] == description
    assert output["Group"]["Precedence"] == 7

    stored_group = cognito.rpc(
        "GetGroup",
        {"UserPoolId": pool_id, "GroupName": group_name},
    )["Group"]
    assert stored_group["GroupName"] == group_name
    assert stored_group["UserPoolId"] == pool_id
    assert stored_group["Description"] == description
    assert stored_group["Precedence"] == 7