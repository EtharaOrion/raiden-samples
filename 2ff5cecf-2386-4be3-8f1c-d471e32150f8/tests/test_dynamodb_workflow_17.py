from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_recreate_empty(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf18Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf18Tbl", Item={"pk": {"S": "a"}})
    result = cli("dynamodb", "delete-table", "--table-name", "Wf18Tbl")
    assert result.returncode == 0
    assert "Wf18Tbl" not in ddb_client.list_tables()["TableNames"]
