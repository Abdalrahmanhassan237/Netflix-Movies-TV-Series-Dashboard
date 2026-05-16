import pandas as pd
import re

# 1. read excel files
titles_df = pd.read_csv(
    r"C:\Users\rebuytech\Downloads\PowerBI Projects\Dataset\Netflix_titles.csv"
)
ratings_df = pd.read_csv(
    r"C:\Users\rebuytech\Downloads\PowerBI Projects\Dataset\Netflix_Ratings.csv"
)
revenue_df = pd.read_csv(
    r"C:\Users\rebuytech\Downloads\PowerBI Projects\Dataset\Movies_Revenue.csv"
)


# 2. advanced text cleaning
def clean_title(text):
    if pd.isna(text):
        return text
    text = str(text).lower()
    # إزالة أي علامات ترقيم (مثل : أو - أو أقواس) والاحتفاظ بالحروف والأرقام فقط
    text = re.sub(r"[^\w\s]", "", text)
    # إزالة المسافات الزائدة
    text = re.sub(r"\s+", " ", text).strip()
    return text


titles_df["clean_title"] = titles_df["title"].apply(clean_title)
ratings_df["clean_title"] = ratings_df["title"].apply(clean_title)
revenue_df["clean_title"] = revenue_df["title"].apply(clean_title)

# 3.seperate movies
movies_only_df = titles_df[titles_df["type"].str.lower().str.strip() == "movie"].copy()

# 4. keep first & remove duplicates
ratings_unique = ratings_df.drop_duplicates(subset=["clean_title"], keep="first")
revenue_unique = revenue_df.drop_duplicates(subset=["clean_title"], keep="first")


# 3. merge the files in one file
merged_df = pd.merge(
    movies_only_df,
    ratings_unique[
        [
            "clean_title",
            "imdbAverageRating",
            "imdbNumVotes",
            "poster_path",
            "backdrop_path",
        ]
    ],
    on="clean_title",
    how="left",
)

final_df = pd.merge(
    merged_df,
    revenue_unique[
        [
            "clean_title",
            "rating",
            "votes",
            "budget",
            "opening_weekend_gross",
            "gross_worldwide",
            "gross_us_canada",
        ]
    ],
    on="clean_title",
    how="left",
)

# 5. rename columns after merge
final_df.rename(
    columns={"rating_x": "mautaring_rating", "rating_y": "revenue_rating"},
    inplace=True,
)

# 6. fix the money columns from "$" & "estimated"

money_cols = ["budget", "opening_weekend_gross", "gross_worldwide", "gross_us_canada"]

for col in money_cols:
    final_df[col] = final_df[col].astype(str).str.replace(r"[^\d.]", "", regex=True)
    final_df[col] = pd.to_numeric(final_df[col], errors="coerce")

# 7. clean duration column
if "duration" in final_df.columns:
    final_df["duration"] = (
        final_df["duration"]
        .astype(str)
        .str.replace(r"\s*min\s*$", "", regex=True)
        .str.strip()
    )
    final_df["duration"] = pd.to_numeric(final_df["duration"], errors="coerce")

# 8. rename it
final_df.rename(columns={"duration": "duration_min"}, inplace=True)


# 9. clean votes column
def clean_votes(val):
    if pd.isna(val):
        return val
    val = str(val).upper()
    if "K" in val:
        return float(val.replace("K", "")) * 1000
    if "M" in val:
        return float(val.replace("M", "")) * 1000000
    # remove ',' or anything else
    val = re.sub(r"[^\d.]", "", val)
    return pd.to_numeric(val, errors="coerce")


final_df["votes"] = final_df["votes"].apply(clean_votes)
final_df["imdbNumVotes"] = final_df["imdbNumVotes"].apply(clean_votes)

# 10.seperate Tv Shows
tv_shows_df = titles_df[titles_df["type"].str.lower().str.strip() == "tv show"].copy()

print(final_df.isnull().sum())
print(f"original tiltles data : {titles_df.shape}")
print(f"original movies_tiltles data : {movies_only_df.shape}")
print(f"seperated Tv Shows data : {tv_shows_df.shape}")
print(f"merged data : {merged_df.shape}")
print(f"final data : {final_df.shape}")


tv_shows_df.to_csv("Netflix_Tv_Shows.csv", index=False, encoding="utf-8-sig")
final_df.to_csv("Final_Netflix_Analysis_Clean.csv", index=False, encoding="utf-8-sig")
