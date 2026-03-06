import gspread
from google.oauth2.service_account import Credentials
import config

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def _get_client():
    creds = Credentials.from_service_account_file(config.GOOGLE_CREDS_FILE, scopes=SCOPES)
    return gspread.authorize(creds)


def _get_sheet():
    client = _get_client()
    return client.open(config.GOOGLE_SHEET_NAME)


def ensure_tabs_exist():
    """Create the 4 required tabs if they don't exist."""
    sheet = _get_sheet()
    existing = [ws.title for ws in sheet.worksheets()]

    tabs = {
        "Competitors": ["handle"],
        "Prospects": ["handle", "user_id", "followers_count", "tweet_count", "source", "date_found", "status"],
        "Followed": ["handle", "user_id", "date_followed", "followed_back"],
        "Weekly Tracking": ["week", "followers_start", "followers_end", "followed", "unfollowed", "followback_rate"],
    }

    for tab_name, headers in tabs.items():
        if tab_name not in existing:
            ws = sheet.add_worksheet(title=tab_name, rows=2000, cols=len(headers))
            ws.append_row(headers)
            print(f"  Created tab: {tab_name}")
        else:
            print(f"  Tab exists: {tab_name}")


def read_tab(tab_name):
    """Read all rows from a tab as list of dicts."""
    sheet = _get_sheet()
    ws = sheet.worksheet(tab_name)
    return ws.get_all_records()


def append_rows(tab_name, rows):
    """Append multiple rows to a tab. Each row is a list of values."""
    if not rows:
        return
    sheet = _get_sheet()
    ws = sheet.worksheet(tab_name)
    ws.append_rows(rows)


def update_cell_by_match(tab_name, match_col, match_val, update_col, update_val):
    """Find a row where match_col == match_val and update update_col."""
    sheet = _get_sheet()
    ws = sheet.worksheet(tab_name)
    records = ws.get_all_records()
    headers = ws.row_values(1)

    match_idx = headers.index(match_col)
    update_idx = headers.index(update_col)

    for i, record in enumerate(records):
        if str(record.get(match_col, "")) == str(match_val):
            ws.update_cell(i + 2, update_idx + 1, update_val)
            return True
    return False


def get_existing_prospect_ids():
    """Get set of user_ids already in Prospects tab."""
    records = read_tab("Prospects")
    return {str(r["user_id"]) for r in records if r.get("user_id")}


def get_existing_followed_ids():
    """Get set of user_ids already in Followed tab."""
    records = read_tab("Followed")
    return {str(r["user_id"]) for r in records if r.get("user_id")}
