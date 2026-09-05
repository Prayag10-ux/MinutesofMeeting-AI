cat > README.md <<'EOF'
# Minutes of Meeting AI

> AI-powered Minutes of Meeting assistant designed to reduce the manual effort involved in documenting faculty and institutional meetings.

## 📌 Overview

Minutes of Meeting AI is a Streamlit-based application that records meeting audio, converts the speech into text using AI, generates structured Minutes of Meeting, and exports the result as a professional Word document.

The system is designed specifically to simplify the documentation workflow for faculty meetings.

## 🎯 Problem Statement

Faculty members often spend significant time manually preparing Minutes of Meeting after discussions. This includes listening to recordings, identifying important points, writing decisions and action items, and attaching meeting evidence.

Minutes of Meeting AI automates this process.

## ✨ Key Features

- 🎙️ Meeting audio recording
- 📝 Automatic speech-to-text transcription
- 🤖 AI-generated Minutes of Meeting
- 📋 Automatic extraction of:
  - Agenda
  - Key Discussion Points
  - Decisions
  - Action Items
- 👥 Participant information
- 📍 Meeting location
- 📸 Meeting photograph as supporting evidence
- 📄 Professional DOCX export
- 🏫 Institutional branding support
- 🔒 Local AI processing without paid API subscriptions

## 🧠 AI Pipeline

```text
Meeting Audio
      ↓
Faster-Whisper
      ↓
Meeting Transcript
      ↓
Gemma 3 4B
      ↓
Structured Minutes of Meeting
      ↓
Word Document