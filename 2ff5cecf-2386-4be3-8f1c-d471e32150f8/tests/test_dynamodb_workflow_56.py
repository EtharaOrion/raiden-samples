from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_all_empty_list(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf57Only",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    rd = cli("dynamodb", "delete-table", "--table-name", "Wf57Only")
    assert rd.returncode == 0
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    assert "Wf57Only" not in ddb_client.list_tables()["TableNames"]
