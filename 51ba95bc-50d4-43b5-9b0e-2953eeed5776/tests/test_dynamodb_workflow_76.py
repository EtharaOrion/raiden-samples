from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_reput_with_extra_attributes(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_rea1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_rea1",
                 "--item", '{"pk":{"S":"re1"},"a":{"S":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_rea1",
                 "--item", '{"pk":{"S":"re1"},"a":{"S":"1"},"b":{"S":"2"},"c":{"S":"3"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_rea1", Key={"pk": {"S": "re1"}})
    assert from_item(resp["Item"]) == {"pk": "re1", "a": "1", "b": "2", "c": "3"}
