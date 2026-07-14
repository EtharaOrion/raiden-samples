from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deletetable_missing_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="TblKeep1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "delete-table", "--table-name", "NoSuchTblDel1")
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    assert "TblKeep1" in ddb_client.list_tables()["TableNames"]
