# Table_Cleanliness_Detector
This software will analyze images or video of a table surface, detect anomalies (like food wastage, spills, or dirt), calculate a cleanliness percentage, and classify the table as "Clean" or "Dirty".

AI-Powered Table Cleanliness Detector
Welcome to the Table Cleanliness Detector! This project harnesses the power of machine learning and computer vision to determine the state of a table—whether it's pristine and ready for use, or cluttered and in need of a cleanup. This tool is ideal for fast-paced environments like cafeterias, co-working spaces, or even just keeping your home desk organized.

What does this do?
The system analyzes an image or a live video feed of a table surface and provides a real-time assessment, categorizing the table into distinct states (e.g., Clean, Slightly Cluttered, Dirty).

Core Capabilities
This project is built around several key functions to ensure robust detection and ease of use:

Real-Time Assessment: Processes video feeds to give continuous feedback on the table's state.

Object Detection & Classification: Identifies items on the table (crumbs, wrappers, cups) to accurately gauge cleanliness.

Threshold-Based Alerts: Can be configured to trigger alerts when a table crosses a specific "clutter" threshold.

Data Logging: Keeps track of cleanliness trends over time (perfect for optimizing cleaning schedules in commercial spaces).

 Getting Started
Follow these intuitive steps to get the detector running on your local machine.

Prerequisites
You'll need a few basics installed before we dive in. Ensure you have the following:

Python 3.8 or higher.

A working webcam or a pre-recorded video feed.

Git (to clone the repository).

Installation
1. Clone the repository
First, grab the code. Open your terminal and run:
git clone [Your-Repository-URL-Here]
cd Table-Cleanliness-Detector

2. Set up a Virtual Environment (Highly Recommended)
Keep your dependencies isolated and clean, just like your table!
python -m venv venv
source venv/bin/activate (On Windows use venv\Scripts\activate)

3. Install Dependencies
Install all necessary packages via our setup file:
pip install -r requirements.txt

 How the Model Works (The Intuitive Breakdown)
To provide you with the deep understanding you prefer, here’s a breakdown of the engine running behind the scenes.

The core of this system is a convolutional neural network (CNN), specifically tuned for image classification. Think of it like a highly observant inspector. When you feed it an image, it breaks the image down into tiny pieces (pixels) and looks for specific patterns—such as the scattered texture of crumbs or the sharp edges of abandoned coffee cups.

Image Input: A frame is grabbed from your webcam.

Preprocessing: The image is resized and normalized so the model can read it consistently.

Feature Extraction: The CNN scans the image, searching for the learned "dirty" or "clean" features.

Classification: The model calculates a probability score and assigns the frame to a specific category.

 Running the Application
Once your environment is set up, running the app is simple.

To run the real-time webcam detector:
python detect_live.py

To analyze a static image:
python detect_image.py --image path/to/your/image.jpg
