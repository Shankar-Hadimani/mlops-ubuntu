FROM python:3.9.13-slim

RUN pip install -U pip 
RUN pip install pipenv

WORKDIR /app

COPY ["Pipfile", "Pipfile.lock", "./"]

# install python packages from pipfile.lock into base python
# pipenv with system option, restircts creating virtual environment within docker
RUN pipenv install --system --deploy  


# copy both pridction module and the model
RUN mkdir -p /app/models
COPY predictions.py /app/
COPY ./models/linear_reg.bin /app/models

## expose port number
EXPOSE 9696

ENTRYPOINT [ "gunicorn","--bind=0.0.0.0:9696", "predictions:app" ]
