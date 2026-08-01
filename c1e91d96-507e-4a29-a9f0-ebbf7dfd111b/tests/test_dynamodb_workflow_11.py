from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_composite_missing_range(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfComp2",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"},{"AttributeName":"sk","AttributeType":"N"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"},{"AttributeName":"sk","KeyType":"RANGE"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfComp2",
                 "--item", '{"pk":{"S":"only"},"sk":{"N":"1"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfComp2", Key={"pk": {"S": "only"}, "sk": {"N": "999"}})
    assert "Item" not in resp
