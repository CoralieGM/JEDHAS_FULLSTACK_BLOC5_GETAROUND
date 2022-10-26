FROM continuumio/miniconda3

#EXPOSE 8501

WORKDIR /home/app

RUN apt-get update

RUN pip install pandas numpy streamlit plotly openpyxl
COPY . /home/app

#CMD streamlit run --server.port=8501 app.py
CMD streamlit run --server.port $PORT app.py