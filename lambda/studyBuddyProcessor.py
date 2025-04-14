import boto3
import urllib.parse
import json
import time

s3_client = boto3.client('s3')
transcribe_client = boto3.client('transcribe')

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    
    timestamp = str(int(time.time()))
    job_name = f"transcribe-{key.replace('/', '-')}-{timestamp}"
    
    try:
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': f's3://{bucket}/{key}'},
            MediaFormat='mp3',
            LanguageCode='en-US',
            OutputBucketName='study-buddy-text'
        )
    except transcribe_client.exceptions.ConflictException:
        job_name = f"{job_name}-{context.aws_request_id}"
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': f's3://{bucket}/{key}'},
            MediaFormat='mp3',
            LanguageCode='en-US',
            OutputBucketName='study-buddy-text'
        )
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Transcription job started',
            'job_name': job_name,
            'filename': key
        })
    }