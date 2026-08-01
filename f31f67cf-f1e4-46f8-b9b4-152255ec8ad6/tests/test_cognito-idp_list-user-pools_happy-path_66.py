def test_list_user_pools_happy_path(cli, cognito, tmp_path):
    import json

    pool_name = f"list-pools-{tmp_path.name}"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "list-user-pools",
        "--max-results",
        "60",
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert any(
        pool["Id"] == pool_id and pool["Name"] == pool_name
        for pool in output["UserPools"]
    )

    actual = cognito.rpc("ListUserPools", {"MaxResults": 60})
    assert any(
        pool["Id"] == pool_id and pool["Name"] == pool_name
        for pool in actual["UserPools"]
    )