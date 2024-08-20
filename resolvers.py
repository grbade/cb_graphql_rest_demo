import json
from ariadne import QueryType, MutationType
import couchbase.subdocument as SD
from couchbase.cluster import Cluster
from couchbase.exceptions import CouchbaseException
from couchbase.auth import PasswordAuthenticator

# Load configuration
with open('config.json') as config_file:
    config = json.load(config_file)

# Initialize Couchbase connection with authentication
authenticator = PasswordAuthenticator(config['couchbase']['username'], config['couchbase']['password'])
cluster = Cluster(config['couchbase']['host'], authenticator=authenticator)
bucket = cluster.bucket(config['couchbase']['bucket'])
collection = bucket.scope(config['couchbase']['scope']).collection(config['couchbase']['collection'])

# Define QueryType for handling query operations
query = QueryType()

# Define MutationType for handling mutation operations
mutation = MutationType()

def build_query_string(args):
    """
    Helper function to build the query string based on provided arguments.
    """
    query_str = "SELECT * FROM `travel-sample`.inventory.airline WHERE"
    conditions = []
    for key, value in args.items():
        if value is not None:
            if key == "id":
                conditions.append(f"`{key}` = {value}")
            else:
                conditions.append(f"`{key}` = '{value}'")
    if conditions:
        query_str += " " + " AND ".join(conditions)
    else:
        query_str = query_str.replace(" WHERE", "")
    return query_str

@query.field("airline")
def resolve_airline(_, info, **kwargs):
    """
    Resolver for fetching airlines by various fields.
    """
    try:
        query_str = build_query_string(kwargs)
        row_iter = cluster.query(query_str)
        airlines = [row["airline"] for row in row_iter]
        return airlines
    except CouchbaseException as e:
        print(f"Error querying airline by fields: {e}")
    return []

@query.field("airlines")
def resolve_airlines(_, info):
    """
    Resolver for fetching all airlines.
    """
    try:
        query_str = "SELECT * FROM `travel-sample`.inventory.airline WHERE type = 'airline'"
        row_iter = cluster.query(query_str)
        airlines = [row["airline"] for row in row_iter]
        return airlines
    except CouchbaseException as e:
        print(f"Error querying airlines: {e}")
    return []

@mutation.field("createAirline")
def resolve_create_airline(_, info, id, type, name, iata, icao, callsign, country):
    """
    Resolver for creating a new airline.
    """
    airline = {
        "id": id,
        "type": type,
        "name": name,
        "iata": iata,
        "icao": icao,
        "callsign": callsign,
        "country": country
    }
    try:
        collection.insert("airline_" + str(id), airline)
        return {
            "success": True,
            "message": "Airline created successfully",
            "airline": airline
        }
    except CouchbaseException as e:
        print(f"Error creating airline: {e}")
        return {
            "success": False,
            "message": f"Error creating airline: {e}",
            "airline": None
        }

@mutation.field("updateAirline")
def resolve_update_airline(_, info, id, type=None, name=None, iata=None, icao=None, callsign=None, country=None):
    """
    Resolver for updating an airline by its ID.
    """
    updates = {}
    if type is not None:
        updates["type"] = type
    if name is not None:
        updates["name"] = name
    if iata is not None:
        updates["iata"] = iata
    if icao is not None:
        updates["icao"] = icao
    if callsign is not None:
        updates["callsign"] = callsign
    if country is not None:
        updates["country"] = country

    try:
        collection.mutate_in("airline_" + str(id), [SD.upsert(field, value) for field, value in updates.items()])
        updated_airline = collection.get("airline_" + str(id)).content_as[dict]
        return {
            "success": True,
            "message": "Airline updated successfully",
            "airline": updated_airline
        }
    except CouchbaseException as e:
        print(f"Error updating airline: {e}")
        return {
            "success": False,
            "message": f"Error updating airline: {e}",
            "airline": None
        }

@mutation.field("deleteAirline")
def resolve_delete_airline(_, info, id):
    """
    Resolver for deleting an airline by its ID.
    """
    try:
        collection.remove("airline_" + str(id))
        return {
            "success": True,
            "message": "Airline deleted successfully"
        }
    except CouchbaseException as e:
        print(f"Error deleting airline: {e}")
        return {
            "success": False,
            "message": f"Error deleting airline: {e}"
        }
