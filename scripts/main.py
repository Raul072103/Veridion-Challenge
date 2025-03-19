import pandas as pd
from scripts.score import similarity_score
from scripts.group_by import create_data_groups
from scripts.processing import process_clean_parquet
from collections import defaultdict


def save_duplicated_groups(duplicate_group_id, rows):
    grouped_df = pd.concat([rows])
    grouped_df.to_csv(f'./../duplicates/group_{duplicate_group_id}.csv', index=False)


if __name__ == '__main__':
    process_clean_parquet()

    df = pd.read_parquet('./../assets/processed_veridion_entity_resolution_challenge_cleaned.snappy.parquet')
    df['duplicate_group_id'] = -1  # Initialize with -1 for unmatched rows

    groups = list(create_data_groups(df))
    duplicate_group_counter = 0

    for group in groups:
        row_ids = list(group.row_indexes)
        checked_ids = [0] * len(row_ids)
        duplicate_groups = defaultdict(list)

        for i in range(0, len(row_ids) - 1):
            id1 = row_ids[i]
            row1 = df[df['id'] == id1].iloc[0]

            for j in range(i + 1, len(row_ids)):
                id2 = row_ids[j]
                row2 = df[df['id'] == id2].iloc[0]

                if checked_ids[j] != 0:
                    continue

                score = similarity_score(row1, row2)
                if score > 0.5:
                    if checked_ids[i] != 0:
                        checked_ids[j] = checked_ids[i]
                    else:
                        checked_ids[i] = duplicate_group_counter
                        checked_ids[j] = duplicate_group_counter

        for i in range(0, len(row_ids)):
            row_id = row_ids[i]
            duplicate_group_id = checked_ids[i]

            # No grouping has been found
            if duplicate_group_id == 0:
                duplicate_groups[duplicate_group_counter].append(row_id)
                duplicate_group_counter += 1
            else:
                duplicate_groups[duplicate_group_id].append(row_id)

    # Assign duplicate group IDs to the DataFrame
    for group_id, rows_id in duplicate_groups.items():
        df.loc[df['id'].isin(rows_id), 'duplicate_group_id'] = group_id

    # Save the DataFrame with duplicate groups as a Parquet file
    df.to_parquet('./../duplicates/processed_with_duplicates.parquet', index=False)
