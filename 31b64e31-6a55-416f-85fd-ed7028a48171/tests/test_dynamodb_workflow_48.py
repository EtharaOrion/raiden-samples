from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_put_get_numeric_neg(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf49Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf49Tbl",
                 "--item", '{"pk":{"S":"neg"},"bal":{"N":"-42"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf49Tbl", Key={"pk": {"S": "neg"}})
    assert resp["Item"]["bal"]["N"] == "-42"
