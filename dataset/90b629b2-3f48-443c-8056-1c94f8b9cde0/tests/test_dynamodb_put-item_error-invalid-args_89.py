from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_missing_required_item(cli, ddb_client):
    ddb_client.create_table(
        TableName="Tbl1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "put-item",
        "--table-name", "Tbl1",
        "--item", '{"pk":{"S":"nonexistent"}}',
        "--condition-expression", "attribute_exists(pk)",
    )
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Tbl1", Key={"pk": {"S": "nonexistent"}})
    assert resp.get("Item") is None