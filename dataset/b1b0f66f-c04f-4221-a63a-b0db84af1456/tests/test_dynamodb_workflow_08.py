from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_item_reserved_word_fails(cli, ddb_client):
    ddb_client.create_table(
        TableName="WFReserved",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="WFReserved", Item={"pk": {"S": "r1"}, "Status": {"S": "old"}})
    result = cli(
        "dynamodb", "update-item",
        "--table-name", "WFReserved",
        "--key", '{"pk":{"S":"r1"}}',
        "--update-expression", "SET Status = :v",
        "--expression-attribute-values", '{":v":{"S":"new"}}',
    )
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
    from _ddb_http import from_item
    resp = ddb_client.get_item(TableName="WFReserved", Key={"pk": {"S": "r1"}}, ConsistentRead=True)
    assert from_item(resp["Item"])["Status"] == "old"
