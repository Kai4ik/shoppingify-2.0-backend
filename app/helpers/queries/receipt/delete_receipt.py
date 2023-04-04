delete_receipt_mutation = """
mutation($input: DeleteReceiptByReceiptNumberAndUserInput!) {
  deleteReceiptByReceiptNumberAndUser(input: $input) {
    receipt {
      id
    }
  }
}
"""