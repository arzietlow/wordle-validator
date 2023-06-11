import boto3
from datetime import datetime, timezone, timedelta
import random
import io
import json

s3_client = boto3.client('s3')
WORDLE_SOLUTION_BUCKET = 'wordle-solutions-bucket-test-az'
RETRY_LIMIT = 4

# Define the possible styles
COLORS = ['red', 'green', 'blue', 'orange', 'purple']
MARGINS = ['10px', '20px', '30px', '40px', '50px']
FONTS = ['Arial', 'Verdana', 'Helvetica', 'Times New Roman', 'Courier']
FONT_SIZES = ['10px', '12px', '14px', '16px', '18px']

def get_wordle_solutions():
    for i in range(RETRY_LIMIT):
        try:
            # Read wordle solutions file from S3 bucket
            obj = s3_client.get_object(Bucket=WORDLE_SOLUTION_BUCKET, Key='wordle_history.txt')
            file_content = obj['Body'].read().decode('utf-8')
            solution_list = []

            # read the file content using an in-memory buffer
            with io.StringIO(file_content) as file:
                # iterate over each line in the file and process it
                for line in file:
                    solution = line[-6:].strip()
                    solution_list.append(solution)

            # Check if the solution list meets the minimum length requirement
            min_solution_length = (datetime.now().date() - datetime(2021, 6, 19).date()).days - 1
            print(min_solution_length)
            if len(solution_list) >= min_solution_length:
                return solution_list
        except Exception as e:
            print(f'Error while getting wordle solutions from S3 (attempt {i+1}): {e}')
    
    # Raise an exception if the solution list could not be retrieved after the retry limit is reached
    raise Exception('Unable to retrieve wordle solutions from S3')

def get_html_template():
    try:
        obj = s3_client.get_object(Bucket=WORDLE_SOLUTION_BUCKET, Key='template.html')
        html_template = obj['Body'].read().decode('utf-8')
        return html_template
    except Exception as e:
        print(f'Error while getting HTML template from S3: {e}')
        raise e

def lambda_handler(event, context):
    try:
        # Get the wordle solutions
        solution_list = get_wordle_solutions()
        solution_list_str = json.dumps(solution_list)

        # Get the current time in CST
        current_time = datetime.now(timezone(timedelta(hours=-5)))
        current_time_str = current_time.strftime('%B %d, %Y %-I:%M%p')

        # Get the HTML template from S3 bucket
        html_template = get_html_template()

        # Replace the wordle_history variable with the solution list
        html_template = html_template.replace('wordle_history = ["WORD1", "WORD2", "WORD3",];', f'wordle_history = {solution_list_str};')

        # Replace the footer timestamp with the current time
        html_template = html_template.replace('Solutions added automatically. Last updated April 11 2023 @ 7:45pm CST', f'Solutions added automatically. Last updated {current_time_str} CST')
        
        # Replace the input button background with a random color for the day
        color = '%06x' % random.randint(0, 0xFFFFFF)
        print(color)
        html_template = html_template.replace('{input_button_background_color}', '#' + color)
        # Update the style with random values
        # ...

        # Upload the updated HTML file to S3 bucket
        s3_client.put_object(Body=html_template.encode('utf-8'), Bucket=WORDLE_SOLUTION_BUCKET, Key='index.html', ContentType='text/html')

        return {
            'statusCode': 200,
            'body': 'HTML file updated successfully'
        }
    except Exception as e:
        print(f'Error while updating HTML file: {e}')
        raise e
