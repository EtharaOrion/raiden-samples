from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_float_number_roundtrip(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_flt1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_flt1",
                 "--item", '{"pk":{"S":"f1"},"price":{"N":"3.14"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_flt1", Key={"pk": {"S": "f1"}})
    assert resp["Item"]["price"]["N"] == "3.14"
