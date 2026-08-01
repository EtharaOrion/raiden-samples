def test_list_users_empty_user_pool_id_rejected(cli, cognito):
    # Establish a real, valid pool first so the failure is clearly due to the
    # empty --user-pool-id argument and not merely a missing environment.
    created = cognito.rpc("CreateUserPool", {"PoolName": "seed-pool-for-empty-id"})
    valid_pool_id = created["UserPool"]["Id"]

    # Sanity: the valid pool is usable via ListUsers through the raw client.
    listed = cognito.rpc("ListUsers", {"UserPoolId": valid_pool_id})
    assert isinstance(listed.get("Users", []), list)

    # Command under test: an empty user-pool-id must be rejected.
    result = cli("cognito-idp", "list-users", "--user-pool-id", "")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    stderr = result.stderr.lower()
    assert (
        "invalidparameter" in stderr
        or "resourcenotfound" in stderr
        or "validation" in stderr
    )

    # The valid pool remains untouched and still usable.
    still = cognito.rpc("ListUsers", {"UserPoolId": valid_pool_id})
    assert isinstance(still.get("Users", []), list)