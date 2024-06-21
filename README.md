# Couchbase Graphql and REST DEMO

## Description

This demo application showcases how to manage an airline database using both GraphQL and REST interfaces. The application uses Flask for the web server and Couchbase for the database. It provides CRUD operations (Create, Read, Update, Delete) for managing airlines.

## Steps to Setup and Run the Application

### 1. Create Docker Container

Run the following command to create and start a Couchbase container:

```sh
docker run -d --name cb_graphsql_rest_demo -p 8091-8096:8091-8096 -p 11210-11211:11210-11211 -p 5000:5000 -p 5000:5000 couchbase:7.6.1
```

### 2. Checkout Repository

Clone the repository inside the container

### 3. Install Requirements

Install the required Python packages using pip:

```sh
pip install -r requirements.txt
```

Install the "travel-sample" bucket https://docs.couchbase.com/server/current/manage/manage-settings/install-sample-buckets.html

### 4. Run Flask App

Start the Flask application:

```sh
python3 app.py
```

### 5. Go to GraphQL Playground

Open your web browser and navigate to:

```
http://localhost:5000/graphql
```

This will take you to the GraphQL Playground interface.

### 6. Test the CRUD Queries

#### Sample GraphQL Queries

**Get All Airlines**

```graphql
query {
  airlines {
    id
    type
    name
    iata
    icao
    callsign
    country
  }
}
```

**Get Airline by ID**

```graphql
query {
  airline(id: "airline_1234") {
    id
    type
    name
    iata
    icao
    callsign
    country
  }
}
```

**Create an Airline**

```graphql
mutation {
  createAirline(id: "airline_1234", type: "airline", name: "Sample Airline", iata: "SA", icao: "SAL", callsign: "SAMPLE", country: "USA") {
    success
    message
    airline {
      id
      type
      name
      iata
      icao
      callsign
      country
    }
  }
}
```

**Update an Airline**

```graphql
mutation {
  updateAirline(id: "airline_1234", name: "Updated Airline") {
    success
    message
    airline {
      id
      type
      name
      iata
      icao
      callsign
      country
    }
  }
}
```

**Delete an Airline**

```graphql
mutation {
  deleteAirline(id: "airline_1234") {
    success
    message
  }
}
```

### 7. Test the REST Interface with cURL

#### Sample cURL Commands

**Get All Airlines**

```sh
curl -X GET http://127.0.0.1:5000/airlines
```

**Get Airline by ID**

```sh
curl -X GET http://127.0.0.1:5000/airline?id=airline_1234
```

**Create an Airline**

```sh
curl -X POST http://127.0.0.1:5000/airline -H "Content-Type: application/json" -d '{
  "id": "airline_1234",
  "type": "airline",
  "name": "Sample Airline",
  "iata": "SA",
  "icao": "SAL",
  "callsign": "SAMPLE",
  "country": "USA"
}'
```

**Update an Airline**

```sh
curl -X PUT http://127.0.0.1:5000/airline/airline_1234 -H "Content-Type: application/json" -d '{
  "name": "Updated Airline"
}'
```

**Delete an Airline**

```sh
curl -X DELETE http://127.0.0.1:5000/airline/airline_1234
```

## Conclusion

This demo application provides a comprehensive example of how to implement and use GraphQL and REST interfaces with a Couchbase database. It demonstrates the flexibility of GraphQL for querying specific data and the simplicity of REST for traditional API interactions. By following the steps outlined above, you can easily set up, run, and test the application.
```

