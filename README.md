# Challenge 3 - Entity Resolution

### Task
Identify unique companies and group duplicate records accordingly.

### Context

The dataset contains company records imported from multiple systems, leading to duplicate entries with slight variations.

### Guidelines

- The dataset includes extensive company details, but not all fields are necessary for deduplication.
- The key challenge is to identify and leverage the most relevant attributes to accurately detect and group duplicate records.
- Take the time to research and understand what defines a company and which attributes uniquely identify it. This understanding is crucial for accurately detecting and grouping duplicate records.
At times, incomplete data may require you to make decisions where there is no clear right or wrong choice. 

### Output

Return the updated dataset where you have correctly identified unique companies and grouped duplicate records accordingly.

# Before words

Before I dive deep in my solution I would like to clear some things about how I see 'unique' companies.

### My definition on unique companies

In the dataset, there are companies which may come from the same franchise, but in different places, that is
why in my solution I consider companies as legal entities, meaning if KFC has 40 restaurants in Romania, those 40 restaurants are unique companie, since they are different legal entities.

### Another important thing

The description of the challenge strictly implies grouping duplicates together so I won't do anything reargding merging duplicates together.

# Initial thoughts

I am not going to lie, I may have tried to run an hashing algorithm and of course I found 5 total matches, 
I may have :))

After becoming clear that this is a more complex task than it may seem, I decided to do a deep exploration of the dataset, this started with understanding each column and the possible values a column can have.

Initally I hoped to be able to find meaning in the values so I can create an algorithm that runs on the whole dataset and groups together duplicate companies. However after some exploration I found out that the data isn't predictable at all, meaning we can have discrepencies between names, domains, locations, description.

Afterwards, I decided that most likely companies that have the same domain represent the same company, so afterwards I traversed comppanies that have the same **domain** I found out a very intersting case which make me realise that the problem gets even more complicated.

### The ecards phenomen 

This business basically makes business digital cards for companies, so I was getting multiple companies from the **ecards.com** domain that were totally differnt.

### The Cluj wonderland phenomen 

After finding out about what I mentioned above, I was like, okay if they come from the same domain and have the same location it means for sure that they are the same company, well, of course I proved me wrong again, when I found that Wonderland Cluj has multiple companies, with the same domain, one near each other.

For example: Wonderland Horse Riding, Wonderland Hot Air Ballon (I think), Wonderland kindergarden, Wonderland resort etc


### The too much data phenomen

While trying to divise a plan I would get lost through the big volume of data, most of the time data that wouldn't count so much.

### Time for cleaning the dataset

Ok, so now I need to get done to business, there are many uknown varaibles, but to be able  them closely I to research I need to **clear** out the noise.

Therefore, below I will argument why I dropped that column from the dataset.

#### 1. Statistics, national, economics codes 

- 'sics_codified_industry'
- 'sics_codified_industry_code'
- 'sics_codified_subsector'
- 'sics_codified_subsector_code'
- 'sics_codified_sector'
- 'sics_codified_sector_code'
- 'naics_2022_primary_label'
- 'naics_2022_secondary_codes'
- 'naics_2022_secondary_labels'
- 'naics_vertical'
- 'isic_v4_labels'
- 'sic_labels'
- 'sic_codes'
- 'naics_2022_primary_code'
- 'isic_v4_codes'
- 'nace_rev2_labels'
- 'nace_rev2_codes'


**FYI, you can skip this short description of this codes**

- SICS (**Sustainability Industry Classification System**): It has largely been phased out in favor of more standardized systems like NAICS.

- NAICS (**North American Industry Classification System**): Widely used in North America to classify businesses into industries.

- ISIC (**International Standard Industrial Classification**): A global system for classifying economic activities, commonly used for international comparisons.

- SIC (**Standard Industrial Classification**): An older system, mostly replaced by NAICS, but still referenced in some contexts.

- NACE (**Nomenclature of Economic Activities**): The European counterpart to NAICS and ISIC
  
**End of short description of codes**

Basically, this are indicators, simillary to CAEN codes in Romania, to identify the domain in which the company activates, but as I found out, besides the fact thay they are in different regions, **SICS** was replaced by **NAICS**, only used in older contexts it becomes clear that handling this columns requires deeper understanding of them, possibly searching for discrapencies between the codes that actually exist (there are errors in the code, for example I found multiple companies representing a single entity with different latitude and longitude coordinates, that leads me to believe that clearly everything in the dataset could have a little noise), not to mention that we don't have that many non-null values.

```
 25  naics_2022_primary_code       18048 non-null  object
 26  naics_2022_primary_label      18048 non-null  object
 27  naics_2022_secondary_codes    244 non-null    object
 28  naics_2022_secondary_labels   244 non-null    object
 50  sics_codified_industry        5661 non-null   object
 51  sics_codified_industry_code   5661 non-null   object
 52  sics_codified_subsector       5661 non-null   object
 53  sics_codified_subsector_code  5661 non-null   object
 54  sics_codified_sector          5661 non-null   object
 55  sics_codified_sector_code     5661 non-null   object
 56  sic_codes                     18048 non-null  object
 57  sic_labels                    18048 non-null  object
 58  isic_v4_codes                 18048 non-null  object
 59  isic_v4_labels                18048 non-null  object
 60  nace_rev2_codes               18048 non-null  object
```

Conclusion, the time and effort I should put into those codes is a waste of my rsources given the task and the deadline, when I canc learly focus on understanding more important fields.

#### 2. Time related columns

- 'year_founded'
- 'lnk_year_founded'
- 'created_at'
- 'last_updated_at' # this would be useful if I wanted to merge them into one, but since I am just grouping them, i dont care

Not really relevant to my problem, the year a company was founded is not really relevant in my case because, besided that values can be wrong, it also isn't something that can identify a unique company.
'last_updated_at' not really helps me in this situation because I am not interested in merging the information together, also since my job is to group duplicates together if there is a row with outdated company information and one with updated information it still makes the outdated one a duplicate, same with 'created_at'.

#### 3. Website metadata

- 'website_number_of_pages'
- 'website_tld'
- 'inbound_links_count'
- 'all_domains'
- 'website_language_code'

I decided to discard this metadata about the website were the company was scraped from because it provides little to none inside into the strucutre of the company.

Firstly, 'website_number_of_pages' is something related to nothing of intereset currently, because it has no directly connection to the company, same for 'ibound_links_count' cause I am not able to find out which sites point to the current company's site.

Regarding, 'website_tld', that one can just be obtain from the 'website_domain' field, so no need for this. 
'all_domains' is equal to 'domains' so I can delete this one from the start.
'website_language_code' could matter if I would be using an embedding model specific for each language, but in my case my embedding model can handle multiple languages.


    'tiktok_url',
    'alexa_rank',
     48  tiktok_url                    0 non-null      object
 49  alexa_rank                    0 non-null      object
    'status',
    'main_country',
    'main_business_category',
    'business_model',
    'num_locations',
    'company_type',
    'revenue',
    'revenue_type',
    'employee_count',
    'employee_count_type',


# Solution description