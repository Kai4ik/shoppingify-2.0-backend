def create_line_items_mutation(line_items):
    mutation = 'mutation ('
    for k in range(len(line_items)):
        mutation += f'$input_{k}: CreateLineItemInput!,'
        if k == len(line_items)-1:
            mutation = mutation[:-1]

    mutation += ") {"
    for k in range(len(line_items)):
        mutation += f' createLineItem_{k}: createLineItem(input: $input_{k})'
        mutation += "{ clientMutationId }"

    mutation += "}"
    return mutation
