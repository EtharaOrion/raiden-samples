def test_list_groups_missing_user_pool_id(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "list-groups-invalid-args-pool"})
    pool_id = pool["UserPool"]["Id"]

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": "existing-group",
            "Description": "Group that must remain unchanged",
        },
    )

    result = cli("cognito-idp", "list-groups")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()

    groups = cognito.rpc("ListGroups", {"UserPoolId": pool_id})["Groups"]
    assert any(
        group["GroupName"] == "existing-group"
        and group["UserPoolId"] == pool_id
        and group["Description"] == "Group that must remain unchanged"
        for group in groups
    )