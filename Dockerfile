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









# To deploy code with gunicorn
#CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:create_app()"]    


#CMD ["/bin/bash", "docker-entrypoint.sh"]


# Create a container image:
# 'docker build -t image_name .'

# Run a container in the terminal
# 'docker run -p host_port:docker_img_port image_name' -->ex: 'docker run -p 5005:5000 tunz_mvp'

# Run a container in the terminal and use the terminal:
# 'docker run -d -p host_port:docker_img_port image_name' -->ex: 'docker run -d -p 5005:5000 rtunz_mvp'


# Create a volume
# 'docker run -dp 5005:5000 -w /app -v "$(pwd):/app" mvp_tunz'

# --> It creates a volume (= mapping of a directory between my local file system and the container file system) 
# allowng the code folder to be sync with the containers folder --> let us work with the modified code everytime
# Only use volume for local development, not when we want to deploy our app


