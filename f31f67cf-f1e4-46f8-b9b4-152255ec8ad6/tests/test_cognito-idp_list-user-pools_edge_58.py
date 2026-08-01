def test_list_user_pools_max_results_one(cli, cognito):
    import json

    created = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "list-user-pools-max-results-edge"},
    )["UserPool"]
    pool_id = created["Id"]

    result = cli(
        "cognito-idp",
        "list-user-pools",
        "--max-results",
        "1",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert "UserPools" in output
    assert any(
        pool["Id"] == pool_id
        and pool["Name"] == "list-user-pools-max-results-edge"
        for pool in output["UserPools"]
    )

    state = cognito.rpc("ListUserPools", {"MaxResults": 60})
    assert any(
        pool["Id"] == pool_id
        and pool["Name"] == "list-user-pools-max-results-edge"
        for pool in state["UserPools"]
    )