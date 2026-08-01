from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_composite_key_put_get(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf11Tbl",
                 "--attribute-definitions",
                 '[{"AttributeName":"pk","AttributeType":"S"},{"AttributeName":"sk","AttributeType":"S"}]',
                 "--key-schema",
                 '[{"AttributeName":"pk","KeyType":"HASH"},{"AttributeName":"sk","KeyType":"RANGE"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf11Tbl",
                 "--item", '{"pk":{"S":"p1"},"sk":{"S":"s1"},"d":{"S":"data"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf11Tbl",
                               Key={"pk": {"S": "p1"}, "sk": {"S": "s1"}})
    assert from_item(resp["Item"]) == {"pk": "p1", "sk": "s1", "d": "data"}
