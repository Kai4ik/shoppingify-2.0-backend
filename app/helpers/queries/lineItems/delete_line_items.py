from typing import List


def delete_line_items_mutation(line_items_ids: List[int]):
    mutation = 'mutation ('
    for k in range(len(line_items_ids)):
        mutation += f'$input_{k}: DeleteLineItemByIdInput!,'
        if k == len(line_items_ids)-1:
            mutation = mutation[:-1]

    mutation += ") {"
    for k in range(len(line_items_ids)):
        mutation += f'deleteLineItemById_{k}: deleteLineItemById(input: $input_{k})'
        mutation += "{ deletedLineItemId }"

    mutation += "}"
    return mutation
