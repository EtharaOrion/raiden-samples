from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_after_seeding(cli, ddb_client, tmp_path):
    ddb_client.create_table(TableName="WfTblQuery1",
                            AttributeDefinitions=[
                                {"AttributeName": "pk", "AttributeType": "S"},
                                {"AttributeName": "sk", "AttributeType": "S"}],
                            KeySchema=[
                                {"AttributeName": "pk", "KeyType": "HASH"},
                                {"AttributeName": "sk", "KeyType": "RANGE"}],
                            BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="WfTblQuery1", Item={"pk": {"S": "g"}, "sk": {"S": "a"}})
    ddb_client.put_item(TableName="WfTblQuery1", Item={"pk": {"S": "g"}, "sk": {"S": "b"}})
    ddb_client.put_item(TableName="WfTblQuery1", Item={"pk": {"S": "other"}, "sk": {"S": "z"}})
    result = cli("dynamodb", "query", "--table-name", "WfTblQuery1",
                 "--key-condition-expression", "pk = :v",
                 "--expression-attribute-values", '{":v":{"S":"g"}}')
    assert result.returncode == 0
    items = ddb_client.query(
        TableName="WfTblQuery1",
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "g"}})["Items"]
    got = set()
    for it in items:
        got.add(it["sk"]["S"])
    assert got == {"a", "b"}
