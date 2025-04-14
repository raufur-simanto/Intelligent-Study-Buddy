from flask import Flask, request, jsonify, Response
import boto3
import logging
import requests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


s3_client = boto3.client('s3')

polly = boto3.client("polly")


@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        text = request.json.get("text", "")
        logging.info(f"Text to synthesize: {text}")

        response = polly.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId="Joanna"
        )

        if "AudioStream" in response:
            # Create a generator to stream audio data
            def generate():
                for chunk in response["AudioStream"].iter_chunks():
                    yield chunk

            # Return the audio data as a streaming response
            return Response(generate(), mimetype="audio/mpeg")
        
        return {"error": "Audio stream not available"}, 500

    except Exception as e:
        logging.exception("Error in Polly TTS")
        return {"error": str(e)}, 500



@app.route('/generate-quiz', methods=['POST'])
def generate_quiz():
    summary = request.get_json()['summary']

    payload = {
        'document': {'type': 'PLAIN_TEXT', 'content': summary},
        'encodingType': 'UTF8'
    }

    url = "https://language.googleapis.com/v1/documents:analyzeEntities"

    response = requests.post(url, params={'key': "API-KEY"}, json=payload)

    if response.status_code == 200:
        result = response.json()
        
        questions = []
        
        # Generate factual questions based on entities
        for entity in result.get('entities', []):
            name = entity.get('name')
            entity_type = entity.get('type')
            if name:
                if entity_type in ['PERSON', 'LOCATION', 'EVENT', 'WORK_OF_ART']:
                    questions.append(f"Who is {name}?")  
                elif entity_type == 'LOCATION':
                    questions.append(f"Where is {name} located?")
                elif entity_type == 'EVENT':
                    questions.append(f"When did {name} happen?")
                else:
                    questions.append(f"What is {name}?") 

        questions = list(set(questions))
            

        return jsonify({'quiz': questions})
    else:
        print("Error: ", response.text)
        return [], 404


 
@app.route('/')
def index():
    return app.send_static_file('index.html')

summary_bucket = 'study-buddy-text'
@app.route('/get-summary', methods=['POST'])
def get_summary():
    try:
        filename = request.get_json()['filename']
        filename = filename + '-summary.txt'
        logger.info(f"Received filename: {filename}")
        response = s3_client.get_object(Bucket=summary_bucket, Key=filename)
        summary = response['Body'].read().decode('utf-8')
        logger.info(f"Summary: {summary}")
        return jsonify({'summary': summary})
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/get-presigned-url', methods=['POST'])
def get_presigned_url():
    try:
        data = request.get_json()
        filename = data['filename']
        logger.info(f"Received filename: {filename}")
        bucket = 'study-buddy-audio'
        url = s3_client.generate_presigned_url('put_object',
                                            Params={'Bucket': bucket, 'Key': filename, 'ContentType': 'audio/mpeg'},
                                            ExpiresIn=3600)
        logger.info(f"Generated URL: {url}")
        return jsonify({'url': url}), 200
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


