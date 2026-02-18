FROM python:3.10
WORKDIR /code
ENV GDAL_VERSION=3.9.2
ENV GDAL_CONFIG=/opt/homebrew/Cellar/gdal/3.9.2/bin/gdal-config

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./src /code/src
EXPOSE 8080
CMD ["uvicorn", "src.main:app","--host", "0.0.0.0", "--port", "8080"]
