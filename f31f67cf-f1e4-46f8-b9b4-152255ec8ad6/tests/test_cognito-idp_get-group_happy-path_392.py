def test_get_group_happy_path(cli, cognito, tmp_path):
    import json
    import uuid

    suffix = uuid.uuid4().hex[:12]
    pool_name = f"get-group-pool-{suffix}"
    group_name = f"get-group-{suffix}"

    pool = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]
    user_pool_id = pool["Id"]

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": user_pool_id,
            "GroupName": group_name,
            "Description": "Group used to test get-group",
            "Precedence": 7,
        },
    )

    result = cli(
        "cognito-idp",
        "get-group",
        "--group-name",
        group_name,
        "--user-pool-id",
        user_pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["Group"]["GroupName"] == group_name
    assert output["Group"]["UserPoolId"] == user_pool_id
    assert output["Group"]["Description"] == "Group used to test get-group"
    assert output["Group"]["Precedence"] == 7

    stored_group = cognito.rpc(
        "GetGroup",
        {"UserPoolId": user_pool_id, "GroupName": group_name},
    )["Group"]
    assert stored_group["GroupName"] == group_name
    assert stored_group["UserPoolId"] == user_pool_id
    assert stored_group["Description"] == "Group used to test get-group"
    assert stored_group["Precedence"] == 7