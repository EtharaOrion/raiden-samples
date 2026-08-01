def test_get_group_happy_path(cli, cognito):
    import json
    import uuid

    suffix = uuid.uuid4().hex
    pool = cognito.rpc("CreateUserPool", {"PoolName": f"get-group-pool-{suffix}"})
    pool_id = pool["UserPool"]["Id"]

    group_name = f"get-group-{suffix}"
    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": "Group retrieved by the CLI",
            "Precedence": 5,
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
    assert output["Group"]["Description"] == "Group retrieved by the CLI"
    assert output["Group"]["Precedence"] == 5

    groups = cognito.rpc("ListGroups", {"UserPoolId": pool_id})
    matching_groups = [
        group for group in groups["Groups"] if group["GroupName"] == group_name
    ]
    assert len(matching_groups) == 1
    assert matching_groups[0]["UserPoolId"] == pool_id
    assert matching_groups[0]["Description"] == "Group retrieved by the CLI"
    assert matching_groups[0]["Precedence"] == 5