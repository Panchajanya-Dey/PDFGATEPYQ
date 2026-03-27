# GatePYQ
This project is based on previous work of https://github.com/anish384/GatePYQ.git, the current version allows users to directly upload PDFs of question paper and answer keys seperately, instead of uploading JSON files.\
Known Bugs:\
--- For numerical type questions, answers within range are marked as incorrect if they are not strictly equal to one of the bounds.\
\
To launch locally, ensure all python dependencies as mentioned in backend/requirements.txt are installed in your virtual environment.

### Create virtual environment
python3 -m venv venv

### Activate virtual environment
source venv/bin/activate

### Upgrade pip
pip install --upgrade pip

### Install dependencies
pip install -r backend/requirements.txt

### Open two terminals
To launch backend, <br>
cd backend/ <br>
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

To launch frontend <br>
python -m http.server 5500
