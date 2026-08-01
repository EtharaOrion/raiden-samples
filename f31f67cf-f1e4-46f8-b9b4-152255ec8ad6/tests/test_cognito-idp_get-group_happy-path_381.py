def test_get_group_happy_path(cli, cognito):
    import json

    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "get-group-happy-path-pool"},
    )["UserPool"]
    pool_id = pool["Id"]

    group_name = "test-readers"
    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": "Readers group",
            "Precedence": 10,
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
    assert output["Group"]["Description"] == "Readers group"
    assert output["Group"]["Precedence"] == 10

    stored_group = cognito.rpc(
        "GetGroup",
        {"UserPoolId": pool_id, "GroupName": group_name},
    )["Group"]
    assert stored_group["GroupName"] == group_name
    assert stored_group["UserPoolId"] == pool_id
    assert stored_group["Description"] == "Readers group"
    assert stored_group["Precedence"] == 10