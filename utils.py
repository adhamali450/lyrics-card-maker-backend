def add_stats(hits: list) -> None:
    """
    Add stats to the results so that we don't get KeyError when there are no stats

    Parameters:
        hits (list): The list of results from the Genius API
    """
    for i in range(len(hits)):
        if not hits[i]['result']['stats'].get('pageviews'):
            hits[i]['result']['stats'].update({'pageviews': 0})
