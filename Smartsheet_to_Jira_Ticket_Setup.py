#This script creates all tickets that are needed for a new job, grabbing all specifications from Smartsheet

#	Compiled JQL = jql
jql = "issue in ("

#IMPORT PACKAGES
import time
import datetime
from datetime import date
import requests
import shutil

#SMARTSHEET PACKAGE IMPORT AND CREDENTIALS NEEDED FOR API CALLS
import smartsheet
ss = smartsheet.Smartsheet(**SMARTSHEET API KEY**)
ss.errors_as_exceptions(True)

#JIRA PACKAGE IMPORT AND CREDENTIALS NEEDED FOR API CALLS
from jira import JIRA
options = {'server': '**SERVER NAME**'}
username = **JIRA USERNAME**
api_key = **JIRA API KEY**
jira = JIRA(options, basic_auth=(username,api_key))

ticket_dictionary = {}
ticket_list = []

#time / current date setup
uniquedt = time.strftime("%Y%m%d-%H%M%S")
uniquedt2 = time.strftime("%Y-%m-%d")
now = datetime.datetime.now()

#need name of job to default in all scripts
print('What is the name of the job that should be used in the Jira tickets?')
job_name = input('> ')

#ticket_create function
def ticket_create(ticket_content):
    issue_dict = ticket_content
    global new_issue
    new_issue = jira.create_issue(fields=issue_dict)
    ticket_dictionary[str(ticket_content['summary'])] = new_issue.key
    print(str(ticket_content['summary']),": ",new_issue.key,"complete")
    #print(sorted(ticket_dictionary.keys())[-1],": ",ticket_dictionary[sorted(ticket_dictionary.keys())[-1]],"complete")
    ticket_list.append(new_issue.key)

#job onboarding profile variables
webfont = ''
icon_font = ''
logo = ''
nmls = ''
requested_footer = ''
requested_url = ''
requested_return = ''
contact_us = ''

#Job Onboarding Profile smartsheet setup under 'sheet'
import smartsheet
ss = smartsheet.Smartsheet('**SMARTSHEET SHEET ID**')
ss.errors_as_exceptions(True)
onboarding = '**SMARTSHEET SHEET ID**' 
sheet = ss.Sheets.get_sheet(onboarding)

for row in sheet.rows:
	if row.cells[0].value == job_name:
		attach = ss.Attachments.list_row_attachments(onboarding,row.id)
		logo = ss.Attachments.get_attachment(onboarding,attach.result[0].id)
		logo_url = logo.url
		logo_title = F'{job_name} logo.jpg'
		webfont = str(row.cells[10].value) #Preferred Web Fonts
		icon_font = str(row.cells[11].value) # Icon Font Choice
		nmls = str(row.cells[5].value)[:-2] 
		equal_housing = str(row.cells[22].value) 
		requested_footer = F'{job_name} {nmls}'
		contact_us = str(row.cells[6].value)
		requested_return = str(row.cells[7].value)
		brand_color = str(row.cells[8].value)
		accent_color = str(row.cells[9].value)

		#logo image extract
		pic = requests.get(logo_url,stream=True)
		print(pic) #presents status of pic - 200: success

		with open('logo.jpg', 'wb') as out_file: 
		    shutil.copyfileobj(pic.raw, out_file) #file downloads to location of script
		    shutil.copy('**FILEPATH FOR LOGO TO BE SAVED TO**',follow_symlinks=True)
		del pic

		#JOB IMPLEMENTATION EPIC

		#method of grouping Jira data based on https://jira.readthedocs.io/en/master/examples.html
		job_integration = {
		#TICKET NAME: (Job Name) Integration
			'project':{'key':'TES'},
			#'project':{'key':'BW'},
			'summary': F"{job_name} Integration",
			'description': F'''
			As a user, I want the templates branded and set up for my job setup.
			''' + cs_assignment,
			'issuetype':{'name':'Epic'},
			#priority:{'name':'Medium'},
			#'customfield_10006': F"{job_name} Integration" #epic name
		}


		#BRANDING

		design_branding = {
		#TICKET NAME: Design: (Job Name) Branding (https://promontech.atlassian.net/browse/LP-11271)
			'project':{'key':'**JIRA PROJECT**},
		    'summary': F"Design: {job_name} Branding", 
		    'description': F'''
		    As a UI developer, I want to have a prototype of the job-specific branding so that I can build the Branded Environment for {job_name}.
		    
		    ||Specifications||Job Detail||
			|Job Name|{job_name}|
			|Requested URL|{job_URL}|
			|Requested from/sender email address for emails|{requested_return}|
			|Webfont|{webfont}|
			|Icon font|{icon_font}|
			|Primary Brand Color|{brand_color}|
			|Accent Color|{accent_color}|
			|Logo|!{logo_title}|thumbnail!| 
			|Requested Footer|{requested_footer}|
		    ----
		    *Acceptance Criteria:*
		    # All environments reflect the above changes and/or any specific requests made related to the above configurations
		    ''' + cs_assignment,
		    'issuetype':{'name':'Story'}
		    #priority:{'name':'Medium'},
		    #'components': [{'name':'Design'}]
		}


		ui_branding = {
		#TICKET NAME: UI: (Job Name) Branding 
			'project':{'key':'**JIRA BOARD**},
			'summary': F"UI: {job_name} Branding", 
			'description': F'''
			As a user, I want the environment to be branded based on the mockup provided in the linked Design Ticket.
			----
			*Acceptance Criteria:*
			# The environment reflects the above specifications
			''',
			'issuetype':{'name':'**JIRA ISSUE TYPE**'},
			'priority':{'name':'**JIRA ISSUE PRIORITY**'},
			'components': [{'name':'**JIRA ISSUE COMPONENT**'}]
		}

		#create job_integration separately, for linking as epic at end of script
		ticket_create(job_integration)
		job_integration = new_issue.key
		ticket_list = []

		active_branding_env = [
			design_branding,
			ui_branding
			]

		for line in active_branding_env:
			ticket_create(line)

		attach = '/Users/kareygraham/Downloads/logo.jpg'
		jira.add_attachment(issue=ticket_dictionary[sorted(ticket_dictionary.keys())[-1]], attachment=attach,filename=F'{logo_title}')
		jira.add_attachment(issue=ticket_dictionary[sorted(ticket_dictionary.keys())[-2]], attachment=attach,filename=F'{logo_title}')

		jira.create_issue_link('Relates',ticket_dictionary[sorted(ticket_dictionary.keys())[-13]],ticket_dictionary[sorted(ticket_dictionary.keys())[-1]])

#print(sorted(ticket_dictionary))

if job_integration != '':
	for link in ticket_list:
		jira.create_issue_link('Cloners',job_integration,link)

#REVERT TICKETS' STATUS TO CANCELLED - Use transitions(issue) to see which statuses & associated IDs are available
ticket_list.append(job_integration)
for issue in ticket_list:
#	jira.transition_issue(issue,transition='41') 
	jql += str(issue) + str(",")

#SQL / Spreadsheet Buildout
jql = jql[:-1] + str(")")

import time
uniquedt = time.strftime("%Y%m%d-%H%M%S")

import sqlite3
conn = sqlite3.connect('job.db')
c = conn.cursor()

from openpyxl import Workbook
wb = Workbook()
ws_summary = wb.create_sheet("Summary",0)

c.execute("drop table ticket_templates")
c.execute('''create table ticket_templates 
	(project,
	issuename,
	summary,
	description,
	issuetype,
	priority,
	components,
	story_points
	)''')

for issue in jira.search_issues(jql, maxResults = None):
	project = str(issue.fields.project)
	issuename = str(issue)
	summary = str(issue.fields.summary)
	description = str(issue.fields.description)
	issuetype = str(issue.fields.issuetype)
	priority = str(issue.fields.priority)
	components = []
	for line in issue.fields.components:
		comp = str(line.name)
		components.append(comp)
	components = str('[%s]' % ', '.join(map(str,components)))[:-1][1:]
	story_points = str(issue.fields.customfield_10008)

	c.execute('''INSERT INTO ticket_templates
				values(?,?,?,?,?,?,?,?)''',(project,issuename,summary,description,issuetype,priority,components,story_points))

ws_summary['A1'] = 'Project'
ws_summary['B1'] = 'Issue Name'
ws_summary['C1'] = 'Summary'
ws_summary['D1'] = 'Description'
ws_summary['E1'] = 'Issue Type'
ws_summary['F1'] = 'Priority'
ws_summary['G1'] = 'Components'
ws_summary['H1'] = 'Story Points'

for row in c.execute('''
		SELECT
		project,issuename,summary,description,issuetype,priority,components,story_points
		from ticket_templates
		'''):
	ws_summary.append(row)

file1 = ('TicketTemplates_'+uniquedt+'.xlsx')
wb.save(file1)

conn.commit()
conn.close()
