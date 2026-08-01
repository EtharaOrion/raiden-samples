from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_number_types_get(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf13Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf13Tbl",
                 "--item", '{"pk":{"S":"num"},"a":{"N":"42"},"b":{"N":"7"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf13Tbl", Key={"pk": {"S": "num"}})
    assert resp["Item"]["a"]["N"] == "42"
    assert resp["Item"]["b"]["N"] == "7"
