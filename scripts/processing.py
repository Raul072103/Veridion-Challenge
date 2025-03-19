import pandas as pd

columns_to_drop = [
    'sics_codified_industry',
    'sics_codified_industry_code',
    'sics_codified_subsector',
    'sics_codified_subsector_code',
    'sics_codified_sector',
    'sics_codified_sector_code',
    'year_founded',
    'lnk_year_founded',
    'naics_2022_primary_label',
    'naics_2022_secondary_codes',
    'naics_2022_secondary_labels',
    'website_number_of_pages',
    'website_tld',
    'inbound_links_count',
    'tiktok_url',
    'alexa_rank',
    'created_at',
    'last_updated_at',
    'status',
    'main_country',
    'num_locations',
    'company_type',
    'naics_vertical',
    'isic_v4_labels',
    'sic_labels',
    'sic_codes',
    'naics_2022_primary_code',
    'isic_v4_codes',
    'nace_rev2_labels',
    'nace_rev2_codes',
    'revenue',
    'revenue_type',
    'employee_count',
    'employee_count_type',
    'all_domains',
    'website_language_code'
]

url_columns = {
    'website_url', 'facebook_url', 'twitter_url', 'instagram_url',
    'linkedin_url', 'ios_app_url', 'android_app_url', 'youtube_url'
}


# I want everything before the encounter of the third '/' discarded since that is information I know already
# http and https don't make any difference, since usually sites and especially big companies like linkedin, facebook etc
# keep them for backwards compatibility
def process_url(url):
    if isinstance(url, str):
        parts = url.split('/')
        if len(parts) > 3:
            return '/'.join(parts[3:])
        else:
            # around 10 url's
            return url
    return url


# handles the preprocessing needed for the data
def process_clean_parquet():
    df = pd.read_parquet('./../assets/veridion_entity_resolution_challenge.snappy.parquet')

    # normalize data (lowercase everything, strip of whitespaces)
    # don't normalize URLs since it matters, they are case-sensitive
    for col in df.select_dtypes(include='object').columns:
        if col not in url_columns:  # Skip the columns in url_columns
            df[col] = df[col].apply(lambda x: x.lower().strip() if isinstance(x, str) else x)
        else:
            df[col] = df[col].apply(process_url)

    # fill data on locations columns if "locations" has any data
    # we could have multiple locations and from my observations if data isn't filled on the other columns and it is
    # filled on the "locations" column then it is the first one from the "locations" column when split by '|'
    # which corresponds to that row
    locations = df['locations'].str.split('|').apply(
        lambda x: x[0] if isinstance(x, list) else '')  # Only take the first location
    locations_split = locations.str.split(',').apply(lambda x: [item.strip() for item in x])

    # List of column names corresponding to the values in 'locations'
    columns = [
        'main_country_code', 'main_country', 'main_region', 'main_city',
        'main_postcode', 'main_street', 'main_street_number', 'main_latitude', 'main_longitude'
    ]

    # Iterate over the rows and fill missing values in respective columns
    for index, row in df.iterrows():
        location_data = locations_split.iloc[index]

        # Iterate over each column and fill missing values
        for i, col in enumerate(columns):
            if pd.isnull(row[col]):  # Check if the column is empty
                value = location_data[i] if i < len(location_data) and location_data[i] else None
                df.at[index, col] = value

    # drop columns
    existing_columns = [col for col in columns_to_drop if col in df.columns]

    if existing_columns:
        df = df.drop(columns=existing_columns, axis=1)
        print(f"Dropped columns: {existing_columns}")
    else:
        print("None of the specified columns were found in the DataFrame.")

    # I want to be able to identify each row by a unique id
    df['id'] = range(len(df))

    df.to_parquet('./../assets/processed_veridion_entity_resolution_challenge_cleaned.snappy.parquet', engine='pyarrow')

    # Initially I wanted to drop companies entries that don't have a linkedin url, facebook, url, website url etc
    # after more thinking I realised I don't know from what sources the data comes so i decided not to delete anything
    # since data could be coming from a source I am not aware of, maybe some gov site