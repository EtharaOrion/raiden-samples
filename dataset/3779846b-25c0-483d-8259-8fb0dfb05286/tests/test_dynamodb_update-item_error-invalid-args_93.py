from _ddb_http import to_item, from_item, to_av, from_av


def test_update_item_missing_required_update_causes_error(cli, ddb_client):
    table_name = "UpdateItemErrTbl"
    ddb_client.create_table(
        TableName=table_name,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName=table_name,
        Item={"pk": {"S": "item1"}, "v": {"S": "orig"}},
    )

    long_name = "x" * 600
    result = cli(
        "dynamodb", "update-item",
        "--table-name", long_name,
        "--key", '{"pk":{"S":"item1"}}',
    )

    assert result.returncode != 0
    assert (
        "ValidationException" in result.stderr
        or "ResourceNotFoundException" in result.stderr
    )

    resp = ddb_client.get_item(TableName=table_name, Key={"pk": {"S": "item1"}})
    assert resp.get("Item") is not None
    assert resp["Item"]["v"]["S"] == "orig"