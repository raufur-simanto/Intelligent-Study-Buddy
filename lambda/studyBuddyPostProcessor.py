import boto3
import urllib.parse
import json


s3_client = boto3.client('s3')
comprehend_client = boto3.client('comprehend')
lex_client = boto3.client('lexv2-runtime')

#  generate a summary from the transcription text
def get_summary(text):
    try:
        response = comprehend_client.detect_key_phrases(Text=text, LanguageCode='en')
        if not response['KeyPhrases']:
            return text
        return ' '.join(phrase['Text'] for phrase in response['KeyPhrases'][:-1])
    except Exception as e:
        print(f"Error in get_summary: {str(e)}")
        return text  

# Lambda function handler
def lambda_handler(event, context):
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
        print(f'Processing file: {key}')
        print(f'Bucket: {bucket}')
        
        filename_parts = key.split('transcribe-')[1].split('-')
        filename = '-'.join(filename_parts[:-1])
        
        transcript_obj = s3_client.get_object(Bucket=bucket, Key=key)
        transcript_data = json.loads(transcript_obj['Body'].read().decode('utf-8'))
        text = transcript_data['results']['transcripts'][0]['transcript']
        print(f'Transcription: {len(text)} characters')
        
        summary = get_summary(text)
        print(f'Summary: {len(summary)} characters')

        s3_client.put_object(
            Bucket='study-buddy-text',
            Key=f'{filename}-summary.txt',
            Body=summary.encode('utf-8')
        )
        
        # # Update Lex session with the summary (use V2 syntax)
        # lex_client.put_session(
        #     botId='MIZXEY8IRY',        # Replace with your BotId
        #     botAliasId='TSTALIASID',   # Replace with your BotAliasId
        #     localeId='en_US',          # Locale ID for Lex V2
        #     sessionId='study-buddy-session',
        #     sessionState={
        #         'sessionAttributes': {'summary': summary}
        #     }
        # )
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Processing complete', 'summary': summary})
        }

    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
