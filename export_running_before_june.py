import os
import json
import xlsxwriter
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

OUTPUT_FILE = "experiments_running_before_june.xlsx"


response = (
    supabase
    .table("optimizely_experiments")
    .select("*")
    .or_(
        "and(start_date.gte.2026-06-01T00:00:00Z,start_date.lt.2026-07-01T00:00:00Z),"
        "and(start_date.lt.2026-06-01T00:00:00Z,end_date.gte.2026-06-01T00:00:00Z),"
        "and(status.eq.running,start_date.lt.2026-07-01T00:00:00Z)"
    )
    .order("start_date")
    .execute()
)

rows = response.data

workbook = xlsxwriter.Workbook(OUTPUT_FILE)
worksheet = workbook.add_worksheet("Running Before June")

header = workbook.add_format({"bold": True})
text = workbook.add_format({"num_format": "@"})

if rows:
    columns = list(rows[0].keys())

    for c, col in enumerate(columns):
        worksheet.write(0, c, col, header)

    for r, row in enumerate(rows, start=1):
        for c, col in enumerate(columns):
            value = row[col]

            if isinstance(value, (dict, list)):
                value = json.dumps(value)

            if col in ["experiment_id", "campaign_id"]:
                worksheet.write_string(r, c, str(value), text)
            else:
                worksheet.write(r, c, value)

workbook.close()

print(f"Exported {len(rows)} rows")
