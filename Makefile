install:
	pip install -r requirements.txt

format:
	black .
	isort .

run-fetch:
	python src/get_news.py

run-app:
	streamlit run app.py

