FROM ubuntu:trusty
MAINTAINER Eduardo Blancas Reyes

#Set a better PS1
ENV PS1='\[\e[0;31m\]\u\[\e[m\] \[\e[1;34m\]\w\[\e[m\] \[\e[0;31m\]$ \[\e[m\]\[\e[0;32m\]'

#Setup project env variables
ENV ROOT_FOLDER=/root/code
ENV DATA_FOLDER=/root/data

#Install wget and unzip
RUN apt-get install -y wget
RUN apt-get install -y unzip

#Install Python 2.7 via miniconda
RUN wget https://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -O /root/miniconda.sh
RUN bash /root/miniconda.sh -b -p /root/miniconda
RUN rm /root/miniconda.sh
ENV PATH="/root/miniconda/bin:$PATH"

#Install common packages
RUN apt-get install -y software-properties-common
#Add repository for gdal
RUN add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable
#Add repo for java 8
RUN add-apt-repository -y ppa:webupd8team/java
RUN apt-get update

#Install GDAL
RUN apt-get install -y gdal-bin

#Auto accept oracle license and install required java version for NER (Java 1.8 or later)
RUN echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | sudo /usr/bin/debconf-set-selections
RUN apt-get install -y oracle-java8-installer

#Install postgresql (only client)
RUN apt-get -y install postgresql-client

#Install mdbtools to convert access databases to csv files
RUN apt-get install -y mdbtools

#Install gnumeric to use ssconvert, which lets convert xls files to csv
RUN apt-get install -y gnumeric
 
#Install Stanford's NER
#http://nlp.stanford.edu/software/CRF-NER.shtml#Download
WORKDIR /root
ENV NAME="stanford-ner-2015-12-09"
RUN wget http://nlp.stanford.edu/software/$NAME.zip
RUN unzip $NAME.zip
RUN rm -rf $NAME.zip
#Define CLASSPATH and path to the NER classifiers
ENV CLASSPATH=/root/$NAME/stanford-ner.jar
ENV NER_CLASSIFIERS=/root/$NAME/classifiers

#Copy the conda requirements file
COPY requirements.conda /tmp/
#For some reason conda is not listing pip installed packages
#so, copy the pip requirements file too
COPY requirements.txt /tmp/

#Install Python dependencies
RUN conda install --file /tmp/requirements.conda
RUN pip install -r /tmp/requirements.txt

#Copy .pgpass
COPY .pgpass /root/

#Install custom package
COPY python_ds_tools/ /tmp/python_ds_tools
WORKDIR /tmp/python_ds_tools
RUN python setup.py install

#Set /root as working dir
WORKDIR /root