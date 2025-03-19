import pandas as pd

from scripts.group import DataGroup

website_domain_dict = {}
facebook_url_dict = {}
twitter_url_dict = {}
instagram_url_dict = {}
linkedin_url_dict = {}
youtube_url_dict = {}
android_app_url_dict = {}
ios_app_url_dict = {}

extra_domains_dict = {}

# these are URI for the data source from where the entity comes
uri_types = ['website_domain', 'facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url', 'youtube_url',
             'android_app_url', 'ios_app_url', 'domains']


# this function should be passed rows which have at least one of the uri's not null
def create_data_groups(df: pd.DataFrame):
    group_counter = 0

    reroute_operations = 0

    # traverse row by row
    for _, row in df.iterrows():
        current_group = None

        for uri_type in uri_types:
            uris = row[uri_type]

            if pd.notna(uris):
                uris = uris.split('|')
                for uri in uris:
                    uri = uri.strip()
                    if uri_type != 'domains':
                        uri_dict = globals().get(f"{uri_type}_dict")
                    else:
                        uri_dict = website_domain_dict

                    # uri_dict[uri] -> DataGroup (group_that_exists)
                    if uri in uri_dict:
                        group_that_exists = uri_dict[uri]

                        # uri_dict -> DataGroup (group_that_exists)
                        if current_group is None:
                            group_that_exists.add_row(row)
                            current_group = group_that_exists
                        elif current_group != group_that_exists:
                            # uri_dict -> DataGroup (group_that_exists)
                            # row -> DataGroup (current_group)
                            group_that_exists.union(current_group)
                            current_group.reroute_uris(
                                group_that_exists, website_domain_dict, facebook_url_dict, twitter_url_dict, instagram_url_dict,
                                linkedin_url_dict, youtube_url_dict, android_app_url_dict, ios_app_url_dict
                            )

                            current_group = group_that_exists

                            reroute_operations += 1
                    elif current_group is None:
                        # uri_dict[uri] -> None
                        current_group = DataGroup(group_counter)
                        current_group.add_row(row)

                        uri_dict[uri] = current_group
                        group_counter += 1

    groups = set()
    # after we created all the dictionary and they point to the same resource
    for uri_type in uri_types:
        if uri_type != 'domains':
            uri_dict = globals().get(f"{uri_type}_dict")
            for uri in uri_dict:
                data_group = uri_dict[uri]
                # even if we add clones, it won't store them in the set
                groups.add(data_group)

    print("reroute operations=", reroute_operations)
    return groups
