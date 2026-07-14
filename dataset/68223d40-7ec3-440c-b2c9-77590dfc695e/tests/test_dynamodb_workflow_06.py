from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_after_seeding_multiple(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfQuery1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"},{"AttributeName":"sk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"},{"AttributeName":"sk","KeyType":"RANGE"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    ddb_client.put_item(TableName="WfQuery1", Item={"pk": {"S": "p"}, "sk": {"S": "s1"}})
    ddb_client.put_item(TableName="WfQuery1", Item={"pk": {"S": "p"}, "sk": {"S": "s2"}})
    ddb_client.put_item(TableName="WfQuery1", Item={"pk": {"S": "other"}, "sk": {"S": "s3"}})
    result = cli("dynamodb", "query", "--table-name", "WfQuery1",
                 "--key-condition-expression", "pk = :v",
                 "--expression-attribute-values", '{":v":{"S":"p"}}')
    assert result.returncode == 0
    items = ddb_client.query(TableName="WfQuery1",
                             KeyConditionExpression="pk = :v",
                             ExpressionAttributeValues={":v": {"S": "p"}})["Items"]
    sks = {from_item(i)["sk"] for i in items}
    assert sks == {"s1", "s2"}
