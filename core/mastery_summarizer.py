from pyutils import Clogger, CloggerSetting
from models.account import Account
from core.riot_api_client import RiotAPIClient

def summarize_mastery(accounts: list[Account], client: RiotAPIClient, includeMetadata: bool = False, include_zeros: bool = False) -> list[tuple[str, dict]]:

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

    # convert champion IDs to names and attach metadata in one pass
    calculated_mastery_with_names = {}
    for champ_id in calculated_mastery:
        champ_name = client.get_champion_name_by_id(champ_id)
        if not champ_name:
            Clogger.warn(f"Could not find name for champion ID {champ_id}, using ID as key.")
            champ_name = f"ID_{champ_id}"

        if includeMetadata:
            calculated_mastery[champ_id]['title'] = champ_name
            champ_icon_filepath = client.get_champion_icon_by_id(champ_id)
            if champ_icon_filepath:
                calculated_mastery[champ_id]['icon'] = champ_icon_filepath
            else:
                Clogger.warn(f"Could not find champion icon for ID {champ_id}, skipping icon metadata.")

        calculated_mastery_with_names[champ_name] = calculated_mastery[champ_id]

    Clogger.debug("Completed mastery calculation and metadata addition")

    # Clogger.debug(calculated_mastery_with_names, settings_override={CloggerSetting.PPRINT_ENABLED: True})

    if include_zeros:
        for champ_id, champ_name in client.championIDs.items():
            if champ_name not in calculated_mastery_with_names:
                entry = {"level": 0, "points": 0}
                if includeMetadata:
                    entry['title'] = champ_name
                    icon_path = client.get_champion_icon_by_id(champ_id)
                    if icon_path:
                        entry['icon'] = icon_path
                calculated_mastery_with_names[champ_name] = entry

    # sort by points
    sorted_mastery = sorted(calculated_mastery_with_names.items(), key=lambda item: item[1]['points'], reverse=True)

    Clogger.debug("Sorted mastery by points")

    return sorted_mastery