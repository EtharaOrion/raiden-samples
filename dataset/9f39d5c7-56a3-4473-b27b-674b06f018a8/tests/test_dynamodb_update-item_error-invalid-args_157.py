from _ddb_http import to_item, from_item, to_av, from_av


def test_update_item_missing_required_update_causes_error(cli, ddb_client):
    table = "UpdItemErrTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "a"}, "n": {"N": "1"}},
    )

    long_name = "x" * 500
    result = cli(
        "dynamodb", "update-item",
        "--table-name", long_name,
        "--key", '{"pk":{"S":"a"}}',
    )

    assert result.returncode != 0
    assert (
        "ValidationException" in result.stderr
        or "ResourceNotFoundException" in result.stderr
    )

    resp = ddb_client.get_item(TableName=table, Key={"pk": {"S": "a"}})
    assert resp.get("Item") is not None
    assert resp["Item"]["n"]["N"] == "1"