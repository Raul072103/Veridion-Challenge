from scripts.location import location_code, get_text_similarity
import pandas as pd
#  'short_description',
#  'long_description',
#  'generated_description',

#  'business_tags',
#  'product_type',
#  'main_industry',
#  'main_sector',
#  'generated_business_tags',

#   should be statically checked for
#  'primary_phone',
#  'phone_numbers',
#  'primary_email',
#  'emails',
#  'other_emails'

# I think I will also go with statically checking
#  'company_name',
#  'company_legal_names',
#  'company_commercial_names',


def name_similarity_score(row1, row2):
    names1 = set()
    names2 = set()

    for col in ['company_name', 'company_legal_names', 'company_commercial_names']:
        if pd.notna(row1[col]):
            names1.update(name.strip() for name in row1[col].split('|'))
        if pd.notna(row2[col]):
            names2.update(name.strip() for name in row2[col].split('|'))

    if not names1 and not names2:
        return 0.0

    return len(names1.intersection(names2)) / (len(names1.union(names2)))


def contact_similarity_score(row1, row2):
    contact_fields = [
        'primary_phone', 'phone_numbers',
        'primary_email', 'emails', 'other_emails'
    ]

    contacts1 = set()
    contacts2 = set()

    for field in contact_fields:
        if pd.notna(row1[field]):
            contacts1.update(contact.strip() for contact in row1[field].split('|'))

        if pd.notna(row2[field]):
            contacts2.update(contact.strip() for contact in row2[field].split('|'))

    if not contacts1 and not contacts2:
        return 0.0

    return len(contacts1.intersection(contacts2)) / (len(contacts1.union(contacts2)))


def description_similarity_score(row1, row2):
    description_fields = [
        'short_description',
        'long_description',
        'generated_description'
    ]

    desc1 = " ".join(str(row1.get(field, "") or "").strip() for field in description_fields).strip()
    desc2 = " ".join(str(row2.get(field, "") or "").strip() for field in description_fields).strip()

    return get_text_similarity(desc1,  desc2)


def business_similarity_score(row1, row2):
    # Group fields into categories
    tag_fields = ['business_tags', 'generated_business_tags']
    sector_field = 'main_sector' # no multiple values
    industry_field = 'main_industry' # no multiple values
    product_field = 'product_type' # no multiple values, all have that &, but I consider them something simillar to CAEN codes

    # Initialize sets for each category
    tags1, tags2 = set(), set()
    sector1, sector2 = set(), set()
    industry1, industry2 = set(), set()
    product1, product2 = set(), set()

    # Populate tag sets
    for field in tag_fields:
        if pd.notna(row1[field]):
            tags1.update(tag.strip() for tag in row1[field].split('|'))
        if pd.notna(row2[field]):
            tags2.update(tag.strip() for tag in row2[field].split('|'))

    # Populate single-value sets for sector, industry, and product type
    if pd.notna(row1[sector_field]):
        sector1.add(row1[sector_field].strip())
    if pd.notna(row2[sector_field]):
        sector2.add(row2[sector_field].strip())

    if pd.notna(row1[industry_field]):
        industry1.add(row1[industry_field].strip())
    if pd.notna(row2[industry_field]):
        industry2.add(row2[industry_field].strip())

    if pd.notna(row1[product_field]):
        product1.add(row1[product_field].strip())
    if pd.notna(row2[product_field]):
        product2.add(row2[product_field].strip())

    def calculate_score(set1, set2):
        if not set1 and not set2:
            return 0.0
        return len(set1.intersection(set2)) / (len(set1.union(set2)))

    tag_score = calculate_score(tags1, tags2)
    sector_score = calculate_score(sector1, sector2)
    industry_score = calculate_score(industry1, industry2)
    product_score = calculate_score(product1, product2)

    # Final score as a weighted average (equal weights for now)
    total_score = (tag_score + sector_score + industry_score + product_score) / 4

    return total_score


def similarity_score(row1, row2):
    location_score = location_code(row1, row2)
    name_score = name_similarity_score(row1, row2)
    contact_score = contact_similarity_score(row1, row2)
    description_score = description_similarity_score(row1, row2)
    business_score = business_similarity_score(row1, row2)

    # location is VERY important, I am going to "penalize" business further away
    # name is also important, remember we have grouped the business together, so if they come from the same domains
    # contact is VERY important, although we could have a "managing" business managing multiple business

    final_score = location_score*0.6 + name_score*0.1 + contact_score*0.2 + description_score*0.05 + business_score*0.05

    return final_score, location_score, name_score, contact_score, description_score, business_score