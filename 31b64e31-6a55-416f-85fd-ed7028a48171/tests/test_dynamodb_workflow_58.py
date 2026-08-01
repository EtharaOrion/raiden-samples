from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_composite_absent_key_no_item(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf59Tbl",
                 "--attribute-definitions",
                 '[{"AttributeName":"pk","AttributeType":"S"},{"AttributeName":"sk","AttributeType":"N"}]',
                 "--key-schema",
                 '[{"AttributeName":"pk","KeyType":"HASH"},{"AttributeName":"sk","KeyType":"RANGE"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf59Tbl",
                 "--item", '{"pk":{"S":"P"},"sk":{"N":"1"},"v":{"S":"x"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf59Tbl", Key={"pk": {"S": "P"}, "sk": {"N": "99"}})
    assert "Item" not in resp
    resp = ddb_client.get_item(TableName="Wf59Tbl", Key={"pk": {"S": "P"}, "sk": {"N": "1"}})
    assert from_item(resp["Item"]) == {"pk": "P", "sk": 1, "v": "x"}
