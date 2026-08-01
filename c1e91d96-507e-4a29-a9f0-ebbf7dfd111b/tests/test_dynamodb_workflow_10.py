from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_composite_key_put_get(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfComp1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"},{"AttributeName":"sk","AttributeType":"N"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"},{"AttributeName":"sk","KeyType":"RANGE"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfComp1",
                 "--item", '{"pk":{"S":"p"},"sk":{"N":"7"},"data":{"S":"x"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfComp1", Key={"pk": {"S": "p"}, "sk": {"N": "7"}})
    assert from_item(resp["Item"]) == {"pk": "p", "sk": 7, "data": "x"}
