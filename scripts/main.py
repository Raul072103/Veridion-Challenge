import pandas as pd
from scripts.score import similarity_score
from scripts.group_by import create_data_groups
from scripts.processing import process_clean_parquet
from collections import defaultdict


if __name__ == '__main__':
    process_clean_parquet()

    df = pd.read_parquet('./../assets/processed_veridion_entity_resolution_challenge_cleaned.snappy.parquet')
    df['duplicate_group_id'] = -1  # Initialize with -1 for unmatched rows

    groups = list(create_data_groups(df))
    duplicate_group_counter = 0

    for group in groups[:1000]:
        row_ids = list(group.row_indexes)
        checked_ids = [-1] * len(row_ids)
        duplicate_groups = defaultdict(list)

        if duplicate_group_counter % 100 == 0:
            print(f"{duplicate_group_counter}: LOADING")

        for i in range(0, len(row_ids) - 1):
            id1 = row_ids[i]
            row1 = df[df['id'] == id1].iloc[0]

            for j in range(i + 1, len(row_ids)):
                id2 = row_ids[j]
                row2 = df[df['id'] == id2].iloc[0]

                if checked_ids[j] != -1:
                    continue

                score = similarity_score(row1, row2)
                if score > 0.5:
                    # Assign duplicate group IDs
                    if checked_ids[i] == -1:
                        checked_ids[i] = duplicate_group_counter
                        duplicate_group_counter += 1
                    checked_ids[j] = checked_ids[i]

        for k, row_id in enumerate(row_ids):
            if checked_ids[k] == -1:
                checked_ids[k] = duplicate_group_counter
                duplicate_group_counter += 1

        # Apply duplicate group IDs directly to the DataFrame
        df.loc[row_ids, 'duplicate_group_id'] = checked_ids

    print('Grouping done')

    # Reset index and save
    df = df.reset_index()
    df.to_parquet('./../duplicates/processed_with_duplicates.parquet', index=False)
    print('Saved successfully')
