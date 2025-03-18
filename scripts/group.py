import pandas as pd

class DataGroup:

    def __init__(self, group_no):
        self.group_no = group_no
        self.domain = set()
        self.facebook_url = set()
        self.twitter_url = set()
        self.instagram_url = set()
        self.linkedin_url = set()
        self.youtube_url = set()
        self.android_app_url = set()
        self.ios_app_url = set()
        # keeps a record of all rows associated to this group
        self.row_indexes = set()

    # makes the union of 2 groups
    def union(self, group: "DataGroup"):
        self.domain.update(group.domain)
        self.facebook_url.update(group.facebook_url)
        self.twitter_url.update(group.twitter_url)
        self.instagram_url.update(group.instagram_url)
        self.linkedin_url.update(group.linkedin_url)
        self.youtube_url.update(group.youtube_url)
        self.android_app_url.update(group.android_app_url)
        self.ios_app_url.update(group.ios_app_url)
        self.row_indexes.update(group.row_indexes)

    # ads a row to the group and its corresponding uri's
    def add_row(self, row):
        self.row_indexes.add(row['id'])

        if pd.notna(row['website_domain']):
            self.domain.add(row['website_domain'])

        if pd.notna(row['facebook_url']):
            self.facebook_url.add(row['facebook_url'])

        if pd.notna(row['twitter_url']):
            self.twitter_url.add(row['twitter_url'])

        if pd.notna(row['instagram_url']):
            self.instagram_url.add(row['instagram_url'])

        if pd.notna(row['linkedin_url']):
            self.linkedin_url.add(row['linkedin_url'])

        if pd.notna(row['youtube_url']):
            self.youtube_url.add(row['youtube_url'])

        if pd.notna(row['android_app_url']):
            self.android_app_url.add(row['android_app_url'])

        if pd.notna(row['ios_app_url']):
            self.ios_app_url.add(row['ios_app_url'])

    # if this is called, it means that we need to reroute using the dictionaries received the URIs that point to this
    # DataGroup
    def reroute_uris(self, reroute_to_group, domain_dict, facebook_url_dict, twitter_url_dict, instagram_url_dict,
                     linkedin_url_dict, youtube_url_dict, android_app_dict, ios_app_dict):

        # Reroute the domains
        for domain in self.domain:
            domain_dict[domain] = reroute_to_group

        # Reroute the facebook_url
        for facebook_url in self.facebook_url:
            facebook_url_dict[facebook_url] = reroute_to_group

        # Reroute the twitter_url
        for twitter_url in self.twitter_url:
            twitter_url_dict[twitter_url] = reroute_to_group

        # Reroute the instagram_url
        for instagram_url in self.instagram_url:
            instagram_url_dict[instagram_url] = reroute_to_group

        # Reroute the linkedin_url
        for linkedin_url in self.linkedin_url:
            linkedin_url_dict[linkedin_url] = reroute_to_group

        # Reroute the youtube_url
        for youtube_url in self.youtube_url:
            youtube_url_dict[youtube_url] = reroute_to_group

        # Reroute the android_app_url
        for android_app_url in self.android_app_url:
            android_app_dict[android_app_url] = reroute_to_group

        # Reroute the ios_app_url
        for ios_app_url in self.ios_app_url:
            ios_app_dict[ios_app_url] = reroute_to_group

        # Clear all the URI sets after rerouting
        self.domain = set()
        self.facebook_url = set()
        self.twitter_url = set()
        self.instagram_url = set()
        self.linkedin_url = set()
        self.youtube_url = set()
        self.android_app_url = set()
        self.ios_app_url = set()

    def __str__(self):
        attrs = [
            ("Group No", self.group_no),
            ("Row Indexes", ", ".join(map(str, self.row_indexes)) if self.row_indexes else "None"),
            ("Domains", ", ".join(self.domain) if self.domain else "None"),
            ("Facebook URLs", ", ".join(self.facebook_url) if self.facebook_url else "None"),
            ("Twitter URLs", ", ".join(self.twitter_url) if self.twitter_url else "None"),
            ("Instagram URLs", ", ".join(self.instagram_url) if self.instagram_url else "None"),
            ("LinkedIn URLs", ", ".join(self.linkedin_url) if self.linkedin_url else "None"),
            ("YouTube URLs", ", ".join(self.youtube_url) if self.youtube_url else "None"),
            ("Android App URLs", ", ".join(self.android_app_url) if self.android_app_url else "None"),
            ("iOS App URLs", ", ".join(self.ios_app_url) if self.ios_app_url else "None"),
        ]

        return str(attrs)