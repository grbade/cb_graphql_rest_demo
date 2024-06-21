import json
from flask import Flask, jsonify, request, send_file
from ariadne import gql, load_schema_from_path, make_executable_schema, graphql_sync
from resolvers import query, mutation
import couchbase.subdocument as SD
from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException

# Initialize the Flask application
app = Flask(__name__)

# Load GraphQL schema from file
type_defs = load_schema_from_path("schema.graphql")
schema = make_executable_schema(type_defs, query, mutation)

# Load configuration
with open('config.json') as config_file:
    config = json.load(config_file)

# Initialize Couchbase connection with authentication
authenticator = PasswordAuthenticator(config['couchbase']['username'], config['couchbase']['password'])
cluster = Cluster(config['couchbase']['host'], authenticator=authenticator)
bucket = cluster.bucket(config['couchbase']['bucket'])
collection = bucket.scope(config['couchbase']['scope']).collection(config['couchbase']['collection'])

@app.route("/", methods=["GET"])
def graphql_test():
    """
    Test route to check if the server is running.
    """
    return "success"

@app.route("/graphql", methods=["GET"])
def graphql_playground():
    """
    Route for accessing the GraphQL Playground interface.
    """
    return send_file('playground.html')

@app.route("/graphql", methods=["POST"])
def graphql_server():
    """
    Route for handling GraphQL queries and mutations.
    """
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code

# REST API endpoints

@app.route('/airlines', methods=['GET'])
def get_airlines():
    """
    Route to get all airlines.
    """
    try:
        query_str = "SELECT * FROM `travel-sample`.inventory.airline WHERE type = 'airline'"
        row_iter = cluster.query(query_str)
        airlines = [row['airline'] for row in row_iter]
        return jsonify(airlines), 200
    except CouchbaseException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/airline', methods=['GET'])
def get_airline():
    """
    Route to get a specific airline by its fields.
    """
    params = request.args
    query_str = "SELECT * FROM `travel-sample`.inventory.airline WHERE " + " AND ".join([f"{k} = '{v}'" for k, v in params.items()])
    try:
        row_iter = cluster.query(query_str)
        airlines = [row['airline'] for row in row_iter]
        return jsonify(airlines), 200
    except CouchbaseException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/airline', methods=['POST'])
def create_airline():
    """
    Route to create a new airline.
    """
    data = request.json
    airline_id = data.get("id")
    if not airline_id:
        return jsonify({"error": "ID is required"}), 400
    try:
        collection.upsert(str(airline_id), data)
        return jsonify({"success": True, "message": "Airline created successfully", "airline": data}), 201
    except CouchbaseException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/airline/<id>', methods=['PUT'])
def update_airline(id):
    """
    Route to update an airline's details.
    """
    data = request.json
    try:
        collection.mutate_in(id, [SD.upsert(k, v) for k, v in data.items() if v is not None])
        updated_airline = collection.get(id).content_as[dict]
        return jsonify({"success": True, "message": "Airline updated successfully", "airline": updated_airline}), 200
    except CouchbaseException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/airline/<id>', methods=['DELETE'])
def delete_airline(id):
    """
    Route to delete an airline by its ID.
    """
    try:
        collection.remove(id)
        return jsonify({"success": True, "message": "Airline deleted successfully"}), 200
    except CouchbaseException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8501, debug=True)
