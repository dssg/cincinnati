#Build docker image

`docker build -t cincinnati .`

#Run docker image

`docker run -v ~/data/cincinnati-data:/root/data -v /Users/Edu/Development/dsapp/cincinnati-dsapp:/root/code -i -t cincinnati /bin/bash`

