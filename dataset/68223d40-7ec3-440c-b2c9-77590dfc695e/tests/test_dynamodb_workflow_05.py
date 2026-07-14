from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_reserved_word_validation(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfResv1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    ddb_client.put_item(TableName="WfResv1", Item={"pk": {"S": "r1"}, "status": {"S": "keep"}})
    result = cli("dynamodb", "update-item", "--table-name", "WfResv1",
                 "--key", '{"pk":{"S":"r1"}}',
                 "--update-expression", "SET Status = :v",
                 "--expression-attribute-values", '{":v":{"S":"changed"}}')
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
    resp = ddb_client.get_item(TableName="WfResv1", Key={"pk": {"S": "r1"}})
    assert from_item(resp["Item"])["status"] == "keep"
