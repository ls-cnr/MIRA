# Module that chooses the highest scored response
def chooser(response_dict):
    score_order = {"high": 3, "medium": 2, "low": 1}

    # Find the response with the highest score
    max_index = max(
        range(len(response_dict['score'])),
        key=lambda i: score_order.get(response_dict['score'][i].lower(), 0)
    )

    return response_dict['response'][max_index]