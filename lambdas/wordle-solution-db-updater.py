import boto3
import datetime
from botocore.vendored import requests

# Initialize S3 client
s3 = boto3.client('s3')

# Lambda function handler
def lambda_handler(event, context):
    # Get the current date and format it for the API URL and output file
    
    # set the timezone to CST
    tz = datetime.timezone(datetime.timedelta(hours=-6))
    
    # get the current datetime in CST
    now = datetime.datetime.now(tz)
    
    # get the date from the datetime object
    today = now.date()
    
    # format the date as a string
    date_str = today.strftime('%B %d, %Y')
    
    # Construct the API URL for today's Wordle puzzle
    url = f'https://www.nytimes.com/svc/wordle/v2/{today:%Y-%m-%d}.json'
    print(url)
    
    # Query the API for today's solution
    response = requests.get(url).json()
    solution = response['solution']
    wordle_number = response['days_since_launch']
    
    # Format the solution for writing to the output file
    solution_line = f"{date_str}\t{wordle_number}\t{solution.upper()}\n"
    
    print(f"adding solution string {solution_line} to wordle s3 file")
    # Write solution to file in S3 bucket
    bucket_name = 'wordle-solutions-bucket-test-az'
    file_name = 'wordle_history.txt'
    try:
        # Download current history file
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        current_data = response['Body'].read().decode('utf-8')
    except s3.exceptions.NoSuchKey:
        print("Failed to retrieve wordle data from s3")
        return
    # Prepend new solution to current history
    new_data = solution_line + current_data
    # Upload updated history file to S3
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=new_data.encode('utf-8'), ContentType='text/html')
    print(f"Added new Wordle solution {solution} to {bucket_name}/{file_name}")
