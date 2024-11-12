import requests
import pandas as pd
import time

# API Base URLs
top_anime_url = "https://api.jikan.moe/v4/top/anime"
anime_detail_url = "https://api.jikan.moe/v4/anime"

# Initialize empty DataFrame to store anime data
anime_df = pd.DataFrame(columns=[
    "anime_name", "status", "synopsis", "aired_from", "aired_to", 
    "anime_type", "total_seasons", "total_episodes", 
    "production_house", "score", "source"
])

# Function to fetch the anime IDs from the top anime page
def fetch_anime_ids():
    anime_ids = []
    page = 1
    total_requested_animes = 500  # we want info of 500 animes 

    while len(anime_ids) < total_requested_animes:
        response = requests.get(f"{top_anime_url}?page={page}")
        if response.status_code == 200:
            anime_data = response.json().get("data", [])
            anime_ids.extend([anime["mal_id"] for anime in anime_data])
            anime_ids = list(set(anime_ids))[:total_requested_animes]  # Remove duplicates and limit to 500
            
            # If no more data is available, stop the loop
            if not anime_data:
                print("No more anime data available.")
                break
        else:
            print(f"Failed to fetch data on page {page}: Status code {response.status_code}")
            break

        page += 1
        time.sleep(1)  # Optional: Sleep to respect API rate limits

    return anime_ids

# Function to fetch details for each anime ID
def fetch_anime_details(anime_id):
    try:
        response = requests.get(f"{anime_detail_url}/{anime_id}")
        if response.status_code == 200:
            anime_data = response.json().get("data", {})

            anime_name = anime_data.get("title", "N/A")
            status = anime_data.get("status", "N/A")
            synopsis = anime_data.get("synopsis", "N/A")
            aired_from = anime_data.get("aired", {}).get("from", "N/A")
            aired_to = anime_data.get("aired", {}).get("to", "N/A")
            anime_type = anime_data.get("type", "N/A")
            total_episodes = anime_data.get("episodes", "N/A")
            score = anime_data.get("score", "N/A")
            
            # Extract production studios
            studios = [studio["name"] for studio in anime_data.get("studios", [])]
            production_house = ", ".join(studios) if studios else "N/A"

            # Default to 1 season, can be adjusted
            source = anime_data.get("source", "N/A")
            total_seasons = 1

            return {
                "anime_name": anime_name,
                "status": status,
                "synopsis": synopsis,
                "aired_from": aired_from,
                "aired_to": aired_to,
                "anime_type": anime_type,
                "total_seasons": total_seasons,
                "total_episodes": total_episodes,
                "production_house": production_house,
                "score": score,
                "source": source
            }
        else:
            print(f"Failed to fetch details for anime ID {anime_id}: Status code {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching anime details for ID {anime_id}: {e}")
        return None

# Main function to run the ETL pipeline
def run_etl_pipeline():
    print("Fetching anime IDs...")
    anime_ids = fetch_anime_ids()

    print(f"Fetched {len(anime_ids)} anime IDs. Now fetching details...")
    for anime_id in anime_ids:
        anime_details = fetch_anime_details(anime_id)
        if anime_details:
            # Append the data to the DataFrame using pd.concat() for efficiency
            anime_row = pd.DataFrame([anime_details])
            global anime_df
            anime_df = pd.concat([anime_df, anime_row], ignore_index=True)

            # Optional: Delay to avoid hitting rate limits
            time.sleep(1)

    print(f"ETL Pipeline Complete. {len(anime_df)} anime details extracted.")
    return anime_df

# Run the ETL pipeline
anime_df = run_etl_pipeline()

# Save the results to a CSV file for further analysis
anime_df.to_csv("anime_data.csv", index=False)

# Display the first few rows of the DataFrame
print(anime_df.head())
