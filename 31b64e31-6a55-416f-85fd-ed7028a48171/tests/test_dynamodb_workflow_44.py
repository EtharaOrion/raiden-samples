from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_nested_map_get(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf45Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf45Tbl",
                 "--item", '{"pk":{"S":"nm"},"m":{"M":{"inner":{"M":{"x":{"N":"1"}}}}}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf45Tbl", Key={"pk": {"S": "nm"}})
    assert from_item(resp["Item"]) == {"pk": "nm", "m": {"inner": {"x": 1}}}
