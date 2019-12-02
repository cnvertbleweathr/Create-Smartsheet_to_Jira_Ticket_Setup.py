#IMPORT PACKAGES
import time
import datetime
from datetime import date
import json

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

#USER ENTERS THE NAME FOR THE JOB
print('What is the name of the job?')
job_name = input('> ')

#CONTENT DEFAULTS DICTIONARY - This dictionary will be used to specify default content, allow for modifications should they exist within Smartsheet, and referenced when building our JSON file 
content_vars = {
'DEFAULT_CONTENT_SECTION1_SUBJECT' : job_name + '''**DEFAULT CONTENT**''',
'DEFAULT_CONTENT_SECTION1_H1' : job_name + "**DEFAULT CONTENT**",
'DEFAULT_CONTENT_SECTION1_BODY' : '''**DEFAULT CONTENT**''' + job_name +'''!**DEFAULT CONTENT**''',
'DEFAULT_CONTENT_SECTION1_CTA' : '''**DEFAULT CONTENT**''',

'DEFAULT_CONTENT_SECTION2_SUBJECT' : job_name + '''**DEFAULT CONTENT**''',
'DEFAULT_CONTENT_SECTION2_H1' : job_name + '''**DEFAULT CONTENT**''',
'DEFAULT_CONTENT_SECTION2_BODY' :'''**DEFAULT CONTENT**''',
'DEFAULT_CONTENT_SECTION2_CTA' : '''**DEFAULT CONTENT**'''',

'DEFAULT_CONTENT_SECTION3_SUBJECT' : '''**DEFAULT CONTENT**''',
'DEFAULT_CONTENT_SECTION3_H1' : '''**DEFAULT CONTENT**''',
'DEFAULT_CONTENT_SECTION3_BODY' : '''**DEFAULT CONTENT**''',
'DEFAULT_CONTENT_SECTION3_CTA' : '''**DEFAULT CONTENT**''',

#SMARTSHEET
#Section overview
onboarding = **SHEET ID TO REFERENCE JOB_NAME TO ESTABLISH VARIABLES**
sheet = ss.Sheets.get_sheet(onboarding)
for row in sheet.rows:
	if row.cells[0].value == job_name:
		global VARIABLE1, VARIABLE2
		VARIABLE1 = str(row.cells[0].value)
		VARIABLE2 = str(row.cells[6].value)[:-2]
    
configurations = **SHEET ID TO REFERENCE JOB_NAME TO ESTABLISH SECOND SET OF VARIABLES**
sheet = ss.Sheets.get_sheet(configurations)
for row in sheet.rows:
#LOOP THROUGH ALL ROWS OF SHEET TO CHECK IF FIRST COLUMN OF SHEET CONTAINS JOB_NAME
	if row.cells[0].value == job_name: 
		global VARIABLE3, VARIABLE4, VARIABLE5, VARIABLE6, VARIABLE7, VARIABLE8, VARIABLE9
		VARIABLE3 = row.id
		VARIABLE4 = str(row.cells[3].value)
		VARIABLE5 = str(row.cells[4].value) 
		VARIABLE6 = str(row.cells[5].value)
		VARIABLE7 = str(row.cells[6].value)
		VARIABLE8 = str(row.cells[7].value)
		VARIABLE9 = str(row.cells[80].value)

#IF THERE IS NO RESPONSE ILICITED, SMARTSHEET SENDS A DEFAULT VALUE OF "NONE", HENCE THE COMPARISON OF A VARIABLE BEING LONGER THAN 4 CHARACTERS. SHOULD MORE THAN 4 CHARACTERS BE SPECIFIED THE VALUE WITHIN THE DICTIONARY CHANGES.  
		if len(str(row.cells[8].value)) > 4:
			content_vars['DEFAULT_CONTENT_SECTION1_SUBJECT'] = str(row.cells[8].value)
		if len(str(row.cells[9].value)) > 4:
			content_vars['DEFAULT_CONTENT_SECTION1_H1'] = str(row.cells[9].value)		
		if len(str(row.cells[10].value)) > 4:
			content_vars['DEFAULT_CONTENT_SECTION1_BODY'] = str(row.cells[10].value)
		
		if len(str(row.cells[11].value)) > 4:
			content_vars['DEFAULT_CONTENT_SECTION2_SUBJECT'] = str(row.cells[11].value)
		if len(str(row.cells[12].value)) > 4:
			content_vars['DEFAULT_CONTENT_SECTION2_H1'] = str(row.cells[12].value)
		if len(str(row.cells[13].value)) > 4:
			content_vars['DEFAULT_CONTENT_SECTION2_BODY'] = str(row.cells[13].value)

#CONVERTS DICTIONARY INTO VARIABLES REFERENCING STRINGS
		locals().update(content_vars)

#INSERT VARIABLES INTO JSON
		content_json = '''
	    {
	      "defaultTemplateContent": {
	        "content": {
	          "greeting": "Hello"
	        },
	        "company": {
	          "specification1": "mailto:'''+VARIABLE1+'''",
	          "specification2": "'''+VARIABLE2''",
	          "specification3": "'''+VARIABLE3'''",
	          "specification4": '''VARIABLE4'',
	          "specification5": "Phone: '''+VARIABLE4'''",
	          "specification6": "'''+VARIABLE5''',",
	          "specification7": "'''+VARIABLE6'''",
	          "specification8": "'''+VARIABLE7+'''",
            "specification9": "'''+VARIABLE8'''"
	        }
	      },
	      "templates": [
	        {
	          "templateBaseName": "whitefall-loan-officer-to-applicant",
	          "actions": {
	            "CO_APPLICANT_HAS_APPLIED" : {
	              "subject": "DEFAULT_CONTENT_SECTION1_SUBJECT",
	              "content": {
	                "heading": "DEFAULT_CONTENT_SECTION1_H1",
	                "btn-label": "Open Borrower Wallet",
	                "btn-link": "{{login-url}}",
	                "cta": "DEFAULT_CONTENT_SECTION1_CTA",
	                "body": [
	                  {
	                    "text": "DEFAULT_CONTENT_SECTION1_BODY"
	                  }
	                ]
	              }
	            }
	          }
	        }

#SAVE JSON FILE TO MACHINE AND ATTACH TO ROW CONTAINING JOB SPECIFICATIONS WITHIN SMARTSHEET
		json_file_name = job_name+'_content_configs.json'
		with open (json_file_name,'w') as outfile:
			outfile.write(content_json)
		json_file_path = **FILEPATH THAT WILL BE REFERENCED WHEN BUILDING OUT THE JIRA TICKET**
		updated_attachment = ss.Attachments.attach_file_to_row(configurations,CLIENT_SS_ROW,(json_file_name, open(json_file_path, 'rb'), 'application/msword'))
		print('\nFile attached to '+job_name+' row in Email Configurations in Smartsheet')

#JIRA
		content_ticket = {
			#TICKET NAME: (Job Name): Requested Content Configurations
				'project':{'key':'**PROJECT KEY**'},
				'summary': F"{job_name}: **TICKET NAME**",
				'description': F'''
				{job_name} **JIRA TICKET BODY CONTENT**
				
	    		[^{json_file_name}]
				''',
				'issuetype':{'name':'**TICKET TYPE**'}
				#priority:{'name':'**TICKET PRIORITY**'}
			}

		#CREATE JIRA TICKET AND ATTACH JSON FILE TO TICKET
		content_config_jira = jira.create_issue(fields=content_ticket)
		attach = json_file_path
		jira.add_attachment(issue=content_config_jira, attachment=attach,filename=json_file_name)

		print('\nTicket '+str(content_config_jira)+' created.')
