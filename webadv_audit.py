#Sean Fritz - s1346012
#Desc
#webadv_audit.py
#Due 4/2/24

#To run:
# python c:/Users/Sean/Desktop/PythonGroupProject/webadv_audit.py s1346012

#TODO:
#Complete audit scraping
#Implement proper exit code if password is incorrect
#Implement save to .pdf flag

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import getpass
import time
import sys
import bs4
from bs4 import BeautifulSoup
import re
import fpdf

#Define help function for below conditionals
def help():
    print("""Usage: python3 webadv_audit.py [--option] [student id, e.g., s1100841]	
   where [--option] can be:
      --help:	     Display this help information and exit
      --save-pdf: Save PDF copy of entire audit to the current folder
                  as audit.pdf"""
)

#Check if argument flagged help
if ((sys.argv[1] == "--help") and (len(sys.argv) != 3)):
    help()
    exit()

#Check for bad argument
if not re.match(r'^s[0-9]{7}$', sys.argv[2]):
    help()
    exit()

#Get commandline argument studentID and password
studentID = sys.argv[2]
#Use getpass to get password
password = getpass.getpass('Enter password for ' + studentID + ': ')

#Check for "--save-pdf" flag
#Implementation: After html_src is found, check if true > print to pdf if so
print_pdf = False
if (sys.argv[1] == "--save-pdf"):
    print_pdf = True  

#If argvs are proper:
#Create webdriver instance
driver = webdriver.Chrome()

#Open webpage on webdriver
driver.get('http://webadvisor.monmouth.edu')
assert 'WebAdvisor Main Menu' in driver.title

#Test wait time
time.sleep(1)

#Find login link
driver.find_element(By.ID, 'acctLogin').click()

#Test wait time
time.sleep(1)

#Sign in with username
input_field = driver.find_element(By.ID, "userNameInput")
input_field.clear()
input_field.send_keys(studentID)
input_field.send_keys(Keys.ENTER)

#Test wait time
time.sleep(1)

#Sign in with password
input_field = driver.find_element(By.NAME, 'Password')
input_field.clear()
input_field.send_keys(password)
input_field.send_keys(Keys.ENTER)

#Test wait time
time.sleep(1)

#AFTER LOGGING IN
#Click on Students Menu
driver.find_element(By.CLASS_NAME, 'WBST_Bars').click()

#Test wait time
time.sleep(1)

#Click Academic Audit/Pgm Eval Menu
driver.find_element(By.XPATH, "//span[.='Academic Audit/Pgm Eval']").click()

#Test wait time
time.sleep(1)

#Click Radio Button
driver.find_element(By.ID, "LIST_VAR1_1").click()

#Test wait time
time.sleep(1)

#Click Submit button - poll Academic Audit
driver.find_element(By.NAME, 'SUBMIT2').click()

#Test wait time
time.sleep(1)

#Save HTML source
html_content = driver.page_source
# print(html_content)    #Print HTML Source - for testing

#init bs4 info gathering here:
audit_soup = bs4.BeautifulSoup(html_content, 'html.parser')

#Parse Name:
#<td class="PersonName"><strong>Student: Sean T. Fritz (1346012)</strong></td>
name_tags = audit_soup.find('td', class_="PersonName")  #Parse name + tags
name = name_tags.text                                   #Turn bs4.tag object into a string object
student_name = name.replace("Student: ", "")            #Remove unnecessary bits here

#Parse Program:
#<td><span class="ReqName">1: Comp. Science BA (CS.BA.MAJ.OUT.22)<b class="StatusInProgress"> (In progress)</b></span></td>
program_tags = audit_soup.find('span', class_="ReqName")  #Parse name + tags
program = program_tags.text                               #Turn bs4.tag object into a string object
program_name = program.replace("1: ", "")                 #Remove some unnecessary bits

#Parse Catalog
#<td class="Bold">Catalog: </td><td>C2223</td>
catalog_match = re.search(r'Catalog: </td><td>(.+?)</td>', html_content)    #Use regex to find catalog
catalog = catalog_match.group(1)

#Parse Anticipated Completion Date:
#Anticipated<br>Completion Date: </td><td valign="bottom">05/14/25</td>
comp_date_match = re.search(r'Anticipated<br>Completion Date: </td><td valign="bottom">([0-9]{2}/[0-9]{2}/[0-9]{2})</td>', html_content)
comp_date = comp_date_match.group(1)

#Parse advisor and class level:
advisor_match = re.search(r'<br> (Advisor: .+?) <br> (Class Level: .+?) <br>', html_content)
advisor = advisor_match.group(1)
class_level = advisor_match.group(2)

#Parse Graduation requirements that are "In Progress":
# <td align="right" width="5%">14.</td><td align="left" width="15%">CS-438</td><td align="left" width="20%">Operating Syst Analysis</td><td align="left" width="18%"></td><td align="left" width="10%">24/SP</td><td align="left" width="7%"></td><td align="right" width="10%">3</td><td width="5%"></td><td align="left" width="10%">
# <table border="0" align="left">
# <tbody><tr>
# <td align="left">*IP</td>
#use re.findall?

#Parse Graduation requirements that are "Not Started"

#Parse Credits earned at a 200+ level (out of 54 credits required):

#Parse Total credits earned (out of 120 credits required; including current credits):
#<td class="Bold" align="left">Overall Credits:</td><td>120.00</td><td>97.00</td><td>23.00</td><td>15.00</td><td>8.00</td>
total_credits_match = re.search(r'<td class="Bold" align="left">Overall Credits:</td><td>120.00</td><td>([0-9]{2}.[0-9]{2})</td><td>23.00</td><td>15.00</td><td>8.00</td>', html_content)
credits_earned = total_credits_match.group(1)


#Print final report!
print("\n\nAcademic Audit Summary")
print("======================")
print("Name: " + student_name)
print("Program: " + program_name)
print("Catalog: " + catalog)
print("Anticipated Completion Date: " + comp_date)
print(advisor)
print(class_level)
print("\nGraduation requirements that are \"In Progress\": INCOMPLETE")
print("\nGraduation requirements that are \"Not Started\": INCOMPLETE")
print("\nCredits earned at a 200+ level (out of 54 credits required): INCOMPLETE")
print("Total Credits Earned: " + credits_earned)

if print_pdf:
    print("Printing PDF!")
    #Create and init pdf page
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    #Add content to .pdf
    pdf.cell(200,10,txt="Academic Audit Summary", ln=1, align="L")
    pdf.cell(200,10,txt="======================", ln=1, align="L")
    pdf.cell(200,10,txt="Name: " + student_name, ln=1, align="L")
    pdf.cell(200,10,txt="Program: " + program_name, ln=1, align="L")
    pdf.cell(200,10,txt="Catalog: " + catalog, ln=1, align="L")
    pdf.cell(200,10,txt="Anticipated Completion Date: " + comp_date, ln=1, align="L")
    pdf.cell(200,10,txt=advisor, ln=1, align="L")
    pdf.cell(200,10,txt=class_level, ln=1, align="L")
    # pdf.cell(200,10,txt="Academic Audit Summary", ln=1, align="L")
    # pdf.cell(200,10,txt="Academic Audit Summary", ln=1, align="L")
    # pdf.cell(200,10,txt="Academic Audit Summary", ln=1, align="L")
    pdf.cell(200,10,txt="Total Credits Earned: " + credits_earned, ln=1, align="L")
    
    #Output pdf file
    pdf.output("audit.pdf")
    