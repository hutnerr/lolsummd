from pyutils import Clogger, CloggerSetting
from models.account import Account
from core.riot_api_client import RiotAPIClient

def summarize_mastery(accounts: list[Account], client: RiotAPIClient, includeMetadata: bool = False) -> list[tuple[str, dict]]:

    # combine the mastery points and levels
    calculated_mastery = {}
    for acc in accounts:
        total_mastery = client.get_mastery_all_champions(acc)

        for id in total_mastery:
            if id not in calculated_mastery:
                calculated_mastery[id] = {"level": 0, "points": 0}

            calculated_mastery[id]["level"] += total_mastery[id]['level']
            calculated_mastery[id]["points"] += total_mastery[id]['points']

    Clogger.debug(f"Calculated mastery for {len(calculated_mastery)} champions across {len(accounts)} accounts.")

    if includeMetadata:
        for champ_id in calculated_mastery:
            champ_name = client.get_champion_name_by_id(champ_id)
            if champ_name:
                calculated_mastery[champ_id]['title'] = champ_name
            else:
                Clogger.warn(f"Could not find champion info for ID {champ_id}, skipping metadata.")

            champ_icon_filepath = client.get_champion_icon_by_id(champ_id)
            if champ_icon_filepath:
                calculated_mastery[champ_id]['icon'] = champ_icon_filepath
            else:
                Clogger.warn(f"Could not find champion icon for ID {champ_id}, skipping icon metadata.")

    Clogger.debug("Completed mastery calculation and metadata addition")

    # convert champion IDs to names
    calculated_mastery_with_names = {}
    for champ_id in calculated_mastery:
        champ_name = client.get_champion_name_by_id(champ_id)
        if champ_name:
            calculated_mastery_with_names[f"{champ_name}"] = calculated_mastery[champ_id]
        else:
            Clogger.warn(f"Could not find name for champion ID {champ_id}, using ID as key.")
            calculated_mastery_with_names[f"ID_{champ_id}"] = calculated_mastery[champ_id]

    # Clogger.debug(calculated_mastery_with_names, settings_override={CloggerSetting.PPRINT_ENABLED: True})

    # sort by points
    sorted_mastery = sorted(calculated_mastery_with_names.items(), key=lambda item: item[1]['points'], reverse=True)

    Clogger.debug("Sorted mastery by points")

    return sorted_mastery