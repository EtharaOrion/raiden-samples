def test_list_users_nonexistent_pool_not_found(cli, cognito):
    # Reference a user pool that does not exist -> ResourceNotFoundException
    missing_pool_id = "local_doesnotexist999"

    # Sanity: ensure this pool id is not present in the listing
    listed = cognito.rpc("ListUserPools", {"MaxResults": 60})
    existing_ids = {p["Id"] for p in listed.get("UserPools", [])}
    assert missing_pool_id not in existing_ids

    result = cli("cognito-idp", "list-users", "--user-pool-id", missing_pool_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Confirm the pool still does not exist in service state
    listed_after = cognito.rpc("ListUserPools", {"MaxResults": 60})
    ids_after = {p["Id"] for p in listed_after.get("UserPools", [])}
    assert missing_pool_id not in ids_after