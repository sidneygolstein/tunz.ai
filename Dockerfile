# Docker image creation. The image will
#   - Setup python
#   - Tell the client/user of container what prt flask is runninhg on (here 5000)
#   - Install flask
#   - Run the flask app 

FROM python:3.12-slim
#EXPOSE 5000
# Copy app.py into the image so that we can then run it 
WORKDIR /app            

COPY requirements.txt requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade -r requirements.txt 
COPY . .           
ENV FLASK_ENV=development

# COPY .env .env
#CMD ["gunicorn", "--bind", "0.0.0.0:80", "run:create_app()"]  
CMD ["flask", "run", "--host", "0.0.0.0"]     
