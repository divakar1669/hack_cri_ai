from services.graph_api import get_post_with_replies
from services.llm_api import summarize_and_tag
from services.db import save_metadata

if __name__ == "__main__":
    post_id = "your-message-id"
    post_data = get_post_with_replies(post_id)
    summary, tags = summarize_and_tag(post_data)
    teams_link = f"https://teams.microsoft.com/l/message/{post_id}"
    save_metadata(post_id, teams_link, summary, tags)
