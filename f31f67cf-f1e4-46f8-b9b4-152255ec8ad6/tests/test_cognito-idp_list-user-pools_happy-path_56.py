def test_list_user_pools_happy_path(cli, cognito):
    import json

    created = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "list-user-pools-happy-path"},
    )["UserPool"]
    pool_id = created["Id"]

    result = cli(
        "cognito-idp",
        "list-user-pools",
        "--max-results",
        "60",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert "UserPools" in output
    assert any(
        pool["Id"] == pool_id
        and pool["Name"] == "list-user-pools-happy-path"
        for pool in output["UserPools"]
    )

    actual_pools = cognito.rpc("ListUserPools", {"MaxResults": 60})["UserPools"]
    assert any(
        pool["Id"] == pool_id
        and pool["Name"] == "list-user-pools-happy-path"
        for pool in actual_pools
    )