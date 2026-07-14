from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_after_seeding(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfTblI",
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"}],
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"}],
        BillingMode="PAY_PER_REQUEST")
    for sk in ["a", "b", "c"]:
        ddb_client.put_item(TableName="WfTblI", Item={"pk": {"S": "grp"}, "sk": {"S": sk}})
    ddb_client.put_item(TableName="WfTblI", Item={"pk": {"S": "other"}, "sk": {"S": "z"}})
    result = cli("dynamodb", "query", "--table-name", "WfTblI",
                 "--key-condition-expression", "pk = :v",
                 "--expression-attribute-values", '{":v":{"S":"grp"}}')
    assert result.returncode == 0
    resp = ddb_client.query(
        TableName="WfTblI",
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "grp"}})
    sks = {from_item(it)["sk"] for it in resp["Items"]}
    assert sks == {"a", "b", "c"}
