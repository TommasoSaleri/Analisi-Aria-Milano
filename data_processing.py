import json

def create_database():
    # apro il file "stazioni.json"
    with open("stazioni.geojson", "r", encoding="utf8") as file:
        geo_stazioni = json.load(file)

    # dizionario con tutte le stazioni e le rispettive caratteristiche
    stazioni = {}

    # estraggo le caratteristiche di ciascuna stazione
    for elem in geo_stazioni["features"]:
        id_stazione = int(elem["properties"]["id_amat"])
        stazioni[id_stazione] = {
            "id": id_stazione,
            "nome": elem["properties"]["nome"],
            "inquinanti": elem["properties"]["inquinanti"],
            "coordinate": elem["geometry"]["coordinates"]
        }

    # lista con tutti i dati suddivisi per anno
    dati = []

    for anno in range(2016, 2026):
        file_name = f"{anno}_qualita-aria.json"

        # apro il file con i dati di ciascun anno
        with open(file_name, "r", encoding="utf8") as file:
            misurazioni = json.load(file)

        # controllo i valori estratti e non li inserisco in caso di valori nulli
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

            # creo un dizionario con i dati di ogni data
            record = {
                "anno": anno,
                "data": m["data"],
                "id_stazione": id_stazione,
                "nome_stazione": stazioni[id_stazione]["nome"],
                "coordinate": stazioni[id_stazione]["coordinate"],
                "inquinante": str(m["inquinante"]),
                "valore": valore
            }

            # aggiungo il dizionario record alla lista dati
            dati.append(record)

    # creo (se non esiste) o apro (se esiste) un file "dati.json" in modalità scrittura
    with open("dati.json", "w", encoding="utf8") as file:
        # converto i dati in un oggetto json
        json.dump(dati, file, ensure_ascii=False, indent=2)