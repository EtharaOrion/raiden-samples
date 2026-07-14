from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_reserved_word_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfUpd3",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="WfUpd3", Item={"pk": {"S": "a"}})
    result = cli(
        "dynamodb", "update-item",
        "--table-name", "WfUpd3",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET Status = :v",
        "--expression-attribute-values", '{":v":{"S":"active"}}',
    )
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
