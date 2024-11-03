# Libraries used
import requests
import csv
import time

# Variables
headers = {'User-agent': 'Mozilla/5.0'}
after = None

# Feature lists for CSV File
fieldnames = ['approved_at_utc', 'subreddit', 'selftext', 'author_fullname', 'saved', 'mod_reason_title', 'gilded',
              'clicked', 'title', 'link_flair_richtext', 'subreddit_name_prefixed', 'hidden', 'pwls',
              'link_flair_css_class', 'downs', 'thumbnail_height', 'top_awarded_type', 'hide_score', 'media_metadata',
              'name', 'quarantine', 'link_flair_text_color', 'upvote_ratio', 'author_flair_background_color', 'ups',
              'total_awards_received', 'media_embed', 'thumbnail_width', 'author_flair_template_id',
              'is_original_content', 'user_reports', 'secure_media', 'is_reddit_media_domain', 'is_meta', 'category',
              'secure_media_embed', 'link_flair_text', 'can_mod_post', 'score', 'approved_by', 'is_created_from_ads_ui',
              'author_premium', 'thumbnail', 'edited', 'author_flair_css_class', 'author_flair_richtext', 'gildings',
              'post_hint', 'content_categories', 'is_self', 'subreddit_type', 'created', 'link_flair_type', 'wls',
              'removed_by_category', 'banned_by', 'author_flair_type', 'domain', 'allow_live_comments', 'selftext_html',
              'likes', 'suggested_sort', 'banned_at_utc', 'view_count', 'archived', 'no_follow', 'is_crosspostable',
              'pinned', 'over_18', 'preview', 'all_awardings', 'awarders', 'media_only', 'link_flair_template_id',
              'can_gild', 'spoiler', 'locked', 'author_flair_text', 'treatment_tags', 'visited', 'removed_by',
              'mod_note', 'distinguished', 'subreddit_id', 'author_is_blocked', 'mod_reason_by', 'num_reports',
              'removal_reason', 'link_flair_background_color', 'id', 'is_robot_indexable', 'report_reasons', 'author',
              'discussion_type', 'num_comments', 'send_replies', 'whitelist_status', 'contest_mode', 'mod_reports',
              'author_patreon_flair', 'author_flair_text_color', 'permalink', 'parent_whitelist_status', 'stickied',
              'url', 'subreddit_subscribers', 'created_utc', 'num_crossposts', 'media', 'is_video',
              'url_overridden_by_dest', 'gallery_data', 'is_gallery', 'author_cakeday']

# List of subreddits to scrape
subreddits = ["r/economy", "r/pennystocks", "r/finance", "r/investing", "r/wallstreetbets"]

# Create a CSV file to store data
with open('data.csv', 'w', newline='', encoding="utf-8") as file:
    file_writer = csv.DictWriter(file, fieldnames=fieldnames)
    file_writer.writeheader()

    for subreddit in subreddits:
        after = None  # Reset after for each subreddit
        num_rows = 0  # Initialize row count for current subreddit

        while num_rows < 400:  # Loop until 400 rows are written
            subreddit_url = 'https://www.reddit.com/' + subreddit + '/.json'
            if after:
                subreddit_url += '?after=' + after

            r = requests.get(subreddit_url, headers=headers)
            data = r.json()  # Parse JSON data

            # Check if there are any posts to process
            if not data['data']['children']:
                break  # Exit loop if no more posts are available

            # Adds the scraped data (fieldnames) into rows in our csv
            for post in data['data']['children']:
                filtered_data = {key: post['data'][key] for key in fieldnames if key in post['data']}
                file_writer.writerow(filtered_data)
                num_rows += 1  # Increment row count after writing a post

                # Stop if we've reached 400 rows
                if num_rows >= 400:
                    print(f"Reached 400 rows for {subreddit}. Stopping.")
                    break  # Exit the for loop if 400 rows are written

            # Update 'after' for pagination
            after = data['data']['after']
            print(f"{num_rows} rows written from {subreddit}.")

            time.sleep(4)  # Sleep for 4 seconds to avoid hitting Reddit's rate limit

print("Scraping completed. Data saved to data.csv.")
