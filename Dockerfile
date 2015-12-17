FROM ubuntu:trusty

#Install common packages (this installs Python 3 which we also need
#for some scripts)
RUN apt-get install -y software-properties-common


#Install Python 2.7 (which is used for most of the code)
RUN add-apt-repository -y ppa:fkrull/deadsnakes-python2.7 && apt-get update
RUN apt-get install -y python2.7
#Alias python2.7 to python
ENV python=python2.7

#Install pip (this will also install Python 2)
#RUN apt-get install -y python python-dev python-distribute python-pip
RUN apt-get install -y python-pip
RUN pip install --upgrade pip

#Install postgresql (only client)
RUN apt-get -y install postgresql-client

#Add repository with the required GDAL version
RUN add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable && apt-get update
RUN apt-get install -y gdal-bin
RUN gdalinfo --version

#Install mdbtools to convert access databases to csv files
RUN apt-get install -y mdbtools

#Install gnumeric to use ssconvert, which lets convert xls files to csv
RUN apt-get install -y gnumeric

#Install required java version for NER (Java 1.8 or later)
#http://www.webupd8.org/2012/09/install-oracle-java-8-in-ubuntu-via-ppa.html
RUN add-apt-repository -y ppa:webupd8team/java && apt-get update
#Auto accept Oracle license
RUN echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | sudo /usr/bin/debconf-set-selections
#RUN apt-get update
RUN apt-get install -y oracle-java8-installer

#Setup enviromental variables
ENV ROOT_FOLDER=/root/code
ENV DATA_FOLDER=/root/data

#Copy the requirements file
COPY requirements.txt /tmp/

#Install Python dependencies
RUN pip install -r /tmp/requirements.txt

#Set /root as working dir
WORKDIR /root