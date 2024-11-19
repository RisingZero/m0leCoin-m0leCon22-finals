# Stage 1, build angular
FROM node:16 as build

WORKDIR /usr/src/app
COPY package*.json ./

RUN npm install

COPY . .

# Update ETH contract address
ARG token_contract
ARG shop_contract
ARG bank_contract
ARG frontend_api_port
RUN sed -i "s/{token_contract}/${token_contract}/g" ./src/environments/environment.prod.ts
RUN sed -i "s/{bank_contract}/${bank_contract}/g" ./src/environments/environment.prod.ts
RUN sed -i "s/{shop_contract}/${shop_contract}/g" ./src/environments/environment.prod.ts
RUN sed -i "s/{frontend_api_port}/${frontend_api_port}/g" ./src/environments/environment.prod.ts

RUN npm run buildprod

# Stage 2, nginx serve
FROM nginx:alpine

COPY --from=build /usr/src/app/dist/m0lecoin-frontend /usr/share/nginx/html

EXPOSE 80