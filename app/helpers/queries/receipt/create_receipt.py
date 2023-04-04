create_receipt_mutation = """
mutation($input: CreateReceiptInput!) {
  createReceipt(input: $input) {
    receipt {
      id
    }
  }
}
"""