FROM node:18

RUN apt-get update && apt-get install -y ffmpeg python3 python3-pip curl
RUN pip3 install ffsubsync

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 10000

CMD ["node", "index.js"]
