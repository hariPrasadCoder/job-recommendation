import PyPDF2,pdfplumber

def cv_to_text():
    ## CV to texts
    CV_File=open('./resume.pdf','rb')
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
    return CV_Clear