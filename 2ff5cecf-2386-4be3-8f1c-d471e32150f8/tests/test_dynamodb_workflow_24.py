from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_twice_second_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf25Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "delete-table", "--table-name", "Wf25Tbl")
    assert result.returncode == 0
    result = cli("dynamodb", "delete-table", "--table-name", "Wf25Tbl")
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
