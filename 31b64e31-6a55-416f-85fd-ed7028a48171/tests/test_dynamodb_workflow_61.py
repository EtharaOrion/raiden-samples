from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_zero_number_get(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf62Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf62Tbl",
                 "--item", '{"pk":{"S":"z"},"n":{"N":"0"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf62Tbl", Key={"pk": {"S": "z"}})
    assert resp["Item"]["n"]["N"] == "0"
