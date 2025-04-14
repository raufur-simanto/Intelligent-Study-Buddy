

```markdown
# 🎓 Intelligent Study Buddy

An AI-powered web application that transforms lecture audio into concise summaries and quiz questions — helping students learn smarter, faster.

---

## 📌 Features

- 🎤 **Upload Audio**: Easily upload your recorded lecture.
- 📝 **Automatic Transcription**: Uses AWS Transcribe to convert audio to text.
- 🧠 **Smart Summarization**: Summary generated using Amazon Comprehend.
- ❓ **Quiz Generator**: Creates quiz questions from the summary using Google NLP.
- 🔊 **Text-to-Speech**: Summary and quiz can be played using Amazon Polly.
- 🌐 **Clean UI**: Simple and intuitive frontend for interaction.


---

## 🧭 Application Flow

1. **User Uploads Audio**  
2. **Audio Stored in S3**
3. **Lambda Trigger (Transcribe)**  
   - Converts audio to text  
   - Stores transcript as JSON in another S3 bucket  
4. **Lambda Trigger (Summarize)**  
   - Summarizes text using Amazon Comprehend  
   - Stores summary as a `.txt` file in S3  
5. **Frontend (UI)**  
   - Fetches summary and displays it  
   - Allows user to generate quiz questions from the summary using Google NLP  
   - Provides audio playback of both using Amazon Polly  

---

## 🧰 Tech Stack

### ⚙️ Backend (Cloud Services)
- **AWS S3** – file storage  
- **AWS Lambda** – serverless compute  
- **Amazon Transcribe** – speech-to-text  
- **Amazon Comprehend** – text summarization  
- **Amazon Polly** – text-to-speech  
- **Google Cloud NLP** – quiz question generation  

### 🌐 Frontend
- HTML / CSS / JavaScript (Vanilla)

---

## 🚀 Setup & Deployment

### Prerequisites:
- AWS account with IAM access
- Google Cloud NLP API key
- Python 3.8+
- Flask (`pip install flask boto3 google-cloud-language`)

### Local Setup:
```bash
git clone https://github.com/raufur-simanto/Intelligent-Study-Buddy
cd Intelligent-Study-Buddy
python app.py
```


---

## 📌 Future Improvements

- Export results (PDF)
- MCQ-style quiz format
- User authentication & history
- Language support & customization


---

## 📄 License

This project is licensed under the MIT License.
```