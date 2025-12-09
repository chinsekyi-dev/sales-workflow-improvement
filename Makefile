install:
	pip install -r requirements.txt

format:
	black src/*.py *.py
	isort src/*.py *.py

run-fetch:
	python src/get_news.py

run-app:
	streamlit run app.py

