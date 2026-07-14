from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deletetable_removed_from_listtables(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf_DelTbl1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    assert "Wf_DelTbl1" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "delete-table", "--table-name", "Wf_DelTbl1")
    assert result.returncode == 0
    assert "Wf_DelTbl1" not in ddb_client.list_tables()["TableNames"]
