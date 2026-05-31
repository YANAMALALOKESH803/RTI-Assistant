import os

def test_app_exists():
 assert os.path.exists("app.py")

def test_requirements_exists():
 assert os.path.exists("requirements.txt")

def test_data_folder_exists():
 assert os.path.exists("data")

def test_assets_folder_exists():
 assert os.path.exists("assets")
