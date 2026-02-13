# pill_box
ai integrated pillbox


### create ENV
-   py -3.11 -m venv venv

### activate for windows only -->
-   venv\Scripts\activate

### install requirements.txt
-   pip install -r requirement.txt


# uvx commands -->

uvx ruff check .
uvx ruff format .
uvx ruff check . --select I --fix


# First run detection

python main.py detect

# second embed

python main.py embed

# testing with image path

python main.py recognize --image "src\dataset\Alvaro Morte\Alvaro Morte1_152.jpg"

# Testing with webcam

python main.py webcam
