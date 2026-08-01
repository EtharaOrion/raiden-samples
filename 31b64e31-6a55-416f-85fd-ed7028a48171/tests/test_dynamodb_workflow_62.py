from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_decimal_number_get(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf63Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf63Tbl",
                 "--item", '{"pk":{"S":"d"},"price":{"N":"19.99"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf63Tbl", Key={"pk": {"S": "d"}})
    assert resp["Item"]["price"]["N"] == "19.99"
