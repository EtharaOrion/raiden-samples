def test_create_user_pool_missing_required_pool_name(cli, cognito):
    seeded = cognito.rpc("CreateUserPool", {"PoolName": "existing-pool"})
    seeded_pool = seeded["UserPool"]

    before = cognito.rpc("ListUserPools", {"MaxResults": 60})["UserPools"]
    before_ids = {pool["Id"] for pool in before}
    assert seeded_pool["Id"] in before_ids

    result = cli("cognito-idp", "create-user-pool")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()

    after = cognito.rpc("ListUserPools", {"MaxResults": 60})["UserPools"]
    assert {pool["Id"] for pool in after} == before_ids
    assert any(
        pool["Id"] == seeded_pool["Id"] and pool["Name"] == "existing-pool"
        for pool in after
    )