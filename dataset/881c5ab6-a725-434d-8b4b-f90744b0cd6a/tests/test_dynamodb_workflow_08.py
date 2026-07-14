from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_seeded_items(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfTblI",
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"}],
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"}],
        BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="WfTblI", Item={"pk": {"S": "p"}, "sk": {"S": "a"}})
    ddb_client.put_item(TableName="WfTblI", Item={"pk": {"S": "p"}, "sk": {"S": "b"}})
    ddb_client.put_item(TableName="WfTblI", Item={"pk": {"S": "q"}, "sk": {"S": "c"}})
    result = cli("dynamodb", "query", "--table-name", "WfTblI",
                 "--key-condition-expression", "pk = :v",
                 "--expression-attribute-values", '{":v":{"S":"p"}}')
    assert result.returncode == 0
    items = ddb_client.query(
        TableName="WfTblI",
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "p"}})["Items"]
    got = set((from_item(i)["pk"], from_item(i)["sk"]) for i in items)
    assert got == {("p", "a"), ("p", "b")}
