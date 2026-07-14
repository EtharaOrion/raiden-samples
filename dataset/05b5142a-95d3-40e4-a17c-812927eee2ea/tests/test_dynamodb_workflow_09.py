from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_after_seeding(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfQuery",
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"}],
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"}],
        BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="WfQuery", Item={"pk": {"S": "g1"}, "sk": {"S": "s1"}})
    ddb_client.put_item(TableName="WfQuery", Item={"pk": {"S": "g1"}, "sk": {"S": "s2"}})
    ddb_client.put_item(TableName="WfQuery", Item={"pk": {"S": "g2"}, "sk": {"S": "s3"}})
    result = cli("dynamodb", "query", "--table-name", "WfQuery",
                 "--key-condition-expression", "pk = :v",
                 "--expression-attribute-values", '{":v":{"S":"g1"}}')
    assert result.returncode == 0
    resp = ddb_client.query(
        TableName="WfQuery",
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "g1"}})
    sks = {from_item(it)["sk"] for it in resp["Items"]}
    assert sks == {"s1", "s2"}
