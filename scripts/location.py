from sentence_transformers import SentenceTransformer, util
import numpy as np
from geopy.distance import geodesic  # For geodesic distance between lat/long
import torch

#  These are all columns related to location
# [
#     "locations",
#     "main_country_code",
#     "main_region",
#     "main_city_district",
#     "main_city",
#     "main_postcode",
#     "main_street",
#     "main_street_number",
#     "main_latitude",
#     "main_longitude",
# ]

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = SentenceTransformer('paraphrase-MiniLM-L6-v2', device=device)

# if 2 locations are in a range of 10m, it means that they are similar
GEODESIC_THRESHOLD = 100


def get_text_similarity(text1, text2):
    if text1 and text2:
        embeddings = model.encode([text1, text2], convert_to_tensor=True)
        return util.cos_sim(embeddings[0], embeddings[1]).item()
    return 0.0


# Function to calculate geodesic distance between lat/long pairs
def calculate_geodesic_distance(lat1, lon1, lat2, lon2):
    try:
        if lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None:
            return geodesic((lat1, lon1), (lat2, lon2)).meters
        else:
            return None
    except Exception as e:
        print("Caught: ", e)
        return None


# Function to compute location similarity between two rows
def location_similarity_code(row1, row2):
    lat1, lon1 = row1.get('main_latitude'), row1.get('main_longitude')
    lat2, lon2 = row2.get('main_latitude'), row2.get('main_longitude')

    geodesic_distance = calculate_geodesic_distance(lat1, lon1, lat2, lon2)
    geodesic_score = 0.0
    if geodesic_distance is not None:
        if geodesic_distance == 0.0:
            geodesic_score = 1.0
        else:
            geodesic_score = min(1.0, GEODESIC_THRESHOLD / geodesic_distance)

    # in this case it is safe to return 1.0
    if geodesic_score == 1.0:
        return 1.0

    direct_comparisons = {
        'main_country_code': (row1['main_country_code'] == row2['main_country_code']) if row1['main_country_code'] and row2['main_country_code'] else False,
        'main_region': (row1['main_region'] == row2['main_region']) if row1['main_region'] and row2['main_region'] else False,
        'main_city_district': (row1['main_city_district'] == row2['main_city_district']) if row1['main_city_district'] and row2['main_city_district'] else False,
        'main_city': (row1['main_city'] == row2['main_city']) if row1['main_city'] and row2['main_city'] else False,
        'main_postcode': (row1['main_postcode'] == row2['main_postcode']) if row1['main_postcode'] and row2['main_postcode'] else False,
        'main_street': (row1['main_street'] == row2['main_street']) if row1['main_street'] and row2['main_street'] else False,
        'main_street_number': (row1['main_street_number'] == row2['main_street_number']) if row1['main_street_number'] and row2['main_street_number'] else False,
    }

    location_similarities = sum(direct_comparisons.values())

    # if we have each one equal to each other it is clearly the same location
    if location_similarities == len(direct_comparisons):
        return 1.0

    # a score how many from how many did we match (normalised)
    location_sim_mean = location_similarities / len(direct_comparisons)

    locations1 = row1['locations'].split('|') if row1['locations'] else []
    locations2 = row2['locations'].split('|') if row2['locations'] else []

    location_scores = []
    for loc1 in locations1:
        for loc2 in locations2:
            location_scores.append(get_text_similarity(loc1.strip(), loc2.strip()))

    if location_scores:
        location_similarity = np.mean(location_scores)
    else:
        location_similarity = 0.0

    final_score = (geodesic_score + location_similarity + location_sim_mean) / 3

    return final_score


if __name__ == '__main__':
    print(calculate_geodesic_distance(18.6629769, 73.7211681, 18.6626078, 73.7295653))