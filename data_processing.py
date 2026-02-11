import json

def create_database():
    with open("stazioni.geojson", "r", encoding="utf8") as file:
        geo_stazioni = json.load(file)

    stazioni = {}

    for elem in geo_stazioni["features"]:
        id_stazione = int(elem["properties"]["id_amat"])
        stazioni[id_stazione] = {
            "id": id_stazione,
            "nome": elem["properties"]["nome"],
            "inquinanti": elem["properties"]["inquinanti"],
            "coordinate": elem["geometry"]["coordinates"]
        }

    dati = []

    for anno in range(2016, 2026):
        file_name = f"{anno}_qualita-aria.json"

        with open(file_name, "r", encoding="utf8") as file:
            misurazioni = json.load(file)

        for m in misurazioni:
            if "stazione_id" not in m or "data" not in m or "inquinante" not in m or "valore" not in m:
                continue

            try:
                id_stazione = int(m["stazione_id"])
                valore = float(m["valore"])
            except:
                continue

            if id_stazione not in stazioni:
                continue

            record = {
                "anno": anno,
                "data": m["data"],
                "id_stazione": id_stazione,
                "nome_stazione": stazioni[id_stazione]["nome"],
                "coordinate": stazioni[id_stazione]["coordinate"],
                "inquinante": str(m["inquinante"]),
                "valore": valore
            }

            dati.append(record)

    with open("dati.json", "w", encoding="utf8") as file:
        json.dump(dati, file, ensure_ascii=False, indent=2)