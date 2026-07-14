from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_item_missing_table(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf4Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "get-item", "--table-name", "WfNoSuch4",
                 "--key", '{"pk":{"S":"x"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
