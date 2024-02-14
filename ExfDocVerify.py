# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 12:56:02 2024

@author: harshini
"""

from dash import dcc, html
from dash.dependencies import Input, Output, State
import io
import fitz  
import pandas as pd
import dash
import base64
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import openai
import json
import time
import os
from dotenv import load_dotenv


load_dotenv(".env.py")
openai_key = os.getenv("OPENAI_API_KEY")


#sample_contract_path = './assets/Complete_with_DocuSign_MSA-Exafluence-UnicaT.pdf'
#sample_checklist_path = './assets/ChecklistTest.xlsx'

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css'
]

# Custom colors
table_header_color = '#427D9D'
border_color = '#9BBEC8'
#pie_chart_colors = ['#164863', '#9BBEC8']

pie_chart_colors = ['#ff4757','#164863']
# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)



# Global variables to store file contents
contract_contents = None
checklist_contents = None
df = pd.DataFrame()
# Layout
app.layout = html.Div(children=[
    # Top bar with colored background for app name
    html.Div(
        className='app-header',
        style={
            'font-family': 'Roboto, sans-serif',
            'background-color': '#164863',
            'padding': '10px',
            'color': 'white',
        },
        #asset\logo.png
        children=[
                # Add the image icon here
                html.Div([
                    html.Img(src='./assets/logo.png', style={'position': 'absolute', 'left': '35%',  'top': '-25%', 'height': '15vh'}),
                    html.H1('ExfDocVerify', style={'margin': '0px', 'text-align': 'center'}),
                    html.Br(),
                    html.P('Bullet Proof Your Documents', style={'margin-bottom': '0rem', 'font-size': '2vh', 'text-align': 'center'}),
                ], style={'position': 'relative', 'height': '10vh'}),
            ]

    ),

    # File Upload Section
    html.Div(className='container', children=[
        html.Div(className='file-upload-container', children=[
            # contract File Upload
            html.Div(className='file-upload', children=[
                dcc.Upload(
                    id='upload-contract',
                    children=[
                        html.Div([
                            'Drag and Drop your ',
                            html.Strong('Documents'),
                            ' here Or click to browse',
                            html.Button('Upload File', style={
                                'margin-left': '550px',
                                'margin-top':' 3px',
                                'background-image': 'linear-gradient(-180deg, #37AEE2 0%, #1E96C8 100%)',
                                'border-radius': '.5rem',
                                'box-sizing': 'border-box',
                                'color': '#FFFFFF',
                                'font-size': '20px',
                                'justify-content': 'center',
                                'text-decoration': 'none',
                                'border': '0',
                                'cursor': 'pointer',
                                'user-select': 'none',
                                'height': '50px',
                                'width': '150px',
                                'lineHeight': '40px',
                            })
                        ])
                    ],
                    style={
                        'position':'relative',
                        'left': '-30px',
                        'width': '100%',
                        'height': '63px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'backgroundColor': '#9BBEC8',
                        'textAlign': 'center',
                        'margin': '20px',
                        'font-size': '20px'

                    },
                    multiple=False
                ),
               # Sample Contract Download Button with Download Icon
                html.Div([
                    dcc.Download(id="download-contract"),
                    dcc.Dropdown(
                   options=[
                            {'label': 'Contract', 'value': 'Complete_with_DocuSign_MSA-Exafluence-UnicaT.pdf'},
                            {'label': 'Invoice', 'value': 'Invoice.pdf'},
                            {'label': 'SOW', 'value': 'IT_Service_Provider_Healthcare_SOW.pdf'},
                     ],
                        value='',  # Default selected value, you can change this if needed
                        style={'margin-right':'18px'},  # Additional styling can be added here
                        id='demo-dropdown-documents'
                         ),
                    html.Button(
                        [
                            html.I(className="fas fa-download", style={'margin-right': '5px'}),
                            
                            #'Download Contract',
                        ],
                        id='btn-download-sample-contract',
                        n_clicks=0,
                        style={
                            'width': '52px',
                            'position': 'relative',
                            'left': '1295px',
                            'bottom': '42px',
                            'background-image': 'linear-gradient(-180deg, #37AEE2 0%, #1E96C8 100%)',
                            'border-radius': '.5rem',
                            'box-sizing': 'border-box',
                            'color': '#FFFFFF',
                            'font-size': '16px',
                            'text-decoration': 'none',
                            'border': '0',
                            'cursor': 'pointer',
                            'user-select': 'none',
                            'padding': '10px 20px',
                            'display': 'inline-block',
                        }
                    ),
                ]),
      

                dbc.Alert(
                    id="contract_alert",
                    is_open=False,
                    duration=2000,
                    fade=True,
                    style={'margin-left': '50px'}
                ),
            ], 
                #style={'padding-bottom': '30px'},
                ),

            # Checklist File Upload
            html.Div(className='file-upload', children=[
                dcc.Upload(
                    id='upload-checklist',
                    children=[
                        html.Div([
                            'Drag and Drop your ',
                            html.Strong('Checklist'),
                            ' file here Or click to browse',
                            html.Button('Upload File', style={
                                'margin-left': '550px',
                                'margin-top':' 9px',
                                'background-image': 'linear-gradient(-180deg, #37AEE2 0%, #1E96C8 100%)',
                                'border-radius': '.5rem',
                                'box-sizing': 'border-box',
                                'color': '#FFFFFF',
                                'font-size': '20px',
                                'justify-content': 'center',
                                'text-decoration': 'none',
                                'border': '0',
                                'cursor': 'pointer',
                                'user-select': 'none',
                                'height': '50px',
                                'width': '150px',
                                'lineHeight': '40px',
                            })
                        ])
                    ],
                    style={
                        'position':'relative',
                        'left': '-30px',
                        'width': '100%',
                        'height': '69px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'backgroundColor': '#9BBEC8',
                        'textAlign': 'center',
                        'margin': '20px',
                        'font-size': '20px',
                    },
                    multiple=False
                ),
               # Sample Checklist Download Button with Download Icon
               html.Div([
                   dcc.Download(id="download-checklist"),
                   dcc.Dropdown(
                   options=[
                            {'label': 'Contract', 'value': 'ContractChecklist.xlsx'},
                            {'label': 'Invoice', 'value': 'InvoiceChecklist.xlsx'},
                            {'label': 'SOW', 'value': 'SOWChecklist.xlsx'},
                     ],
                        value='',  # Default selected value, you can change this if needed
                        style={'margin-right':'18px'},  # Additional styling can be added here
                        id='demo-dropdown-checklist'
                         ),
                   html.Button(
                       [
                           html.I(className="fas fa-download", style={'margin-right': '5px'}),
                           #'Download Contract',
                       ],
                       id='btn-download-sample-checklist',
                       n_clicks=0,
                       style={
                           'width': '52px',
                           'position': 'relative',
                           'left': '1295px',
                           'bottom': '42px',
                           'background-image': 'linear-gradient(-180deg, #37AEE2 0%, #1E96C8 100%)',
                           'border-radius': '.5rem',
                           'box-sizing': 'border-box',
                           'color': '#FFFFFF',
                           'font-size': '16px',
                           'text-decoration': 'none',
                           'border': '0',
                           'cursor': 'pointer',
                           'user-select': 'none',
                           'padding': '10px 20px',
                           'display': 'inline-block',
                       }
                   ),
               ]),
     

                dbc.Alert(
                    id="checklist-success-alert",
                    is_open=False,
                    duration=2000,
                    fade=True,
                    style={'margin-left': '50px'}
                ),
            ], 
                #style={'padding-bottom': '50px'},
                ),

        ], style={
            'display': 'center',
            'padding-top': '30px',
            'padding-bottom':'10px'
        }),
        # Submit Button
        html.Button('Run Checklist', id='submit-button', n_clicks=0, style={
            'position': 'relative',
            'left': '560px',
            'top' :'-15px',
            'background-image': 'linear-gradient(-180deg, #37AEE2 0%, #1E96C8 100%)',
            'border-radius': '.5rem',
            'box-sizing': 'border-box',
            'color': '#FFFFFF',
            'font-size': '20px',
            'justify-content': 'center',
            'text-decoration': 'none',
            'border': '0',
            'cursor': 'pointer',
            'user-select': 'none',
            'width': '200px',  # Adjust the width as needed
            'height': '50px',  # Adjust the height as needed
        }),
        
        dbc.Alert(
            id="Nofile",
            is_open=False,
            duration=3000,
            fade=True,
            style={
           'width': '50%',  
           'background-color': '#ff4757',  
           'color': 'white',  
           'margin': 'auto',  
           'margin-top': '20px',  
           'text-align': 'center',
           'font-size':'19px'
       })
        

    ]),
            # Add loading spinner and results container
       dcc.Loading(
            id="loading",
            type="circle",
            children=[
                html.Div(id='loading-output'),
                # Collapsible div
                html.Div(id='printedContent'),
            ],
            style={'marginTop': '50px'}
        ),
  
])

            
                
            
            
            
#.......all functions.....

def process_pdf_content(pdf_data):
    try:
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        text = ""
        for page_number in range(doc.page_count):
            page = doc[page_number]
            text += page.get_text()
            print("from pdf_converter",text)
        return text
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None

def upload_excel_as_df(file_content):
    try:
        # Assuming file_content is bytes
        print("from upload as df_checklist:",pd.read_excel(io.BytesIO(file_content), engine='openpyxl'))
        return pd.read_excel(io.BytesIO(file_content), engine='openpyxl')
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

def get_total_pages_from_pdf(pdf_content):
    try:
        pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
        total_pages = pdf_document.page_count
        return total_pages
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def parse_openai_response(response_text):
    try:
        # Find the index where the JSON content begins
        json_start_index = response_text.find("{")
        
        # Check if JSON content is found
        if json_start_index != -1:
            # Extract the JSON content
            json_content = response_text[json_start_index:]
            
            # Remove any trailing characters after the JSON
            json_content = json_content.rstrip('\n').rstrip('```')
            
            # Parse the JSON
            response_data = json.loads(json_content)
        else:
            raise ValueError("No JSON content found in the response.")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return pd.DataFrame(columns=['S.No', 'Status', 'Category', 'Section Number', 'Analysis', 'Suggestions'])

    serial_no = 1
    rows = []

    for item, details in response_data.items():
        checklist_item_part = item.split(": ")[-1]
        row = {
            "S.No": details.get("S.No", serial_no),
            "Category": details.get("Category", "Unknown"),
            "Checklist Item": checklist_item_part,
            "Status": details.get("Status", ""),
            "Section Number": details.get("Section Number", ""),
            "Analysis": details.get("Analysis", ""),
            "Suggestions": details.get("Suggestions", "")
        }
        print("checklist items:",checklist_item_part)
        rows.append(row)
        serial_no += 1

    df = pd.DataFrame(rows)
    print(df)
    return df

def log_time(log_message, log_file_path='timelogs.txt'):
    with open(log_file_path, 'a') as log_file:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
        log_entry = f"{current_time} - {log_message}\n"
        log_file.write(log_entry)
        log_file.write("................")


#.......Functions for OpenAI ........

def query_openai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes contracts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0  
        )
        response_content = response['choices'][0]['message']['content']
        token_usage_info = response['usage']

        # Log the token count
        with open("token_consumption.txt", "a") as file:
            file.write("........................Token Usage Info.....................\n")
            file.write(f"Completion Tokens: {token_usage_info['completion_tokens']}\n")
            file.write(f"Prompt Tokens: {token_usage_info['prompt_tokens']}\n")
            file.write(f"Total Tokens: {token_usage_info['total_tokens']}\n")
            #file.write(".............................................................")

        return response_content, token_usage_info
    except Exception as e:
        print(f"An error occurred: {e}")
        return None 

def create_analysis_prompt(checklist_items, contract_text):
    prompt_text = {
    "question": f"Analyze the uploaded contract agreement  {contract_text} and determine the if the uploaded checklist items {checklist_items}  are fulfilled/satisfaction for each checklist item from the {checklist_items}. ",
    "context": f"You are a smart legal Assistant responsible  for analyzing and verifying if the contractual document text fulfills the checklist criteria with the checklist items {checklist_items}.",
    "information": "These are the details of output schema:"
                    'Checklist Item 1: provide the checklist items from uploaded Excel": {\n'
                    '    "S.No": "Same as checklist items",\n'
                    '   "Status": "based on the analysis: (Satisfied/Not satisfied)",'
                    '    "Category": "category of checklist item from uploaded checklist excel file {checklist_items}",\n'
                    f'    "Section Number": "section numbers from contract agreement  {contract_text} ",\n'
                    '    "Analysis": "Your analysis here",\n'
                    '    "Suggestions": "Your suggested amendment here"\n'
                    '  },\n'
                    ,
    "instruction":"Analyze each checklist item in detail, offering suggestions or improvements even if relevant clauses exist."
                    '"Verify that the document aligns precisely with the checklist criteria and matches the number of items and categories in the uploaded Excel file."'
                    '"Accurately specify the contract section numbers corresponding to each checklist item."'
                   
    
                  
                   
                   
                   '"Format the response in a structured JSON format with each item as a key, including analysis, suggestions, "'
                   ' "Do not include any other verbose explanations apart from the response format"'
                   ' Example of format with proper spacing:\n'
                   '{\n'
                   '  "Checklist Item 1: Clause for pre-existing IP": {\n'
                   '    "S.No": "1",\n'
                   '    "Status": "Satisfied",\n'
                   '    "Category": "Intellectual Property Rights",\n'
                   '    "Section Number": "4.1.1",\n'
                   '    "Analysis": "Your analysis here",\n'
                   '    "Suggestions": "Your suggested amendment here"\n'
                   '  },\n'
                   '  "Checklist Item 2: Limitation of Liability should be limited": {\n'
                   '    "S.No": "2",\n'
                   '    "Status": "Not satisfied",\n'
                   '    "Category": "Liability",\n'
                   '    "Section Number": "6",\n'
                   '    "Analysis": "Your analysis here",\n'
                   '    "Suggestions": "Your suggested amendment here"\n'
                   '  }\n'
                   '}\n\n'
    "ResponseFormat:\n"
                    'The extracted elements should be in the following JSON format: The output should be a\n'
                    'markdown code snippet formatted in the following schema, including the leading and '
                    '    trailing "```json" and "```":'
                    '    ```json'                       
                    '{\n'
                    '  "Checklist Item 1: "string"//Checklist category": {\n'
                    '    "S.No": "integer"//,\n'
                    '    "Status": "string"// "Satisfied/Not satisfied",\n'
                    '    "Category":  "string"//"Intellectual Property Rights",\n'
                    '    "Section Number":  "integer"//"If satisfied, provide the section number",\n'
                    '    "Analysis":  "string"//"Your analysis here",\n'
                    '    "Suggestions":  "string"//"Your suggested amendment here"\n'
                    '  },\n'
                    '}'
                    '```'
                     '  I want you to extract the features all the columns as a key-value pair like mentioned above '
                     '   in a JSON string'

                   ,}
      # You can add more information or prompts as needed
 

    for item in checklist_items:
        prompt_text["instruction"] += f"- {item}\n"
    prompt_text["instruction"] += ("\nContractual Agreement (Excerpt):\n" + contract_text + "\n\n"
                                   "Begin your JSON analysis below:\n-----------------------------\n")
    return json.dumps(prompt_text)


#.........callbacks.....

# Callback to update collapsible div contents on button click
@app.callback(
    Output("printedContent", "children"),
    [Input("submit-button", "n_clicks")],
    [State("upload-contract", "contents"),
     State("upload-checklist", "contents"),
     State("upload-contract", "filename"),
     State("upload-checklist", "filename")]
)
def update_collapsible_content(n_clicks, contract_contents, checklist_contents, contract_filename, checklist_filename):
    global df 
    if n_clicks is None or n_clicks <= 0:
        raise PreventUpdate

    # Check if contract file and checklist file are uploaded
    if contract_contents is None or checklist_contents is None:
        # Display alert if files are not uploaded
        alert_text = "Please upload Contract agreement  and Checklist file before running the checklist."
        return html.Div(dbc.Alert(
            id="Nofile",
            is_open=False,
            duration=4000,
            fade=True,
            children=alert_text,
            style={
            'width': '50%',  
            'background-color': '#ff4757',  
            'color': 'white',  
            'margin': 'auto',  
            'margin-top': '20px',  
            'text-align': 'center', 
            'font-size':'19px'
        }
        ))

    try:
        # Decode file contents 
        #pdf_content = base64.b64decode(contents.split(",")[1])
        contract_content_decoded = process_pdf_content(base64.b64decode(contract_contents.split(",")[1]))
        checklist_content_decoded = upload_excel_as_df(base64.b64decode(checklist_contents.split(",")[1]))
        
        # Extract information from filenames
        contract_file_name = contract_filename  # Use the contract filename as contract_file_name
        checklist_file_name = checklist_filename
        start_time = time.time() 
        
        
        contract_length = len(contract_content_decoded)
        print(f"The length of the contract text is: {contract_length} characters")

        
        
        # Generate the prompt for analysis
        prompt = create_analysis_prompt(checklist_content_decoded, contract_content_decoded)
        end_time = time.time()  # Record the end time
        time_taken = end_time - start_time
        print(f"Time taken for prompt: {time_taken} seconds")
        
        # Log time
        log_time(f"Time taken for prompt: {time_taken} seconds")
        
        
        
        
        start_time = time.time() 
        # Query OpenAI and print the response
        #response = query_openai(prompt)
        response, token_usage_info = query_openai(prompt)
        #print("RESPONSE!!!",response)
        end_time = time.time()  # Record the end time
        time_taken = end_time - start_time
        print(f"Time taken for OpenAI response: {time_taken} seconds")
        print("token  usage info:",token_usage_info)
        # Log time
        log_time(f"Time taken for OpenAI response: {time_taken} seconds")
        
      
        
       
        
        start_time = time.time() 
        # Parse OpenAI response
        analysis_results = parse_openai_response(response)
        end_time = time.time()  # Record the end time
        time_taken = end_time - start_time
        print(f"Time taken for parsing OpenAI response: {time_taken} seconds")
        
        # Log time
        log_time(f"Time taken for parsing OpenAI response: {time_taken} seconds")
        
        
        
        start_time = time.time() 
        # Update the DataFrame with the OpenAI analysis results
        if isinstance(analysis_results, pd.DataFrame) and not analysis_results.empty:
            df = analysis_results
            print("df after analysis:", df)
        else:
            df = pd.DataFrame(columns=['S.No', 'Status', 'Category', 'Section Number', 'Analysis', 'Suggestions'])
        end_time = time.time()  # Record the end time
        time_taken = end_time - start_time
        print(f"Time taken for updating df : {time_taken} seconds")
        
        # Log time
        log_time(f"Time taken for updating df : {time_taken} seconds")

        # Extract information for display
        num_checklist_items = len(checklist_content_decoded)  # Example: Number of rows in the checklist dataframe
        num_satisfied = df[df['Status'] == 'Satisfied'].shape[0]  # Example: Count of 'Satisfied' rows in the result dataframe
        num_unsatisfied = df[df['Status'] == 'Not satisfied'].shape[0]  # Example: Count of 'Unsatisfied' rows
        #num_SwithS = df[df['Status'] == 'Satisfied with suggestions'].shape[0] 
        # Extract page numbers from the contract agreement (assuming it's a PDF)
        print("type of pdf file:",type(contract_content_decoded))
        #pdf_content = base64.b64decode(contents.split(",")[1])
        total_pages = get_total_pages_from_pdf(base64.b64decode(contract_contents.split(",")[1]))
        print("total_pages")
        print("total_pages",total_pages)
            
        # Further processing of the OpenAI response and updating the displayed content
        updated_content = html.Div(
                children=[
                    dcc.Loading(
                        id="loading-output",
                        type="circle",
                        children=[
                            # Table
                            html.Div(
                                children=[
                                    html.H2('Results',
                                            style={'background-color': table_header_color, 'color': 'white',
                                                   'text-align': 'center',
                                                   'width': '80%', 'margin': '0 auto 5px'}),
                                    html.Table(
                                        # Header
                                        [html.Tr([html.Th(col, style={'font-size': '20px'}) for col in df.columns],
                                                 style={'background-color': '#55a2bc', 'color': 'white',
                                                        'text-align': 'center'})] +
                                        # Body
                                        [html.Tr([html.Td(value, style={'padding': '10px', 'border': f'1px solid {border_color}'})
                                                  for value in row]) for row in df.values],
                                        style={'width': '80%', 'margin': '0 auto', 'border-spacing': '0 10px',
                                               'text-align': 'left'},  # Center the table, add gap between rows
                                    ),
                                ],
                                style={'width': '97%', 'margin': '30px', 'text-align': 'center'}  # Center the entire content
                            ),
                            html.Div(
                                # Percentages Header
                                html.H2('Checklist Verification Statistics',
                                        style={'background-color': table_header_color, 'color': 'white',
                                               'text-align': 'center',
                                               'width': '80%', 'margin': '0 auto 5px'}),
                                style={'width': '97%', 'margin': '30px', 'text-align': 'center'}  # Center the entire content
                            ),
                            # Pie Chart
                            html.Div(
                                children=[
                                              
                                   html.Div(
                                                children=[
                                                    dcc.Markdown(
                                                        f"Contract File: **{contract_filename}**",
                                                        style={'border': '2px solid #2c8bc3', 'margin': '0 auto', 'text-align': 'center', 'width': '185px'}),
                                                    dcc.Markdown(
                                                        f"Total number of pages in document: **{total_pages}**",
                                                        style={'border': '2px solid #2c8bc3', 'margin': '0 auto', 'text-align': 'center', 'width': '185px'}),
                                                    dcc.Markdown(
                                                        f"Number of Checklist Items: **{num_checklist_items}**",
                                                        style={'border': '2px solid #2c8bc3', 'margin': '0 auto', 'text-align': 'center', 'width': '185px'}),
                                                    dcc.Markdown(
                                                        f"Number of Satisfied Items: **{num_satisfied}**",
                                                        style={'border': '2px solid #2c8bc3', 'margin': '0 auto', 'text-align': 'center', 'width': '185px'}),
                                                    dcc.Markdown(
                                                        f"Number of Not Satisfied Items: **{num_unsatisfied}**",
                                                        style={'border': '2px solid #2c8bc3', 'margin': '0 auto', 'text-align': 'center', 'width': '185px'}),
                                                   
                                                ],
                                                style={'display': 'flex', 'flex-direction': 'row', 'align-items': 'center'}
                                            ),
                                   
                                   html.Div(
                                       # Percentages Header
                                       html.H5('Percentage Variance ',
                                               style={ 'color': '#164863',
                                                      'text-align': 'center',
                                                      'width': '80%',
                                                      'margin': '5px auto 5px',
                                                      'border': '2px dashed #00b8ff',
                                                      'position': 'relative',
                                                      'padding': '10px',
                                                      'top': '37px',
                                                      'z-index': '3'
                                                      }),
                                       style={'width': '97%', 'margin': '30px', 'text-align': 'center'}  # Center the entire content
                                   ),
                                    # Donut graph
                                    dcc.Graph(
                                      
                                        figure={
                                            'data': [
                                                {
                                                    'labels': ['Not Satisfied', 'Satisfied'],
                                                        'values': df['Status'].value_counts().values.tolist(),
                                                        #'title':'Your contract',
                                                        'type': 'pie',
                                                        'hole': 0.5,
                                                        'textfont': {'size': 16},
                                                        'text': f"Total: {len(df)}",  # Add the total number of checklist items
                                                        'textposition': 'inside',  # Place the text inside the hole
                                                        'hoverinfo': 'label+percent+value',  # Display label, percentage, and value on hover
                                                        'marker': {'colors': pie_chart_colors},
                                                        'hoverlabel': {'font': {'size': 16}} 
                                                },
                                            ],
                                            'layout': {
                                                'legend': {'orientation': 'h', 'x': 0.4, 'y': -0.1,'font': {'size': 16}},
                                            },
                                           
                                        },
                                        style={'height': '540px','position': 'relative', 'right': '10px','bottom': '30px'}
                                    ),
                                ],
                                style={'padding-left':' 194px',    'width': '90%',   ' margin-top': '50px',   ' text-align': 'center',    'height': '20px'}
                            ),
                        ],
                    ),
                    html.Div([
                       
                        dcc.Download(id="download-dataframe-xlsx"),
                        html.Button(
                            [
                                html.I(className="fas fa-download", style={'margin-right': '5px'}),
                                'Download Results',
                            ],
                            id='btn_xlsx',
                            n_clicks=0,
                            style={
                                'margin-top': '44rem',
                               ' margin-right':' 2rem',
                                'background-image': 'linear-gradient(-180deg, #37AEE2 0%, #1E96C8 100%)',
                                'border-radius': '.5rem',
                                'box-sizing': 'border-box',
                                'color': '#FFFFFF',
                                'font-size': '20px',
                                'color':' rgb(255, 255, 255)',
                                'font-size': '20px',
                                'text-decoration': 'none',
                                'border': '0px',
                                'cursor': 'pointer',
                               ' user-select': 'none',
                                'width': '200px',
                                'height': '50px',
                                'z-index': '12'
                            }
                        ),
                    ],style={    'display':' flex',    'justify-content': 'center'}),
                ],
            )

        return updated_content


    except Exception as e:
        # Handle errors and display a generic error message
        #print(f"An error occurred: {e}")
        #error_message = "An error occurred during analysis. Please try again later."
        return html.Div( dbc.Alert(
            id="Nofile",
            is_open=False,
            duration=3000,
            fade=True,
            style={
           'width': '50%',  # Adjust the width as needed
           'background-color': '#ff4757',  # Change the background color to red
           'color': 'white',  # Change the text color if needed
           'margin': 'auto',  # Center the alert box horizontally
           'margin-top': '20px',  # Add margin-top to center vertically (adjust as needed)
           'text-align': 'center',  # Center the text inside the alert box
           'font-size':'19px'
       }
        ),)


#..............................
# contract upload callback
@app.callback(
    [Output("contract_alert", "is_open"), Output("contract_alert", "children")],
    [Input("upload-contract", "contents")],
    [State("upload-contract", "filename")],
)
def upload_contract_file(contents, filename):
    global contract_contents
    if not contents:
        raise PreventUpdate

    contract_contents = contents  # Update global variable
    print("contents contract:",type(contents))
    alert_text = f"{filename} uploaded successfully!"
    alert_color = "success"

    return contents, alert_text

# Checklist upload callback
@app.callback(
    [Output("checklist-success-alert", "is_open"), Output("checklist-success-alert", "children")],
    [Input("upload-checklist", "contents")],
    [State("upload-checklist", "filename")],
)
def upload_checklist_file(contents, filename):
    global checklist_contents
    if not contents:
        raise PreventUpdate

    checklist_contents = contents
    print("con checkl",type(contents))# Update global variable
    alert_text = f"{filename} uploaded successfully! "
    alert_color = "success"

    return contents, alert_text

# Callback to display an alert when no file is uploaded but "Run Checklist" is clicked
@app.callback(
    [Output("Nofile", "is_open"), Output("Nofile", "children")],
    [Input("submit-button", "n_clicks")],
    [State("upload-contract", "contents"),
     State("upload-checklist", "contents")]
)
def check_file_upload(n_clicks, contract_contents, checklist_contents):
    if n_clicks is None or n_clicks <= 0:
        raise PreventUpdate

    # Check if contract file and checklist file are uploaded
    if contract_contents is None or checklist_contents is None:
        # Display alert if files are not uploaded
        alert_text = "Please upload Contract agreement  and Checklist file before running the checklist."
        return True, alert_text
    else:
        # Continue with the checklist analysis
        return False, ""
#................................
# Callback to set the href for the contract download
@app.callback(
    Output("download-contract", "data"),
    [Input("btn-download-sample-contract", "n_clicks")],
    [State('demo-dropdown-documents', 'value')],
    prevent_initial_call=True
)
def download_sample_contract(n_clicks, value):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate

    sample_contract_path = f'./assets/{value}'
    with open(sample_contract_path, 'rb') as contract_file:
        contract_content = contract_file.read()

    return dcc.send_bytes(contract_content, f"{value}")

# Callback to set the href for the contract download
@app.callback(
    Output("download-checklist", "data"),
    [Input("btn-download-sample-checklist", "n_clicks")],
    [State('demo-dropdown-checklist', 'value')],
    prevent_initial_call=True
)
def download_sample_contract(n_clicks, value):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate

    sample_checklist_path = f'./assets/{value}'
    with open(sample_checklist_path, 'rb') as checklist_file:
        checklist_content = checklist_file.read()

    return dcc.send_bytes(checklist_content, f"{value}")


#.........................
@app.callback(
    Output("download-dataframe-xlsx", "data"),
    Input("btn_xlsx", "n_clicks"),
    prevent_initial_call=True,
)
def download_excel(n_clicks):
    global df 
    # Exclude the index column from the Excel file
    df_no_index = df.copy().reset_index(drop=True)  # Copy the DataFrame and reset the index
    return dcc.send_data_frame(df_no_index.to_excel, "mydf.xlsx", sheet_name="Sheet_name_1", index=False)




if __name__ == '__main__':
    app.run_server(debug=True, port='5000')
    
    
    
 
