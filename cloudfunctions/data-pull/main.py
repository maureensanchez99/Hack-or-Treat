import sqlalchemy
import math

def request_entry(request):

    if not request.args or 'lat' not in request.args or 'lng' not in request.args or 'rad' not in request.args or 'flag' not in request.args:
        return str(request.args)

    latitude = safe_cast(request.args.get('lat'), float)
    longitude = safe_cast(request.args.get('lng'), float)

    if latitude is None or longitude is None or latitude < -90.0 or latitude > 90.0 or longitude < -180.0 or longitude > 180.0:
        return f'invalid coordinates'

    radius = safe_cast(request.args.get('rad'), float)

    if radius is None or radius < 0.1 or radius > 100.0:
        return f'invalid radius'

    flag = safe_cast(request.args.get('flag'), int)

    if flag is None:
        return f'invalid flag'

    bounds = boundingBox(latitude, longitude, radius)
    latmin = bounds[0]
    longmin = bounds[1]
    latmax = bounds[2]
    longmax = bounds[3]
    result = None

    db = connect_db()
    if isinstance(db, Exception):
        return repr(db)

    if flag == 0:
        query = "SELECT name, zip_code, street, street_number, lat, lng FROM safe_houses WHERE candy IS TRUE AND (lat BETWEEN {} AND {}) AND (lng BETWEEN {} AND {});".format(latmin, latmax, longmin, longmax)
        result = executequery(db, query)

    elif flag == 1:
        query = "SELECT name, zip_code, street, street_number, lat, lng FROM safe_houses WHERE candy IS FALSE AND (lat BETWEEN {} AND {}) AND (lng BETWEEN {} AND {});".format(latmin, latmax, longmin, longmax)
        result = executequery(db, query)

    elif flag == 2:
        query = "SELECT name, zip_code, street, street_number, lat, lng FROM sex_offenders WHERE (lat BETWEEN {} AND {}) AND (lng BETWEEN {} AND {});".format(latmin, latmax, longmin, longmax)
        result = executequery(db, query)

    else:
        db.dispose()
        return 'invalid flag'
    
    db.dispose()
    if isinstance(result, Exception):
            return repr(result)

    if result is None:
        return f'EMPTY'

    return str(result)

# degrees to radians
def deg2rad(degrees):
    return math.pi*degrees/180.0
# radians to degrees
def rad2deg(radians):
    return 180.0*radians/math.pi

# Semi-axes of WGS-84 geoidal reference
WGS84_a = 6378137.0  # Major semiaxis [m]
WGS84_b = 6356752.3  # Minor semiaxis [m]

# Earth radius at a given latitude, according to the WGS-84 ellipsoid [m]
def WGS84EarthRadius(lat):
    # http://en.wikipedia.org/wiki/Earth_radius
    An = WGS84_a*WGS84_a * math.cos(lat)
    Bn = WGS84_b*WGS84_b * math.sin(lat)
    Ad = WGS84_a * math.cos(lat)
    Bd = WGS84_b * math.sin(lat)
    return math.sqrt( (An*An + Bn*Bn)/(Ad*Ad + Bd*Bd) )

# Bounding box surrounding the point at given coordinates,
# assuming local approximation of Earth surface as a sphere
# of radius given by WGS84
def boundingBox(latitudeInDegrees, longitudeInDegrees, halfSideInKm):
    lat = deg2rad(latitudeInDegrees)
    lon = deg2rad(longitudeInDegrees)
    halfSide = 1000*halfSideInKm

    # Radius of Earth at given latitude
    radius = WGS84EarthRadius(lat)
    # Radius of the parallel at given latitude
    pradius = radius*math.cos(lat)

    latMin = lat - halfSide/radius
    latMax = lat + halfSide/radius
    lonMin = lon - halfSide/pradius
    lonMax = lon + halfSide/pradius

    return (rad2deg(latMin), rad2deg(lonMin), rad2deg(latMax), rad2deg(lonMax))

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

def executequery(db, selstr):

    result = None
    try:
        conn = db.connect()
        count = conn.execute(selstr)
        if not count.rowcount:
            conn.close()
            return None
        result = count.fetchall()
        conn.close()
    except Exception as ex:
        return ex

    return result

def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default
