from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_multi_table_list_and_delete(cli, ddb_client, tmp_path):
    for nm in ("Wf40X", "Wf40Y", "Wf40Z"):
        ddb_client.create_table(
            TableName=nm,
            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    names = set(ddb_client.list_tables()["TableNames"])
    assert {"Wf40X", "Wf40Y", "Wf40Z"} <= names
    rd = cli("dynamodb", "delete-table", "--table-name", "Wf40Y")
    assert rd.returncode == 0
    names2 = set(ddb_client.list_tables()["TableNames"])
    assert "Wf40Y" not in names2
    assert "Wf40X" in names2 and "Wf40Z" in names2
