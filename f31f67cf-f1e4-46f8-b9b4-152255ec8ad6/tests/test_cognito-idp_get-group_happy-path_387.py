def test_get_group_happy_path(cli, cognito):
    import json
    import uuid

    suffix = uuid.uuid4().hex
    pool_name = f"get-group-pool-{suffix}"
    group_name = f"get-group-{suffix}"

    pool = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]
    pool_id = pool["Id"]

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
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
        pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["Group"]["GroupName"] == group_name
    assert output["Group"]["UserPoolId"] == pool_id
    assert output["Group"]["Description"] == "Group used to test get-group"
    assert output["Group"]["Precedence"] == 7

    stored_group = cognito.rpc(
        "GetGroup",
        {"UserPoolId": pool_id, "GroupName": group_name},
    )["Group"]
    assert stored_group["GroupName"] == group_name
    assert stored_group["UserPoolId"] == pool_id
    assert stored_group["Description"] == "Group used to test get-group"
    assert stored_group["Precedence"] == 7