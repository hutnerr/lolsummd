from util.clogger import Clogger
from models.account import Account
from util.riot_api_client import RiotAPIClient

def summarize_mastery(accounts: list[Account], client: RiotAPIClient) -> list[tuple[str, dict]]:

    # combine the mastery points and levels
    calculated_mastery = {}
    for acc in accounts:
        total_mastery = client.get_mastery_all_champions(acc)

        for id in total_mastery:
            if id not in calculated_mastery:
                calculated_mastery[id] = {"level": 0, "points": 0}

            calculated_mastery[id]["level"] += total_mastery[id]['level']
            calculated_mastery[id]["points"] += total_mastery[id]['points']

    # convert champion IDs to names
    calculated_mastery_with_names = {}
    for champ_id in calculated_mastery:
        champ_name = client.get_champion_name_by_id(champ_id)
        if champ_name:
            calculated_mastery_with_names[champ_name] = calculated_mastery[champ_id]
        else:
            Clogger.warn(f"Could not find name for champion ID {champ_id}, using ID as key.")
            calculated_mastery_with_names[f"ID_{champ_id}"] = calculated_mastery[champ_id]

    # sort by points
    sorted_mastery = sorted(calculated_mastery_with_names.items(), key=lambda item: item[1]['points'], reverse=True)
    return sorted_mastery