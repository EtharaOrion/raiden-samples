def test_list_groups_returns_existing_groups(cli, cognito, tmp_path):
    import json

    pool_name = "list-groups-" + tmp_path.name.replace("_", "-")
    pool = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]
    pool_id = pool["Id"]

    expected_groups = {
        "developers": {"Description": "Application developers", "Precedence": 10},
        "auditors": {"Description": "Read-only auditors", "Precedence": 20},
    }
    for group_name, details in expected_groups.items():
        cognito.rpc(
            "CreateGroup",
            {
                "UserPoolId": pool_id,
                "GroupName": group_name,
                "Description": details["Description"],
                "Precedence": details["Precedence"],
            },
        )

    result = cli(
        "cognito-idp",
        "list-groups",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    returned_groups = {group["GroupName"]: group for group in output["Groups"]}
    assert set(returned_groups) == set(expected_groups)
    for group_name, details in expected_groups.items():
        assert returned_groups[group_name]["Description"] == details["Description"]
        assert returned_groups[group_name]["Precedence"] == details["Precedence"]

    state = cognito.rpc("ListGroups", {"UserPoolId": pool_id})
    persisted_groups = {group["GroupName"]: group for group in state["Groups"]}
    assert set(expected_groups).issubset(persisted_groups)
    for group_name, details in expected_groups.items():
        assert persisted_groups[group_name]["Description"] == details["Description"]
        assert persisted_groups[group_name]["Precedence"] == details["Precedence"]