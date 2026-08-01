def test_update_group_rejects_empty_group_name(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "update-group-invalid-args-pool"})
    pool_id = pool["UserPool"]["Id"]

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": "existing-group",
            "Description": "original description",
        },
    )

    result = cli(
        "cognito-idp",
        "update-group",
        "--group-name",
        "",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Invalid length" in result.stderr

    group = cognito.rpc(
        "GetGroup",
        {"UserPoolId": pool_id, "GroupName": "existing-group"},
    )["Group"]
    assert group["GroupName"] == "existing-group"
    assert group["Description"] == "original description"

    groups = cognito.rpc("ListGroups", {"UserPoolId": pool_id})["Groups"]
    assert {item["GroupName"] for item in groups} == {"existing-group"}