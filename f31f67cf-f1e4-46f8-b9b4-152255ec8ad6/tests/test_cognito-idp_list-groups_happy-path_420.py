def test_list_groups_happy_path(cli, cognito):
    import json

    pool_name = "list-groups-happy-path"
    pool = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]
    pool_id = pool["Id"]

    expected_groups = {
        "developers": {"Description": "Development team", "Precedence": 10},
        "operators": {"Description": "Operations team", "Precedence": 20},
    }
    for group_name, details in expected_groups.items():
        cognito.rpc(
            "CreateGroup",
            {
                "UserPoolId": pool_id,
                "GroupName": group_name,
                **details,
            },
        )

    result = cli(
        "cognito-idp",
        "list-groups",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert {group["GroupName"] for group in output["Groups"]} == set(expected_groups)

    described_pool = cognito.rpc(
        "DescribeUserPool",
        {"UserPoolId": pool_id},
    )["UserPool"]
    assert described_pool["Name"] == pool_name

    stored_groups = cognito.rpc("ListGroups", {"UserPoolId": pool_id})["Groups"]
    stored_by_name = {group["GroupName"]: group for group in stored_groups}
    assert set(stored_by_name) == set(expected_groups)
    for group_name, details in expected_groups.items():
        assert stored_by_name[group_name]["UserPoolId"] == pool_id
        assert stored_by_name[group_name]["Description"] == details["Description"]
        assert stored_by_name[group_name]["Precedence"] == details["Precedence"]