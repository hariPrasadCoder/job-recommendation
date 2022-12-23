import requests
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def match_percentage(info_table, CV_Clear):
    # Finding match percentage
    headers = {'User-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}
    match_percent = []
    for l in info_table['Link']: 
        
        # extract job description from 2nd webpage (ie, main page for each job post)
        r = requests.get(l, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")
        job_description = soup.find('div', class_='show-more-less-html__markup show-more-less-html__markup--clamp-after-5').text.replace("\n","")
        
        # calculate match percentage 
        Match_Test = [CV_Clear,job_description]
        cv = CountVectorizer()
        count_matrix = cv.fit_transform(Match_Test)
        MatchPercentage = cosine_similarity(count_matrix)[0][1]*100
        match_percent.append(MatchPercentage)

    match_percent = pd.DataFrame(match_percent, columns = ['Matching_percentage'])
    final_info_table = pd.concat([info_table, match_percent], axis=1)
    final_info_table = final_info_table.sort_values(by = 'Matching_percentage', axis = 0, ascending=False)

    final_info_table = final_info_table.nlargest(10,['Matching_percentage'])

    return final_info_table