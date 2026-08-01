def test_list_user_pools_happy_path(cli, cognito):
    import json

    created = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "pytest-list-user-pools"},
    )["UserPool"]
    pool_id = created["Id"]

    result = cli(
        "cognito-idp",
        "list-user-pools",
        "--max-results",
        "10",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert any(
        pool["Id"] == pool_id and pool["Name"] == "pytest-list-user-pools"
        for pool in output["UserPools"]
    )

    observed = cognito.rpc("ListUserPools", {"MaxResults": 10})
    assert any(
        pool["Id"] == pool_id and pool["Name"] == "pytest-list-user-pools"
        for pool in observed["UserPools"]
    )