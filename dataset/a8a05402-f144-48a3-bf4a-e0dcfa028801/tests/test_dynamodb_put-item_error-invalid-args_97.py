from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_conditional_check_failure(cli, ddb_client):
    ddb_client.create_table(
        TableName="Tbl1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName="Tbl1",
        Item={"pk": {"S": "abc"}, "n": {"N": "5"}},
    )

    result = cli(
        "dynamodb", "put-item",
        "--table-name", "Tbl1",
        "--item", '{"pk":{"S":"abc"},"n":{"N":"99"}}',
        "--condition-expression", "attribute_not_exists(pk)",
    )

    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr

    resp = ddb_client.get_item(TableName="Tbl1", Key={"pk": {"S": "abc"}})
    assert resp.get("Item") is not None
    assert resp["Item"]["n"]["N"] == "5"