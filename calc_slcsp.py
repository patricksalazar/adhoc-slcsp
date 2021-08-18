import pandas as pd
import math

# Constants
FILTER_METAL = 'Silver'

#########################################################################
# Merge DataFrames
# input: 
#   slcsp_df - input of zip codes, 
#   zips_df - rate area for codes
# output: 
#   merged_df - extracts the rate areas for the given zip codes
#########################################################################
def mergeDF(slcsp_df, zips_df):
    ## Merge SLCSP and Zip dataframes to create new merged dataframe
    merged_df = pd.merge(slcsp_df[['zipcode']], zips_df[['zipcode','state','rate_area']], on="zipcode")

    ### Remove duplicates in dataframe
    merged_df = merged_df.drop_duplicates()
    merged_df = merged_df.set_index('zipcode')

    ### Count how many rate areas there are and add the column
    merged_df['count'] = merged_df.groupby(['zipcode']).count().rename(columns={"rate_area": "count"})[["count"]]
    return merged_df


#########################################################################
# Get 2nd Lowest Rate based on a given Zip Grouping
# input: 
#   zip_group - zipcode, state, and rate area
#   Note: only pulls 'Silver' metals
# output: 
#   rate - 2nd lowest rate based on zip grouping
#########################################################################
def get2ndLowestRateByZip(zip_group, plans_df):
    # pull rates by state, rate_area and metal_level
    rates_df = plans_df[(plans_df.state == zip_group['state']) & (plans_df.rate_area == zip_group['rate_area']) & (plans_df.metal_level == FILTER_METAL)]
    
    # remove any duplicate rates and sort values
    rates_df = rates_df[['state', 'metal_level', 'rate_area', 'rate']].drop_duplicates().sort_values(by=['rate'])

    if rates_df is None or len(rates_df) <= 1:
        return None
    else:
        # extract 2nd lowest rate
        return rates_df.iloc[1,3]

def printResults(slcsp_df):
    for index, row in slcsp_df.iterrows():
        print(str(int(row['zipcode']))+','+('' if math.isnan(row['rate']) else row['rate'].astype(str)))

def main():
    ## Read csv files
    slcsp_df = pd.read_csv("slcsp.csv")
    zips_df = pd.read_csv("zips.csv")
    plans_df = pd.read_csv("plans.csv")

    # We are only looking at Silver
    plans_df = plans_df[plans_df.metal_level == FILTER_METAL]

    # merge the slcsp and zip dataframes and count rate areas
    merged_df = mergeDF(slcsp_df, zips_df)

    for index, row in merged_df.iterrows():
        # skip zipcodes where there is more than 1 rate area
        if row['count'] > 1:
            continue

        # find 2nd lowest rate based on zip data
        rate = get2ndLowestRateByZip(row, plans_df)

        # get rate
        slcsp_df.loc[slcsp_df['zipcode'] == index, "rate"]=rate
    
    # print out results
    printResults(slcsp_df)


if __name__ == "__main__":
    main()