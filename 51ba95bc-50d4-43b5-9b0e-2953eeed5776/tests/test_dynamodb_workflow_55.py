from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_two_puts_condition_between(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_2pc1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_2pc1",
                 "--item", '{"pk":{"S":"pc1"},"seq":{"N":"1"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_2pc1",
                 "--item", '{"pk":{"S":"pc1"},"seq":{"N":"2"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_2pc1", Key={"pk": {"S": "pc1"}})
    assert from_item(resp["Item"]) == {"pk": "pc1", "seq": 2}
