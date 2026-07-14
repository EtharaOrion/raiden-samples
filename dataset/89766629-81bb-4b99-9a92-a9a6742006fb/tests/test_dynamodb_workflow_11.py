from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deletetable_then_getitem_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfDelGet",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfDelGet",
                 "--item", '{"pk":{"S":"k1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "delete-table", "--table-name", "WfDelGet")
    assert result.returncode == 0
    assert "WfDelGet" not in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "get-item", "--table-name", "WfDelGet",
                 "--key", '{"pk":{"S":"k1"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
