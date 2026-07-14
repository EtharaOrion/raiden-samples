from _ddb_http import to_item, from_item, to_av, from_av


def test_update_item_missing_update_arguments(cli, ddb_client):
    ddb_client.create_table(
        TableName="Tbl1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName="Tbl1",
        Item={"pk": {"S": "abc"}, "n": {"N": "1"}},
    )
    result = cli(
        "dynamodb",
        "update-item",
        "--table-name",
        "Tbl1",
        "--key",
        '{"pk":{"S":"abc"}}',
        "--update-expression",
        "SET n = :v",
        "--condition-expression",
        "attribute_exists(missingattr)",
        "--expression-attribute-values",
        '{":v":{"N":"99"}}',
    )
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Tbl1", Key={"pk": {"S": "abc"}})
    assert resp.get("Item") is not None
    assert resp["Item"]["n"]["N"] == "1"