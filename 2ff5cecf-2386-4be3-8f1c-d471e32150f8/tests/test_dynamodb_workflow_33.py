from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_negative_get_then_valid(cli, ddb_client, tmp_path):
    result = cli(
        "dynamodb", "get-item", "--table-name", "Wf34Missing",
        "--key", '{"pk":{"S":"a"}}',
    )
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    ddb_client.create_table(
        TableName="Wf34Real",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf34Real", Item={"pk": {"S": "a"}})
    result = cli(
        "dynamodb", "get-item", "--table-name", "Wf34Real",
        "--key", '{"pk":{"S":"a"}}',
    )
    assert result.returncode == 0
