from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_negative_number(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_neg1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_neg1",
                 "--item", '{"pk":{"S":"ng1"},"bal":{"N":"-15"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_neg1", Key={"pk": {"S": "ng1"}})
    assert from_item(resp["Item"]) == {"pk": "ng1", "bal": -15}
