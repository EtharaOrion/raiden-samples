def test_list_groups_happy_path(cli, cognito):
    import json
    import uuid

    suffix = uuid.uuid4().hex[:12]
    pool = cognito.rpc("CreateUserPool", {"PoolName": f"list-groups-{suffix}"})["UserPool"]
    pool_id = pool["Id"]

    expected_groups = {
        f"admins-{suffix}": "Administrative users",
        f"auditors-{suffix}": "Read-only auditors",
    }
    for precedence, (group_name, description) in enumerate(expected_groups.items(), start=1):
        cognito.rpc(
            "CreateGroup",
            {
                "UserPoolId": pool_id,
                "GroupName": group_name,
                "Description": description,
                "Precedence": precedence,
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
    output_groups = {
        group["GroupName"]: group.get("Description")
        for group in output["Groups"]
    }
    assert output_groups == expected_groups

    stored = cognito.rpc("ListGroups", {"UserPoolId": pool_id})
    stored_groups = {
        group["GroupName"]: group.get("Description")
        for group in stored["Groups"]
    }
    assert stored_groups == expected_groups