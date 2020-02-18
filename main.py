import geopy
import ssl
import folium
from geopy.distance import great_circle
ssl._create_default_https_context = ssl._create_unverified_context


def create_map(films, pop_locations, year, loc_of_user):
    """(list)
    Creates a HTML map
    """
    world_map = folium.Map()

    fg = folium.FeatureGroup(name="Film")
    for film in films:
        fg.add_child(folium.Marker(location=[float(film[1]), float(film[2])],
                                   popup=locations(film[3])))

    fg2 = folium.FeatureGroup(name="Films per country")
    for film in pop_locations:
        fg2.add_child(folium.Marker(location=[float(film[0]), float(film[1])],
                                   popup=locations(str(pop_locations[film])) + 'films in ' + str(year) + 'year',
                                   icon=folium.Icon(color=color_creator(pop_locations[film]))))

    fg3 = folium.FeatureGroup(name="Your Location")
    loc_of_user = loc_of_user.split(', ')
    fg3.add_child(folium.Marker(location=[float(loc_of_user[0]), float(loc_of_user[1])],
                                popup='You are here!', icon=folium.Icon(color='green')))

    world_map.add_child(fg)
    world_map.add_child(fg2)
    world_map.add_child(fg3)
    world_map.add_child(folium.LayerControl())
    world_map.save(str(year) + "_movies_map_.html")


def locations(location_set):
    """(set) -> (str)
    Return a string of films for a particular location
    :param location_set: set = {(str), ...}
    :return: (str)
    """
    loc = ''
    for location in location_set:
        loc += '- ' + location + '\n'
    return loc


def color_creator(number_of_films):
    """(int) -> (str)
    Return a color of location
    """
    if 0 < number_of_films < 100:
        return 'green'
    elif 101 < number_of_films < 200:
        return 'orange'
    elif 201 < number_of_films < 500:
        return 'red'
    else:
        return 'purple'


def get_distance(film_coordinates, latitude, longitude):
    """(dict), (float), (float) -> (list)
    Return a sorted list of the films data by their distance to user location
    :param film_coordinates: (dict) = {coordinates(tuple)(int): {film(str), ...}, ...)
    :param latitude: (float)
    :param longitude: (float)
    :return: list = [tuple(int, int, int, set(str)), ...]
    """
    film_distance = []
    for film in film_coordinates.keys():
        user_coordinates = (latitude, longitude)
        film_coord = (film[0], film[1])

        distance = great_circle(user_coordinates, film_coord).kilometers
        film_distance.append((distance, film[0], film[1], film_coordinates[film]))

    film_distance.sort(key=lambda x: x[0])
    return film_distance[:10]


def get_film_coordinates(film_dict):
    """(dict) -> (dict)
    Return a dictionary of coordinates of films
    :param film_dict: (dict) = {location(str): {film(str), ...}, ...)
    :return: (dict) = {coordinates(tuple)(int): {film(str), ...}, ...)
    """
    coordinate_dict = dict()
    for location in film_dict.keys():
        try:
            locator = geopy.Nominatim(user_agent="filmGeocoder", timeout=10)
            coordinates = locator.geocode(location)

            coordinate_dict[coordinates.latitude, coordinates.longitude] = film_dict[location]
        except (TypeError, AttributeError, IndexError):
            continue

    return coordinate_dict


def get_films_location(year):
    """(int) -> (set)
    Write down films that match a year in a file
    :param year: (int)
    :return: set = {tuple(str, str), ...)
    """
    locations_set = set()
    f = open('locations.list', 'r', encoding='utf-8', errors='ignore')
    for line in f:
        line = line.strip()

        try:
            if get_year(line) == str(year):
                name = get_title(line)
                location = get_location(line)
                locations_set.add((name, location))
        except IndexError:
            continue
    return locations_set


def get_year(line):
    """(str) -> (str)
    Return a year from a film data
    """
    year = line.split(')')[0][-4:]
    return year


def get_title(line):
    """(str) -> (str)
    Return a title from a film data
    """
    title = line.split(' (')[0]
    return title


def get_location(line):
    """(str) -> (str)
    Return a location of film
    """
    line = line.split('\t')
    for char in line:
        if ',' in char and line.index(char) != 0:
            char_index = line.index(char)
            return line[char_index]


def get_user_country(user_location):
    """(str) -> (str)
    Return a country from a user coordinates
    """
    geo_locator = geopy.Nominatim(user_agent="User Location", timeout=10)
    location = geo_locator.reverse(user_location, language='en')
    location = str(location).split(', ')
    country = location[-1]

    if country == 'United States of America':
        country = 'USA'
    elif country == 'United Kingdom':
        country = 'UK'

    return country


def get_films_in_country(film_set, country):
    """(set), (str) -> (dict)
    Return a dictionary of locations of the films
    :param film_set: (dict) = {(title(str), address(str)), ...}
    :param country: (str)
    :return: (dict) = {location(str): {film(str), ...}, ...)
    """
    film_dict = dict()
    for film in film_set:
        try:
            film_locations = film[1].split(', ')
            film_country = film_locations[-1]
            film_city = film_locations[-2]

            if film_country == country:
                if film_city in film_dict:
                    film_dict[film_city].add(film[0])
                else:
                    film_dict[film_city] = {film[0]}
        except (TypeError, IndexError, AttributeError):
            continue
    return film_dict


def get_popular_locations_dict(film_set):
    """(set) -> (dict)
    Return a dictionary of popular film locations
    :param film_set: set = {tuple((srt), (str)), ...)
    :return: dict = {(str):(int), ... }
    """
    popular_locations = dict()
    for film in film_set:
        try:
            location = film[1].split(', ')[-1]
            if location in popular_locations.keys():
                popular_locations[location] += 1
            else:
                popular_locations[location] = 1
        except (TypeError, AttributeError, IndexError):
            continue

    return popular_locations


if __name__ == "__main__":

    user_loc = input("Please enter your location (format: lat, long): ")
    film_year = int(input("Please enter a year you would like to have a map for: "))

    user_loc1 = user_loc.split(', ')
    latitude1 = float(user_loc1[0])
    longitude1 = float(user_loc1[1])

    print("Map is generating...")

    films_set = get_films_location(film_year)

    print("Please wait...")

    films_dict = get_films_in_country(films_set, get_user_country(user_loc))
    coordinates_dict = get_film_coordinates(films_dict)
    distance_dict = get_film_coordinates(coordinates_dict)
    dist = get_distance(coordinates_dict, latitude1, longitude1)
    popular_locations1 = get_popular_locations_dict(films_set)
    popular_film_coord = get_film_coordinates(popular_locations1)

    create_map(dist, popular_film_coord, film_year, user_loc)

    print(f"Finished. Please have look at the map {film_year}_movies_map.html")
