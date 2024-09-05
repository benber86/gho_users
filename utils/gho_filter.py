def filter_gho_users(data: list[dict], action_labels=None):

    if action_labels is None:
        action_labels = ['borrowHistory']

    def get_gho_usage(history: dict, action: str) -> bool:
        for action in history[action]:
            if 'reserve' in action:
                if action['reserve']['symbol'] == 'GHO':
                    return True
        return False

    gho_users = []
    for label in action_labels:
        for entry in data:
            if get_gho_usage(entry, label):
                gho_users.append(entry['id'])

    return gho_users
