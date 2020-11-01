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
    
    if 'candy' in args and not 'delete' in args:

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
        
        updatehouse(name, zipcode, street, house, location.latitude, location.longitude, candy)


    elif 'delete' in args and not 'candy' in args:

        if str(request.args.get('delete')) != "DELETE":
            return f'did not delete entry'

        if not adressformatcheck(zipcode, street, house):
            return f'invalid adress'

        deletehouse(zipcode, street, house)

    else:
        return f'invalid request format'

    return f'success'



def deletehouse(zipcode, street, house):




    return



def updatehouse(name, zipcode, street, house, latitude, longitude, candy):




    return



def adressformatcheck(zipcode, street, house):

    if len(zipcode) > 10 or if len(zipcode) < 2 or if len(street) > 50 or if len(street) < 2 or if len(house) > 10:
        return False
        
    return True


def adressgeocheck(zipcode, street, house):

    location = None
    geostr = house + " " + street + ", " + zipcode
    geolocator = Nominatim(user_agent="sp00kr4d4r")

    try:
        location = geolocator.geocode(geostr)
    except Exception ex:
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
    
    except Exception ex:
        return ex

    return pool
