import sqlalchemy
from geopy.geocoders import Nominatim

def request_entry(request):

    if not request.args or 'name' not in request.args or 'zip' not in request.args or 'street' not in request.args or 'house' not in request.args:
        return f'invalid request format'
    

    if request.args.get('name') is None or request.args.get('zip') is None or request.args.get('street') is None or request.args.get('house') is None:
        return f'invalid parameters'

    name = str(request.args.get('name'))
    zipcode = str(request.args.get('zip'))
    street = str(request.args.get('street'))
    house = str(request.args.get('house'))
    candy = None

    if len(name) < 2 or len(name) > 80:
        return 'invalid parameters?'
    
    feedback = None

    if 'candy' in request.args and not 'delete' in request.args:

        if str(request.args.get('candy')) == 'yes':
            candy = True

        elif str(request.args.get('candy')) == 'no':
            candy = False

        else:
            return f'invalid parameters'

        if not adressformatcheck(zipcode, street, house):
            return f'invalid adress'

        coordinates = adressgeocheck(zipcode, street, house)

        if coordinates is None:
            return f'invalid adress'

        if isinstance(coordinates, Exception):
            return "API error: " + repr(coordinates)
        
        feedback = updatehouse(name, zipcode, street, house, coordinates.latitude, coordinates.longitude, candy)


    elif 'delete' in request.args and not 'candy' in request.args:

        if str(request.args.get('delete')) != "DELETE":
            return f'did not delete entry'

        if not adressformatcheck(zipcode, street, house):
            return f'invalid adress'

        feedback = deletehouse(zipcode, street, house)

    else:
        return f'invalid request format'

    if isinstance(feedback, Exception):
        return repr(feedback)
    return feedback



def deletehouse(zipcode, street, house):
    
    db = connect_db()
    if isinstance(db, Exception):
        return db

    query = "SELECT EXISTS ( SELECT zip_code FROM safe_houses WHERE zip_code LIKE {} AND street LIKE {} AND street_number LIKE {} );".format('"' + zipcode + '"', '"' + street + '"', '"' + house + '"')
    result = executequery(db, query, True)
    if isinstance(result, Exception):
        db.dispose()
        return result

    if not (result[0])[0]:
        db.dispose()
        return 'cannot delete entry because it does not exist'

    query = "DELETE FROM safe_houses WHERE zip_code LIKE {} AND street LIKE {} AND street_number LIKE {};".format('"' + zipcode + '"', '"' + street + '"', '"' + house + '"')
    result = executequery(db, query, False)
    db.dispose()
    if isinstance(result, Exception):
        return result

    return 'successfully deleted entry'



def updatehouse(name, zipcode, street, house, latitude, longitude, candy):

    db = connect_db()
    if isinstance(db, Exception):
        return db

    query = "SELECT name FROM safe_houses WHERE zip_code LIKE {} AND street LIKE {} AND street_number LIKE {};".format('"' + zipcode + '"', '"' + street + '"', '"' + house + '"')
    result = executequery(db, query, True)
    if isinstance(result, Exception):
        db.dispose()
        return result

    if result:
        if str((result[0])[0]) == name.upper():

            query = "UPDATE safe_houses SET candy = {} WHERE zip_code LIKE {} AND street LIKE {} AND street_number LIKE {};".format(candy, '"' + zipcode + '"', '"' + street + '"', '"' + house + '"')
            result = executequery(db, query, False)
            db.dispose()
            if isinstance(result, Exception):
                return result
            return 'successfully updated house'
        
        db.dispose()
        return 'cannot update house that does not belong to account'

    query = "SELECT EXISTS ( SELECT zip_code FROM sex_offenders WHERE zip_code LIKE {} AND street LIKE {} AND street_number LIKE {} );".format('"' + zipcode + '"', '"' + street + '"', '"' + house + '"')
    result = executequery(db, query, True)
    if isinstance(result, Exception):
        db.dispose()
        return result

    if (result[0])[0]:
        db.dispose()
        return 'cannot add a house in which a sex offender lives'


    query = "INSERT INTO safe_houses (name, lat, lng, street_number, street, zip_code, candy) VALUES ({},{},{},{},{},{},{});".format('"' + name + '"', latitude, longitude, '"' + house + '"', '"' + street + '"', '"' + zipcode + '"', candy)
    result = executequery(db, quer, False)
    db.dispose()
    if isinstance(result, Exception):
        return result

    return 'successfully added new house'



def adressformatcheck(zipcode, street, house):

    if len(zipcode) > 10 or len(zipcode) < 2 or len(street) > 50 or len(street) < 2 or len(house) > 10:
        return False
        
    return True


def adressgeocheck(zipcode, street, house):

    location = None
    geostr = house + " " + street + ", " + zipcode
    geolocator = Nominatim(user_agent="sp00kr4d4r")

    try:
        location = geolocator.geocode(geostr)
    except Exception as ex:
        return ex

    return location



def connect_db():

    # Remember - storing secrets in plaintext is potentially unsafe. Consider using
    # something like https://cloud.google.com/secret-manager/docs/overview to help keep
    # secrets secret.

    pool = None

    try:
        # Remember - storing secrets in plaintext is potentially unsafe. Consider using
        # something like https://cloud.google.com/secret-manager/docs/overview to help keep
        # secrets secret.
        db_user = "root"
        db_pass = "sp00k"
        db_name = "Houses"
        db_socket_dir = "/cloudsql"
        cloud_sql_connection_name = "spook-radar:us-central1:sp00kdb"

        pool = sqlalchemy.create_engine(
            # Equivalent URL:
            # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=<socket_path>/<cloud_sql_instance_name>
            sqlalchemy.engine.url.URL(
                drivername="mysql+pymysql",
                username=db_user,  # e.g. "my-database-user"
                password=db_pass,  # e.g. "my-database-password"
                database=db_name,  # e.g. "my-database-name"
                query={
                    "unix_socket": "{}/{}".format(
                        db_socket_dir,  # e.g. "/cloudsql"
                        cloud_sql_connection_name)  # i.e "<PROJECT-NAME>:<INSTANCE-REGION>:<INSTANCE-NAME>"
                }
            ),
            # ... Specify additional properties here.
        )
    
    except Exception as ex:
        return ex

    return pool

def executequery(db, selstr, res):

    result = None
    try:
        conn = db.connect()
        if res:
            result = conn.execute(selstr).fetchall()
        else:
            conn.execute(selstr)
        conn.close()
    except Exception as ex:
        return ex

    return result
