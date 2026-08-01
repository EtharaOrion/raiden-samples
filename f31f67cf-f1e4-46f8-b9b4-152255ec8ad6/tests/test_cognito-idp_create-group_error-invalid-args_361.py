def test_create_group_missing_required_group_name(cli, cognito, tmp_path):
    pool_name = f"missing-group-name-{tmp_path.name}"
    pool = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]
    pool_id = pool["Id"]

    sentinel_group = "existing-group"
    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": sentinel_group,
        },
    )

    before = cognito.rpc("ListGroups", {"UserPoolId": pool_id})
    assert {group["GroupName"] for group in before["Groups"]} == {sentinel_group}

    result = cli(
        "cognito-idp",
        "create-group",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--group-name" in result.stderr

    after = cognito.rpc("ListGroups", {"UserPoolId": pool_id})
    assert {group["GroupName"] for group in after["Groups"]} == {sentinel_group}