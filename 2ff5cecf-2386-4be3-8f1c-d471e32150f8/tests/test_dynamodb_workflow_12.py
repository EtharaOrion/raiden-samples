from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_two_tables_delete_one(cli, ddb_client, tmp_path):
    for nm in ("Wf13A", "Wf13B"):
        ddb_client.create_table(
            TableName=nm,
            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
    result = cli("dynamodb", "delete-table", "--table-name", "Wf13A")
    assert result.returncode == 0
    names = set(ddb_client.list_tables()["TableNames"])
    assert "Wf13A" not in names
    assert "Wf13B" in names
