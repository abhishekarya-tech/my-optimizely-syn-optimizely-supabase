import os
import requests
from supabase import create_client

PROJECT_ID = "5790171803680768"
OPTIMIZELY_TOKEN = os.environ["OPTIMIZELY_TOKEN"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_all_experiments():
    url = "https://api.optimizely.com/v2/experiments"

    headers = {
        "Authorization": f"Bearer {OPTIMIZELY_TOKEN}"
    }

    all_experiments = []
    page = 1
    per_page = 100

    while True:
        params = {
            "project_id": PROJECT_ID,
            "page": page,
            "per_page": per_page,
        }

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=30,
        )
        response.raise_for_status()

        experiments = response.json()
        all_experiments.extend(experiments)

        print(f"Page {page}: retrieved {len(experiments)} experiments")

        if len(experiments) < per_page:
            break

        page += 1

    return all_experiments


def map_experiment(experiment):
    return {
        "experiment_id": str(experiment["id"]),
        "campaign_id": str(experiment["campaign_id"]),
        "campaign_name": experiment["name"],
        "experience_name": experiment["name"],
        "type": experiment["type"],
        "variations": experiment["variations"],
        "traffic_split": experiment["traffic_allocation"],
        "holdback": experiment["holdback"],
        "status": experiment["status"],
        "start_date": experiment.get("created"),
        "end_date": experiment.get("last_modified"),
    }


if __name__ == "__main__":
    experiments = get_all_experiments()
    rows = [map_experiment(exp) for exp in experiments]

    batch_size = 100

    for start in range(0, len(rows), batch_size):
        batch = rows[start:start + batch_size]

        (
            supabase
            .table("optimizely_experiments")
            .upsert(batch, on_conflict="experiment_id")
            .execute()
        )

        print(f"Synced records {start + 1}–{start + len(batch)}")

    print(f"Successfully synced all {len(rows)} experiments")
    
