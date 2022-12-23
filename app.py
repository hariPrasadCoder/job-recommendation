from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from src.cv_to_text import cv_to_text
from src.scrape_linkedin import scrape_linkedin
from src.match_percentage import match_percentage

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
    CV_Clear = cv_to_text()

    # Scrape linkedin data
    info_table = scrape_linkedin(job_title, location, num_of_pages)

    # Finding match percentage
    final_info_table = match_percentage(info_table, CV_Clear)

    x = zip(final_info_table['Job_title'], final_info_table['Company'], final_info_table['Job_posted_date'], final_info_table['Link'], final_info_table['Matching_percentage'])
        
    return render_template('index.html', output_data=x)

if __name__ == '__main__':

    app.debug = True
    app.run()