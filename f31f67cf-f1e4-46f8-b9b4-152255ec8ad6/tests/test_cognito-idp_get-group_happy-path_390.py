def test_get_group_happy_path(cli, cognito):
    import json
    import uuid

    suffix = uuid.uuid4().hex
    pool = cognito.rpc("CreateUserPool", {"PoolName": f"get-group-pool-{suffix}"})
    pool_id = pool["UserPool"]["Id"]

    group_name = f"get-group-{suffix}"
    description = "Group retrieved by the CLI"
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

    observed = cognito.rpc(
        "GetGroup",
        {"UserPoolId": pool_id, "GroupName": group_name},
    )["Group"]
    assert observed["GroupName"] == group_name
    assert observed["UserPoolId"] == pool_id
    assert observed["Description"] == description
    assert observed["Precedence"] == 7