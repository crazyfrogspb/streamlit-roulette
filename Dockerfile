FROM python:3.7.4-slim-stretch

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN mkdir -p /root/.streamlit

RUN pip install streamlit numpy markdown nltk matplotlib

RUN bash -c 'echo -e "\
[general]\n\
email = \"\"\n\
" > /root/.streamlit/credentials.toml'

RUN bash -c 'echo -e "\
[server]\n\
enableCORS = false\n\
" > /root/.streamlit/config.toml'

EXPOSE 8501

COPY podlodka3.png .
COPY app.py .
COPY utils.py .

CMD [ "streamlit", "run", "app.py" ]