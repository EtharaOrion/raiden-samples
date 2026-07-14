from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_seeded_items(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="QueryTbl",
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"}],
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"}],
        BillingMode="PAY_PER_REQUEST")

    result = cli("dynamodb", "put-item", "--table-name", "QueryTbl",
                 "--item", '{"pk":{"S":"g1"},"sk":{"S":"a"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "QueryTbl",
                 "--item", '{"pk":{"S":"g1"},"sk":{"S":"b"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "QueryTbl",
                 "--item", '{"pk":{"S":"g2"},"sk":{"S":"c"}}')
    assert result.returncode == 0

    resp = ddb_client.query(
        TableName="QueryTbl",
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "g1"}})
    sks = sorted(from_item(it)["sk"] for it in resp["Items"])
    assert sks == ["a", "b"]
