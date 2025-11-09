# Focus Detection System

A real-time focus monitoring system that uses artificial intelligence and computer vision to track user attention, detect distractions, and help maintain productivity during study or work sessions. This system is designed to help students, professionals, and anyone looking to improve their focus and productivity.

## Project Description

The Focus Detection System is an innovative solution that combines modern web technologies with advanced computer vision to create a comprehensive focus monitoring tool. It uses your computer's webcam to:

1. **Monitor Attention Levels**
   - Tracks face presence and orientation to ensure you're looking at your work
   - Detects eye movements and blink patterns to identify signs of fatigue or drowsiness
   - Provides real-time feedback on your attention state

2. **Detect Distractions**
   - Identifies phone usage and alerts you when you reach for your mobile device
   - Monitors writing/pen activity to ensure active engagement
   - Tracks overall movement patterns to distinguish between focused work and distracted behavior

3. **Track Productivity**
   - Implements a customizable timer system (Pomodoro-style) for structured work sessions
   - Calculates and displays a real-time focus score
   - Maintains history of focus metrics for performance analysis

4. **Smart Alerts**
   - Sends timely notifications when distractions are detected
   - Alerts you of potential fatigue or drowsiness
   - Reminds you to maintain good posture and eye contact with your work

The system is built with privacy in mind, processing all video data locally on your machine without storing or transmitting any video footage. It combines the power of YOLOv8 object detection with custom-trained models for precise detection of phones, pens, and other objects relevant to focus monitoring.

## Features

- 🎯 Real-time focus tracking
- ⏱️ Customizable focus timer (15, 25, 45, or 60 minutes)
- 📸 Live video feed with distraction detection
- 👁️ Eye tracking and drowsiness detection
- 📱 Phone usage detection
- ✏️ Pen/writing activity monitoring
- 📊 Focus score calculation and history
- ⚡ Fast, efficient detection using YOLOv8

## Technical Description

### Architecture Overview

The system is built on a modern client-server architecture:

1. **Backend System**
   - FastAPI server handling real-time video processing
   - Multi-threaded architecture for concurrent processing
   - CameraWorker class managing video capture and analysis
   - Custom YOLOv8 models for object detection
   - OpenCV integration for face and eye tracking
   - Focus score calculation algorithm combining multiple metrics

2. **Frontend Interface**
   - React-based single-page application
   - Real-time MJPEG streaming for video display
   - Tailwind CSS for responsive design
   - Component-based architecture for maintainability
   - WebSocket integration for real-time updates

### Detection Systems

1. **Face and Eye Tracking**
   - Uses OpenCV's cascade classifiers
   - Real-time face orientation analysis
   - Eye state monitoring (open/closed)
   - Gaze direction estimation

2. **Phone Detection**
   - Custom-trained YOLOv8 model
   - High accuracy in various lighting conditions
   - Fast inference time for real-time detection
   - Robust against false positives

3. **Pen/Writing Detection**
   - Specialized YOLOv8 model for writing implements
   - Activity duration tracking
   - Idle time monitoring
   - Pattern recognition for actual writing vs. idle holding

### Focus Score Algorithm

The system uses a sophisticated algorithm to calculate focus scores:
- Base score from face presence and orientation
- Deductions for detected distractions
- Time-weighted averaging for smooth transitions
- Contextual adjustments based on activity patterns
- Exponential decay for sustained distractions

## Tech Stack

### Backend
- Python (FastAPI)
- OpenCV for computer vision
- YOLOv8 for object detection
- Face and eye tracking
- Threading for concurrent video processing

### Frontend
- React
- Tailwind CSS
- Vite build system
- Real-time MJPEG streaming

## Installation

### Prerequisites
- Python 3.8+ with pip
- Node.js 16+ with npm
- Webcam access
- Git (optional)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Focus_Detection
```

2. Set up Python virtual environment:
```bash
python -m venv mp_env
```

3. Activate virtual environment:
- Windows:
```bash
mp_env\Scripts\activate
```
- Linux/Mac:
```bash
source mp_env/bin/activate
```

4. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

5. Install frontend dependencies:
```bash
cd frontend
npm install
```

## Running the Application

1. Start the backend server (from project root):
```bash
cd backend
..\mp_env\Scripts\python -m uvicorn api.server:app --reload
```

2. Start the frontend development server (in a new terminal):
```bash
cd frontend
npm run dev
```

3. Open your browser and navigate to:
```
http://localhost:5173
```

## Usage

1. Open the application in your browser
2. Select your desired focus session duration (15-60 minutes)
3. Click "Start" to begin focus tracking
4. Position yourself in view of the webcam
5. The system will monitor:
   - Face presence and eye state
   - Phone usage
   - Writing/pen activity
   - Overall focus score

## Features In Detail

### Focus Score Calculation
- Face Detection: Ensures user presence
- Eye Tracking: Detects drowsiness and attention
- Phone Detection: Identifies mobile device distractions
- Pen Tracking: Monitors study/work activity
- Score updates in real-time with smooth transitions

### Alert System
The system provides alerts for:
- Mobile phone usage detected
- Drowsiness detection
- Extended inactivity periods

## Project Structure

```
├── backend/
│   ├── api/                 # FastAPI server
│   ├── models/             # ML model files
│   ├── modules/            # Detection modules
│   └── utils/              # Helper functions
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   └── assets/        # Static resources
│   └── public/            # Public assets
└── dataset/               # Training data
```

## Development

### Adding New Features
1. Backend detection modules are in `backend/modules/`
2. Frontend components are in `frontend/src/components/`
3. Update requirements.txt after adding Python dependencies

### Model Training
- Training notebooks are provided in `backend/`
- Dataset structure and annotations in `dataset/`
- Pre-trained models available in `backend/models/`

## Troubleshooting

### Common Issues

1. **Video stream not showing:**
   - Ensure webcam isn't in use by another application
   - Check browser console for errors
   - Verify backend server is running
   - Click "Start" to initialize camera worker

2. **Detection not working:**
   - Verify model files are present in `backend/models/`
   - Check console for Python errors
   - Ensure proper lighting conditions

3. **Performance issues:**
   - Close other applications using the webcam
   - Reduce resolution if needed
   - Check CPU/GPU usage

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

[Your chosen license]

## Acknowledgments

- YOLOv8 for object detection
- OpenCV for computer vision capabilities
- FastAPI for backend services
- React and Tailwind for frontend UI