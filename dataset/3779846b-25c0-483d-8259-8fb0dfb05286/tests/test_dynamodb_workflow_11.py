from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_then_delete_then_query(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfMix1",
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ],
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="WfMix1", Item={"pk": {"S": "g"}, "sk": {"S": "1"}})
    ddb_client.put_item(TableName="WfMix1", Item={"pk": {"S": "g"}, "sk": {"S": "2"}})
    upd = cli(
        "dynamodb", "update-item",
        "--table-name", "WfMix1",
        "--key", '{"pk":{"S":"g"},"sk":{"S":"1"}}',
        "--update-expression", "SET tag = :t",
        "--expression-attribute-values", '{":t":{"S":"kept"}}',
    )
    assert upd.returncode == 0
    dl = cli(
        "dynamodb", "delete-item",
        "--table-name", "WfMix1",
        "--key", '{"pk":{"S":"g"},"sk":{"S":"2"}}',
    )
    assert dl.returncode == 0
    q = cli(
        "dynamodb", "query",
        "--table-name", "WfMix1",
        "--key-condition-expression", "pk = :v",
        "--expression-attribute-values", '{":v":{"S":"g"}}',
    )
    assert q.returncode == 0
    resp = ddb_client.query(
        TableName="WfMix1",
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "g"}},
    )
    items = [from_item(it) for it in resp["Items"]]
    sks = {it["sk"] for it in items}
    assert sks == {"1"}
    assert items[0]["tag"] == "kept"
