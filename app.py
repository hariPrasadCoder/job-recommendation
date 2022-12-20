from flask import Flask, render_template, request, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
import PyPDF2,pdfplumber
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import urllib
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import pandas as pd
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/results",  methods=['POST'])
def results():
    job_title = str(request.form['job_title'])
    location = str(request.form['location'])
    num_of_pages = int(request.form['num_of_pages'])
    f = request.files['file']
    f.save(secure_filename('resume.pdf'))

    ## CV to texts
    CV_File=open('resume.pdf','rb')
    Script=PyPDF2.PdfFileReader(CV_File)
    pages=Script.numPages

    Script = []
    with pdfplumber.open(CV_File) as pdf:
        for i in range (0,pages):
            page=pdf.pages[i]
            text=page.extract_text()
            # print (text)
            Script.append(text)
            
    Script=''.join(Script)
    CV_Clear = Script.replace("\n","").replace('●', "")

    # Scrape linkedin data

    info = []
    headers = {'User-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}

    for page in range(num_of_pages):
        getVars = {'keywords' : job_title, 'location' : location ,'sort' : 'date', 'start': str(num_of_pages*10)}
        url = ('https://www.linkedin.com/jobs/search?' + urllib.parse.urlencode(getVars))
        r = requests.get(url, headers=headers, verify=False)
        html = r.content
        print(html)
        soup = BeautifulSoup(html, "html.parser")
        jobs = soup.find_all('div', class_ = 'base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card')
        for job in jobs:
            title = str(job.find('h3', class_='base-search-card__title').text.strip())
            company = str(job.find('h4', class_='base-search-card__subtitle').text.strip())
            post_date = datetime.strptime(job.find('time')['datetime'], '%Y-%m-%d').date()
            link = job.find('a', class_='base-card__full-link')['href']
            
            info.append([title,company,post_date,link])
        
    info_dict_list = defaultdict(list)

    cols = ['Job_title','Company','Job_posted_date','Link']
    info_table = pd.DataFrame(info, columns = cols)
    # sort by post date
    info_table = info_table.sort_values(by = 'Job_posted_date', ascending = False).reset_index(drop=True)
    x = zip(info_table['Job_title'], info_table['Company'], info_table['Job_posted_date'], info_table['Link'])

    # Finding match percentage
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

    final_info_table.nlargest(10,['Matching_percentage'])

    x = zip(final_info_table['Job_title'], final_info_table['Company'], final_info_table['Job_posted_date'], final_info_table['Link'], final_info_table['Matching_percentage'])
        
    return render_template('index.html', output_data=x)

if __name__ == '__main__':

    app.debug = True
    app.run()