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

movies_only_df = titles_df[titles_df["type"].str.lower().str.strip() == "movie"].copy()
# 2. standarize the title key
# for df in [titles_df, ratings_df, revenue_df]:
# df["title"] = df["title"].str.lower().str.strip()

# نحتفظ بأول نتيجة تظهر ونحذف التكرارات
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

print(final_df.isnull().sum())
print(f"original tiltles data : {titles_df.shape}")
print(f"original movies_tiltles data : {movies_only_df.shape}")
print(f"merged data : {merged_df.shape}")
print(f"final data : {final_df.shape}")
