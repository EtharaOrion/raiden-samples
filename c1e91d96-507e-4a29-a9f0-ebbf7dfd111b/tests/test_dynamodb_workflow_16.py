from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_map_attribute(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfMap1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfMap1",
                 "--item", '{"pk":{"S":"m"},"meta":{"M":{"k1":{"S":"v1"},"k2":{"N":"9"}}}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfMap1", Key={"pk": {"S": "m"}})
    got = from_item(resp["Item"])
    assert got["meta"] == {"k1": "v1", "k2": 9}
