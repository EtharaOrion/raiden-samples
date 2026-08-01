from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_missing_then_valid(cli, ddb_client, tmp_path):
    rd = cli("dynamodb", "delete-table", "--table-name", "Wf71Ghost")
    assert rd.returncode != 0
    assert "ResourceNotFoundException" in rd.stderr
    ddb_client.create_table(
        TableName="Wf71Real",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    rd2 = cli("dynamodb", "delete-table", "--table-name", "Wf71Real")
    assert rd2.returncode == 0
    assert "Wf71Real" not in ddb_client.list_tables()["TableNames"]
