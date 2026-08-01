from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_list_reflects_deletions(cli, ddb_client, tmp_path):
    for nm in ("Wf53P", "Wf53Q"):
        ddb_client.create_table(
            TableName=nm,
            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
    rd1 = cli("dynamodb", "delete-table", "--table-name", "Wf53P")
    assert rd1.returncode == 0
    rd2 = cli("dynamodb", "delete-table", "--table-name", "Wf53Q")
    assert rd2.returncode == 0
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    names = set(ddb_client.list_tables()["TableNames"])
    assert "Wf53P" not in names and "Wf53Q" not in names
