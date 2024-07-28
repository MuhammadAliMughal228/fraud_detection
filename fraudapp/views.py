from django.shortcuts import render 
from django.http import HttpResponse
import pandas as pd

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .serializers import *
import boto3
from io import StringIO
import warnings
import numpy as np
from smart_open import open
import gzip
from io import BytesIO
from json import loads, dumps

from pathlib import Path
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain.embeddings import BedrockEmbeddings
from langchain.llms import Bedrock
from langchain.vectorstores import Cassandra
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain.document_loaders import TextLoader
from langchain_aws import ChatBedrock
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import joblib
import pickle
import json
import faiss
import re
import os , io


def home(request):
    return HttpResponse("hello world")

warnings.filterwarnings("ignore", category=UserWarning)
class ChartsData(APIView):
    def get(self , request):

        # Create a session with explicit credentials

        session = boto3.Session(
            aws_access_key_id= settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY,
            region_name= settings.AWS_REGION
        ) 
        s3 = session.client('s3')
        # Specify the bucket name and the key (file path within the bucket)
        bucket_name = 'esse-fraudguard'
        key = 'dataset/dataset_with_labels.csv'
        # Get the object from S3
        response = s3.get_object(Bucket=bucket_name, Key=key)
        buffer = []
            # Read the object in chunks
        for i, line in enumerate(response['Body'].iter_lines()):
            if i >= 2000:
                break
            buffer.append(line.decode('utf-8'))

        # Join the lines into a single string
        csv_content = '\n'.join(buffer)
        df = pd.read_csv(StringIO(csv_content))

        ################################################################
        # PIE CHART
        loan_status_counts = df['LoanStatus'].value_counts().to_dict()
        business_type_counts = df['BusinessType'].value_counts().to_dict()
        race_counts = df['Race'].value_counts().to_dict()
        ethnicity_counts = df['Ethnicity'].value_counts().to_dict()

        # Combine all the counts into one dictionary
        combined_counts = {**loan_status_counts, **business_type_counts, **race_counts, **ethnicity_counts}
        # Prepare data for Chart.js
        # print("Pie Chart complete")
        

        # ################################################################
        # # Prepare data for each bar chart component
        loan_status_counts = df['LoanStatus'].value_counts().to_dict()
        borrower_state_counts = df['BorrowerState'].value_counts().to_dict()
        business_type_counts = df['BusinessType'].value_counts().to_dict()
        race_counts = df['Race'].value_counts().to_dict()
        ethnicity_counts = df['Ethnicity'].value_counts().to_dict()
        gender_counts = df['Gender'].value_counts().to_dict()
        veteran_counts = df['Veteran'].value_counts().to_dict()

        # print("bar Chart complete")
        
        # ################################################################

        
        # # LineChart

        # # Convert the 'DateApproved' column to datetime with dayfirst=True
        df['DateApproved'] = pd.to_datetime(df['DateApproved'], dayfirst=True)

        # Sort the dataframe by 'DateApproved'
        df = df.sort_values('DateApproved')

        # Prepare data for DateApproved vs ApprovalDiff
        approval_diff_data = df[['DateApproved', 'ApprovalDiff']].dropna()

        approval_diff_labels = approval_diff_data['DateApproved'].dt.strftime('%Y-%m-%d').tolist()
        approval_diff_values = approval_diff_data['ApprovalDiff'].tolist()

        # Prepare data for DateApproved vs ForgivenessAmount
        forgiveness_amount_data = df[['DateApproved', 'ForgivenessAmount']].dropna()

        forgiveness_amount_labels = forgiveness_amount_data['DateApproved'].dt.strftime('%Y-%m-%d').tolist()
        forgiveness_amount_values = forgiveness_amount_data['ForgivenessAmount'].tolist()

        # # print the JSON data for the line charts
        
        # print("line Chart complete")
        

        #################################################################

        # HistogramData

        
        # Function to clean the data by removing infinite values
        def clean_data(data):
            return data[~np.isinf(data)].dropna().tolist()

        # Prepare data for InitialApprovalAmount distribution
        initial_approval_amount_data = clean_data(df['InitialApprovalAmount'])

        # Prepare data for ForgivenessAmount distribution
        forgiveness_amount_data = clean_data(df['ForgivenessAmount'])

        # Prepare data for PROCEED_Per_Job distribution
        proceed_per_job_data = clean_data(df['PROCEED_Per_Job'])

        # Calculate the histogram data using pandas
        initial_approval_hist, initial_approval_bins = pd.cut(initial_approval_amount_data, bins=10, retbins=True, labels=False)
        initial_approval_hist_data = pd.Series(initial_approval_hist).value_counts().sort_index().tolist()

        forgiveness_hist, forgiveness_bins = pd.cut(forgiveness_amount_data, bins=10, retbins=True, labels=False)
        forgiveness_hist_data = pd.Series(forgiveness_hist).value_counts().sort_index().tolist()

        proceed_per_job_hist, proceed_per_job_bins = pd.cut(proceed_per_job_data, bins=10, retbins=True, labels=False)
        proceed_per_job_hist_data = pd.Series(proceed_per_job_hist).value_counts().sort_index().tolist()

        # Create bins labels
        initial_approval_bins_labels = [f"{round(b, 2)} - {round(initial_approval_bins[i+1], 2)}" for i, b in enumerate(initial_approval_bins[:-1])]
        forgiveness_bins_labels = [f"{round(b, 2)} - {round(forgiveness_bins[i+1], 2)}" for i, b in enumerate(forgiveness_bins[:-1])]
        proceed_per_job_bins_labels = [f"{round(b, 2)} - {round(proceed_per_job_bins[i+1], 2)}" for i, b in enumerate(proceed_per_job_bins[:-1])]

        # # print the JSON data for the histograms
        # print("Histogram ready")
       

        # ################################################################

        # Heatmap
        numerical_columns = ['InitialApprovalAmount', 'ForgivenessAmount', 'UndisbursedAmount', 'JobsReported']

        # Calculate the correlation matrix
        correlation_matrix = df[numerical_columns].corr()

        # # print the correlation matrix as JSON
        correlation_json = correlation_matrix.to_dict()

        

        # print("heat map ready")

        
        # ################################################################
        # Box Plot

        # Prepare the data for box plots
        columns_of_interest = ['InitialApprovalAmount', 'ForgivenessAmount', 'PROCEED_Per_Job']
        categorical_variable = 'LoanStatus'

        # Function to calculate quartiles and outliers
        def calculate_boxplot_data(df, group_col, value_col):
            grouped_data = df.groupby(group_col)[value_col]
            boxplot_data = {}
            for name, group in grouped_data:
                q1 = group.quantile(0.25)
                q3 = group.quantile(0.75)
                iqr = q3 - q1
                lower_fence = q1 - 1.5 * iqr
                upper_fence = q3 + 1.5 * iqr
                outliers = group[(group < lower_fence) | (group > upper_fence)]
                boxplot_data[name] = {
                    'min': group.min(),
                    'q1': q1,
                    'median': group.median(),
                    'q3': q3,
                    'max': group.max(),
                    'outliers': outliers.tolist()
                }
            return boxplot_data

        # Generate box plot data for each column
        box_plot_data = {}
        for column in columns_of_interest:
            box_plot_data[column] = calculate_boxplot_data(df, categorical_variable, column)
        
        

        # print("Box plot ready")

        # ################################################################

        # # Scatter Plot

        initial_approval_vs_forgiveness = df[['InitialApprovalAmount', 'ForgivenessAmount']].dropna().to_dict(orient='list')

        # Prepare data for TOTAL_PROCEED vs PROCEED_Per_Job
        total_proceed_vs_proceed_per_job = df[['TOTAL_PROCEED', 'PROCEED_Per_Job']].dropna().to_dict(orient='list')

        # # print the JSON data for the scatter plots
        

        # print("scatter plot ready")
        # ################################################################

        
        # # water fall

        component_columns = [
            'UTILITIES_PROCEED',
            'PAYROLL_PROCEED',
            'MORTGAGE_INTEREST_PROCEED',
            'RENT_PROCEED',
            'REFINANCE_EIDL_PROCEED',
            'HEALTH_CARE_PROCEED',
            'DEBT_INTEREST_PROCEED'
        ]

        # Calculate the sum of each component and the total proceed
        components_sum = df[component_columns].sum().to_dict()
        total_proceed = df['TOTAL_PROCEED'].sum()

        # Prepare the waterfall data
        waterfall_data = {'TOTAL_PROCEED': total_proceed}
        waterfall_data.update(components_sum)

        
        
        BarChartRecord = {
            'pie_records': {
                'pie_labels': list(combined_counts.keys()),
                'pie_values': list(combined_counts.values())
            },
            'loan_status': {
                'labels': list(loan_status_counts.keys()),
                'values': list(loan_status_counts.values())
            },
            'borrower_state': {
                'labels': list(borrower_state_counts.keys()),
                'values': list(borrower_state_counts.values())
            },
            'business_type': {
                'labels': list(business_type_counts.keys()),
                'values': list(business_type_counts.values())
            },
            'race': {
                'labels': list(race_counts.keys()),
                'values': list(race_counts.values())
            },
            'ethnicity': {
                'labels': list(ethnicity_counts.keys()),
                'values': list(ethnicity_counts.values())
            },
            'gender': {
                'labels': list(gender_counts.keys()),
                'values': list(gender_counts.values())
            },
            'veteran': {
                'labels': list(veteran_counts.keys()),
                'values': list(veteran_counts.values())
            },
            'line_chart_approval': {
                'labels': approval_diff_labels,
                'values': approval_diff_values
            },
            'line_chart_forgiveness': {
                'labels': forgiveness_amount_labels,
                'values': forgiveness_amount_values
            },
            'histogram_initial': {
                'bins': initial_approval_bins_labels,
                'values': initial_approval_hist_data
            },
            'histogram_forgiveness': {
                'bins': forgiveness_bins_labels,
                'values': forgiveness_hist_data
            },
            'histogram_proceed': {
                'bins': proceed_per_job_bins_labels,
                'values': proceed_per_job_hist_data
            },
            'HeatMapProceed': {
                'bins': proceed_per_job_bins_labels,
                'values': proceed_per_job_hist_data
            }
        }

        # print("Data prepared for serialization")

        serializer = BarChartRecordSerializer(data=BarChartRecord)

        if serializer.is_valid():
            return Response({'status': 200, 'message': 'Charts Fetch Sucessfully', 'payload': serializer.data}, status = status.HTTP_200_OK )       
        # print("Serializer errors:")
        # print(serializer.errors) 
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileReaderAPIView(APIView):
    def get(self, request):
        try:
            # Create a session with explicit credentials
            session = boto3.Session(
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            s3 = session.client('s3')
            # print("S3 client created successfully")

            # Specify the bucket name and the key (file path within the bucket)
            bucket_name = 'esse-fraudguard'
            key = 'dataset/encoded_data.csv'

            # Get the object from S3
            response = s3.get_object(Bucket=bucket_name, Key=key)
            # print("S3 object retrieved successfully")

            # Create a buffer to store the lines
            buffer = []

            # Read the object in chunks
            for i, line in enumerate(response['Body'].iter_lines()):
                if i >= 500:
                    break
                buffer.append(line.decode('utf-8'))

            # Join the lines into a single string
            csv_content = '\n'.join(buffer)
            # print("CSV content read successfully")

            if csv_content:
                df = pd.read_csv(StringIO(csv_content))
                json_data = df.to_json(orient='records')
                parsed = loads(json_data)
                serializer = JSONResponseSerializer(data={'json_data': parsed})
                serializer.is_valid(raise_exception=True)
                # print("Data serialized successfully")
                return Response({'status': 200, 'message': 'File read successfully', 'payload': serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            # print("An error occurred:", str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type='application/json')


class gpt(APIView):
    def get(self, request):
        x = "1234"
        serializer = barser(data={'p': x})
        if serializer.is_valid():
            return Response({'status': 201, 'message': 'User created successfully', 'payload': serializer.data}, status = status.HTTP_201_CREATED )       

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

session = boto3.Session(
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)
s3 = session.client('s3')
# Define function to encode categorical features

def encode(data):
    encoder = LabelEncoder()
    categorical_columns = data.select_dtypes(include=['object']).columns.tolist()
    for col in categorical_columns:
        data[col] = encoder.fit_transform(data[col])
    return data
def XGBoost_model(csv_row):
    # input_data = pd.DataFrame([csv_row])
    # print("Input data xg" , csv_row)
    # input_data_encoded = encode(input_data)
    bucket_name = 'esse-fraudguard'
    key = 'ML_models/XGBoost_model.joblib'
    response = s3.get_object(Bucket=bucket_name, Key=key)
    model_bytes = response['Body'].read()
    model = joblib.load(BytesIO(model_bytes))
    prediction = model.predict_proba(csv_row)
    # print("Pred" , prediction)
    return prediction
def RandomForest_model(csv_row):
    # input_data = pd.DataFrame([csv_row])
    # print("Input data xg" , csv_row)

    bucket_name = 'esse-fraudguard'
    key = 'ML_models/RandomForest_model.joblib'
    response = s3.get_object(Bucket=bucket_name, Key=key)
    model_bytes = response['Body'].read()
    model = joblib.load(BytesIO(model_bytes))
    prediction = model.predict_proba(csv_row)
    return prediction
def LogisticRegression_model(csv_row):
    # input_data = pd.DataFrame([csv_row])
    # print("Input data xg" , csv_row)
    # input_data_encoded = encode(input_data)
    bucket_name = 'esse-fraudguard'
    key = 'ML_models/LogisticRegression_model.joblib'
    response = s3.get_object(Bucket=bucket_name, Key=key)
    model_bytes = response['Body'].read()
    model = joblib.load(BytesIO(model_bytes))
    prediction = model.predict_proba(csv_row)
    return prediction
def LightGBM(csv_row):
    # print("Input data xg" , csv_row)
    bucket_name = 'esse-fraudguard'
    key = 'ML_models/LightGBM_model.joblib'
    response = s3.get_object(Bucket=bucket_name, Key=key)
    model_bytes = response['Body'].read()
    model = joblib.load(BytesIO(model_bytes))
    prediction = model.predict_proba(csv_row)
    return prediction
def decision_tree(csv_row):
    # input_data = pd.DataFrame([csv_row])
    # print("Input data xg" , csv_row)
    bucket_name = 'esse-fraudguard'
    key = 'ML_models/DecisionTree_model.joblib'
    response = s3.get_object(Bucket=bucket_name, Key=key)
    model_bytes = response['Body'].read()
    model = joblib.load(BytesIO(model_bytes))
    prediction = model.predict_proba(csv_row)
    return prediction



# Set environment variables using values from settings
os.environ["AWS_ACCESS_KEY_ID"] = settings.AWS_ACCESS_KEY_ID
os.environ["AWS_SECRET_ACCESS_KEY"] = settings.AWS_SECRET_ACCESS_KEY
s3=boto3.client('s3')
file_path = f"/tmp"
Path(file_path).mkdir(parents=True, exist_ok=True)
s3.download_file(Bucket="esse-fraudguard", Key='RAG/index.faiss', Filename=f"{file_path}/my_faiss.faiss")
s3.download_file(Bucket="esse-fraudguard", Key='RAG/index.pkl', Filename=f"{file_path}/my_faiss.pkl")
bedrock_runtime = boto3.client("bedrock-runtime", "ca-central-1")  # ca-central-1
bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0", client=bedrock_runtime)

llm = ChatBedrock(
    client=bedrock_runtime,
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    model_kwargs={"temperature": 0}
)
def load_knowledgeBase():
    bedrock_runtime = boto3.client("bedrock-runtime", "eu-north-1")
    bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0",
                                       client=bedrock_runtime)
    db = FAISS.load_local(
        index_name="my_faiss",
        folder_path=file_path,
        embeddings=bedrock_embeddings,
         allow_dangerous_deserialization=True
    )
    return db
def load_prompt():
    prompt = """ Based on the context you need to classify the question as fraud or not fraud. You also need to tell the reason for the classification.
    Given below is the context and question of the user.
    context = {context}
    question = {question}
    if the answer is not in the given data, answer "use model knowledge base"
    """
    prompt = ChatPromptTemplate.from_template(prompt)
    return prompt
knowledgeBase = load_knowledgeBase()
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)
prompt = load_prompt()
def json_to_paragraph(json_data):
    paragraph = f"The loan with number {json_data['LoanNumber']} was approved on {json_data['DateApproved']} through the Small Business Administration (SBA) office with code {json_data['SBAOfficeCode']}, us>"
    return paragraph

def json_to_paragraph(json_data):
    paragraph = f"The loan with number {json_data['LoanNumber']} was approved on {json_data['DateApproved']} through the Small Business Administration (SBA) office with code {json_data['SBAOfficeCode']}, using the Processing Method {json_data['ProcessingMethod']}. The borrower, {json_data['BorrowerName']}, located at {json_data['BorrowerAddress']}, {json_data['BorrowerCity']}, {json_data['BorrowerState']} {json_data['BorrowerZip']}, saw its loan status marked as \"{json_data['LoanStatus']}\" on {json_data['LoanStatusDate']}, with a term of {json_data['Term']} months and a {json_data['SBAGuarantyPercentage']}% SBA guaranty percentage. The loan, initially approved at ${json_data['InitialApprovalAmount']}, maintained its current approval amount at the same value, with no undisbursed amounts. Classified as a {json_data['FranchiseName']}, the loan was serviced by {json_data['ServicingLenderName']}, situated at {json_data['ServicingLenderAddress']}, {json_data['ServicingLenderCity']}, {json_data['ServicingLenderState']} {json_data['ServicingLenderZip']}. The loan's rural-urban indicator was '{json_data['RuralUrbanIndicator']}', with no Hubzone or Low and Moderate Income (LMI) indicators. The business, {json_data['BusinessAgeDescription']}, operates in {json_data['ProjectCity']}, {json_data['ProjectState']} {json_data['ProjectZip']}, within the CD {json_data['CD']} area, reporting {json_data['JobsReported']} jobs and carrying a NAICS code of {json_data['NAICSCode']}. The borrower's race and ethnicity were {json_data['Race']} and {json_data['Ethnicity']}, respectively. While the loan proceeds were allocated predominantly to payroll (${json_data['PAYROLL_PROCEED']}), with minimal amounts designated to utilities, the forgiveness amount totaled ${json_data['ForgivenessAmount']}, granted on {json_data['ForgivenessDate']}, resulting in a forgiveness percentage of {json_data['ForgivenPercentage']}%. Despite slight discrepancies in approval and total proceeds, the loan demonstrated a positive impact, averaging ${json_data['PROCEED_Per_Job']} per job created or retained."

def invoke_fun(query):
    try:
        data = query
        query = json_to_paragraph(data)
    except:
        query = query
    if query:
        response = None
        if len(query) > 1000:
            similar_embeddings = knowledgeBase.similarity_search(query)
            similar_embeddings = FAISS.from_documents(documents=similar_embeddings, embedding=bedrock_embeddings)
            retriever = similar_embeddings.as_retriever()
            rag_chain = (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
                )
            response = rag_chain.invoke(query)
        if response is None:
            response = llm.invoke(query)
            return response.content.strip()
        else:
            return response
    return "No query provided"

class InvokeAPIView(APIView):
    def post(self, request):
        serializer = InputSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data.get('data')
            text = serializer.validated_data.get('text')
            query = data if data else text
            response = invoke_fun(query)
            return Response({'message': response}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FrequencyAPIView(APIView):

    def get(self, request, *args, **kwargs):
        s3 = boto3.client('s3')
        bucket_name = 'esse-fraudguard'
        key = 'dataset/dataset/dataset_with_labels.csv'
        
        try:
            response = s3.get_object(Bucket=bucket_name, Key=key)
            buffer = []
            for i, line in enumerate(response['Body'].iter_lines()):
                if i >= 10000:
                    break
                buffer.append(line.decode('utf-8'))
            
            csv_content = '\n'.join(buffer)
            df = pd.read_csv(StringIO(csv_content), usecols=['BorrowerState', 'BorrowerCity'])
            
            state_counts = df['BorrowerState'].value_counts().to_dict()
            city_counts = df['BorrowerCity'].value_counts().to_dict()
            
            data = {
                'state_counts': state_counts,
                'city_counts': city_counts
            }
            
            serializer = FrequencySerializer(data=data)
            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class multigraphsAPIView(APIView):

    def get(self, request, *args, **kwargs):
        session = boto3.Session(
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
        )
        s3 = boto3.client('s3')
        bucket_name = 'esse-fraudguard'
        key = 'dataset/dataset_with_labels.csv'
        
        try:
            response = s3.get_object(Bucket=bucket_name, Key=key)
            buffer = []
            for i, line in enumerate(response['Body'].iter_lines()):
                if i >= 2000:  # Limiting to 100 lines for performance
                    break
                buffer.append(line.decode('utf-8'))
            
            csv_content = '\n'.join(buffer)
            df = pd.read_csv(StringIO(csv_content))
            
            state_counts = df['BorrowerState'].value_counts()
            top5_states = state_counts.head(5).to_dict()
            
            ########################2nd
            
            columns_of_interest = ['LoanStatus', 'RuralUrbanIndicator', 'Label']
            value_counts_arrays_specific = {column: list(df[column].value_counts().values) for column in columns_of_interest}
            
            ####################### 3rd
            df['ForgivenessDate'] = pd.to_datetime(df['ForgivenessDate'])

            # Group by ForgivenessDate and sum ForgivenessAmount
            forgiveness_data = df.groupby('ForgivenessDate')['ForgivenessAmount'].sum().reset_index()

            # Resample the data to monthly frequency
            monthly_data = forgiveness_data.set_index('ForgivenessDate').resample('ME').sum().reset_index()

            # Remove months with zero forgiveness amount
            monthly_data = monthly_data[monthly_data['ForgivenessAmount'] > 0]

            # Calculate cumulative sum
            monthly_data['CumulativeAmount'] = monthly_data['ForgivenessAmount'].cumsum()

            # Create the figure
            

            # Save data points (only non-zero values)
            monthly_data.to_csv('loan_forgiveness_data.csv', index=False)

            # Convert Timestamp to string for JSON serialization
            monthly_data['ForgivenessDate'] = monthly_data['ForgivenessDate'].dt.strftime('%Y-%m-%d')

            # Save bar and line data points separately
            bar_data = monthly_data[['ForgivenessDate', 'ForgivenessAmount']].to_dict(orient='records')
            line_data = monthly_data[['ForgivenessDate', 'ForgivenessAmount']].to_dict(orient='records')


            # Prepare the data for the serializer
            data = {
                'top5_states': top5_states,
                'value_counts_arrays_specific': value_counts_arrays_specific,
                'bar_data' : bar_data,
                'line_data' : line_data
            }

            serializer = GraphsSerializer(data=data)
            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)













from pathlib import Path
from langchain_community.embeddings import BedrockEmbeddings

def similarity_search(xq, k, embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    D, I = index.search(xq, k)  # search
    row_indexes = I[0]
    similar_embeddings = embeddings[row_indexes]
    return row_indexes, similar_embeddings

def extract_label(text):
    true_pattern = re.compile(r'\btrue\b', re.IGNORECASE)
    false_pattern = re.compile(r'\bfalse\b', re.IGNORECASE)
    if true_pattern.search(text):
        return True
    elif false_pattern.search(text):
        return False
    else:
        return None

def load_embeddings():
    s3 = boto3.client('s3')
    file_path = "/tmp"
    Path(file_path).mkdir(parents=True, exist_ok=True)
    
    # Download files from S3
    s3.download_file(Bucket="esse-fraudguard", Key='train_list.pkl', Filename=f"{file_path}/train_list.pkl")
    s3.download_file(Bucket="esse-fraudguard", Key='train_labels.pkl', Filename=f"{file_path}/train_labels.pkl")
    s3.download_file(Bucket="esse-fraudguard", Key='embeddings_list (1).pkl', Filename=f"{file_path}/embeddings_list.pkl")
    
    # Load downloaded files
    with open(f"{file_path}/train_list.pkl", 'rb') as f:
        sentences_train = pickle.load(f)
    with open(f"{file_path}/train_labels.pkl", 'rb') as f:
        y = pickle.load(f)
    with open(f"{file_path}/embeddings_list.pkl", 'rb') as f:
        embeddings_list = pickle.load(f)
    
    return np.array(embeddings_list), y, sentences_train

def load_model_credentials():
    AWS_KEY = settings.AWS_ACCESS_KEY_ID
    AWS_SECRET_KEY = settings.AWS_SECRET_ACCESS_KEY
    bedrock = boto3.client(service_name='bedrock-runtime',
    region_name='eu-north-1',
    aws_access_key_id=AWS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY)
    bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1",
                                          client=bedrock)
    return bedrock, bedrock_embeddings

def classify_sample(test_sample_embedding, arr1, df_str, bedrock, query_table):
    k = 10
    xq = test_sample_embedding.reshape(1, -1)
    similar_rows, _ = similarity_search(xq, k, arr1)
    df_p = df_str.loc[similar_rows]
    df_str1 = df_p.to_string(index=False)
    
    Note = f"""
    You will be provided with a query table and the 10 most similar data of that query table.
    Based on the provided data, check all the values if the provided table including the label (True/False).
    Label is not present in query table and Your task is to assign a label (True/False) to the query table
                [Query Table]:
                {query_table}:
                [Similar Data]:
                \n\n{df_str1}\n\n
    do not print query table in your response for justification as well as you must give me
    one word answer as true or false even when you are not sure or confused.
              """
    body = json.dumps({
            "prompt": f"Human: {Note}\nAssistant:",
            "max_tokens_to_sample": 2000,
            "temperature": 0.1,
            "top_p": 0.9,
                })

    modelId = 'anthropic.claude-v2:1'
    accept = 'application/json'
    contentType = 'application/json'
    response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())
    return extract_label(response_body['completion'])

def generate_sentences(df):
    sentences = []
    for _, row in df.iterrows():
        sentence = " ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
        sentences.append(sentence)
    return sentences

def generate_embeddings(sentences, bedrock_embeddings):
    embeddings = []
    for sentence in sentences:
        embedding = bedrock_embeddings.embed_query(sentence)
        embeddings.append(embedding)
    return np.array(embeddings)

def json_to_dataframe(json_data):
    try:
        # Extract the loan data from the nested structure
        loan_data = list(json_data.values())[0]
        
        # Create a DataFrame from the loan data
        df = pd.DataFrame([loan_data])
        
        # Convert LoanNumber to string
        df['LoanNumber'] = df['LoanNumber'].astype(str)
        
        # print("DataFrame columns:", df.columns)
        return df
    except Exception as e:
        print(f"Error in json_to_dataframe: {e}")
        raise

def main(test_sample_df):
    try:
        arr1, y, sentences_train = load_embeddings()
        bedrock, bedrock_embeddings = load_model_credentials()
        
        sentences_test = generate_sentences(test_sample_df)
        # print("Sentences test:", sentences_test)
        
        test_sample_embedding = generate_embeddings(sentences_test, bedrock_embeddings)
        # print("Test sample embedding shape:", test_sample_embedding.shape)

        df_str = pd.DataFrame({'Text': sentences_train, 'Labels': y})

        predicted_label = classify_sample(test_sample_embedding, arr1, df_str, bedrock, sentences_test)
        
        if predicted_label == True:
            prid = "100%"
        else:
            prid = "0%"
        return prid
    
    except Exception as e:
        print(f"Error in main function: {e}")
        return 0

class FraudPredictionAPIView(APIView):
    def post(self, request):
        serializer = FraudPredictionSerializer(data=request.data)
        if serializer.is_valid():           
            df = pd.DataFrame([serializer.data])
            prediction1 = XGBoost_model(df)
            prediction2 = LightGBM(df)
            prediction3 = RandomForest_model(df)
            prediction4 = LogisticRegression_model(df)
            prediction5 = decision_tree(df)
            # df_test = json_to_dataframe(serializer.data)
            if round(prediction1[0][1], 3)*100 > 50.0:
                llmmain = "100%"
            else:
                llmmain = "0%"
            result = {
                'XGBoost_model' : f'{round(round(prediction1[0][1], 3)*100,3)}%',
                'LightGBM' : f'{round(prediction2[0][1], 3)*100}%',
                'RandomForest_model' : f'{round(prediction3[0][1], 3)*100}%',
                'LogisticRegression_model' :f'{round(prediction4[0][1], 3)*100}%',
                'Decision_tree' : f'{round(prediction5[0][1] , 3)*100}%',
                'LLM' : llmmain

            }
            return Response({'status': 200, 'message': 'Prediction successfully', 'payload': result}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
