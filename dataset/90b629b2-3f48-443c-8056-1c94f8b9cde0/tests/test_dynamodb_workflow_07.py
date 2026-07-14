from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_missing_table_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf8Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "delete-table", "--table-name", "WfNoSuch8")
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    assert "Wf8Tbl" in ddb_client.list_tables()["TableNames"]
