from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_large_number_roundtrip(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_lgn1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_lgn1",
                 "--item", '{"pk":{"S":"lg1"},"big":{"N":"123456789012345"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_lgn1", Key={"pk": {"S": "lg1"}})
    assert from_item(resp["Item"]) == {"pk": "lg1", "big": 123456789012345}
