import simplekml
from haversine import haversine, Unit
import os

"""
GROUP 10 - Fast and Safe Route Planning Project
@authors: Mihir Naresh Shah (ms8830@rit.edu), Abhinandan Desai (ad2724@rit.edu)
This file is a project in which we are given 173 .txt files which contain the $GPRMC and its corresponding
$GPGGA data. We have preprocessed and cleaned the data before analysing the data. The aim of this project is to
find the best possible route considering the trip time, stop signs, left right turns, errands and stops at traffic
signals. We also convert the .txt files to kml files so that they can be plotted on google earth.

Referred the following link for creating KML files:
1) https://simplekml.readthedocs.io/en/latest/styling.html
2) https://simplekml.readthedocs.io/en/latest/gettingstarted.html
"""

cost_function_list = []
file_name_list = []
stops_list_of_dict = []

def readCoord(file, name):
    """
    The function takes in the text file and processes it to calculate
    the latitudes, longitudes, and speed of the car at each point. This data
    is then used to create the KML file.
    :param file: file with the gps data
    :param name: name of the file
    :return:
    """
    list1 = []  # This list will store each and every line of $GPRMC data in the form of list of its attributes

    # Each line in the file is separated and saved as a list in list1
    for i in range(len(file)):
        list1.append(file[i].split(","))

    kml_coordinates = []

    for i in range(5, len(list1)):
        if list1[i][0] == "$GPRMC":  # data required is in these lines
            if list1[i][2] == 'A':  # we check if the data is valid or not
                if len(list1[i]) == 13:
                    # print(list1[i], i)
                    co_ordinate_list = []

                    # Checking for longitude values
                    if list1[i][6] == "E":
                        val = conversion(float(list1[i][5]))
                        co_ordinate_list.append(val)
                    else:
                        val = conversion(float(list1[i][5]))
                        co_ordinate_list.append((-1) * val)  # negative value for West

                    # Checking for latitude values
                    if list1[i][4] == "N":
                        val = conversion(float(list1[i][3]))
                        co_ordinate_list.append(val)
                    else:
                        val = conversion(float(list1[i][3]))
                        co_ordinate_list.append((-1) * val)  # negative value for South

                    co_ordinate_list.append(float(list1[i][7]))  # speed for that co-ordinate is saved
                    co_ordinate_list.append(list1[i][1])  # time recorded for that co-ordinate
                    co_ordinate_list.append(list1[i][8])  # tracking angle for that co-ordinate
                    kml_coordinates.append(co_ordinate_list)  # Each 5 value tuple is saved
    kml = simplekml.Kml()

    list2 = []  # This list is specifically created for inserting co-ordinates for creating kml file

    # Converting each list to tuple as kml accepts tuples
    for row in kml_coordinates:
        #  att contains the lat, long, time, speed and tracking angle.
        att = (row[0], row[1], row[2], float(row[3]), float(row[4]))
        list2.append(att)

    start_coordinate = (list2[0][0], list2[0][1])
    end_coordinate = (list2[len(list2) - 1][0], list2[len(list2) - 1][1])

    # check if coordinates
    if not within_radius(start_coordinate, end_coordinate):
        print("Invalid file...")
        return []
    print("Valid file...")

    ls = kml.newlinestring(extrude=1)
    ls.description = "Speed in knots, instead of altitude"

    # 'relativetoground' shows the variations in the speed of the car at different
    # points in the route.
    ls.altitudemode = simplekml.AltitudeMode.relativetoground

    ls.tessellate = 1

    # Saving the tuples for kml file
    ls.coords = list2
    ls.style.linestyle.width = 4
    ls.style.linestyle.color = simplekml.Color.yellow

    # Creating the kml file
    kmlFile = name + ".kml"
    kml.save("C:\\Users\\Naresh Shah\\PycharmProjects\\BDAproject\\kmlFiles\\" + kmlFile)
    return list2


def within_radius(start_coordinate, end_coordinate):
    """
    This function is created to check the starting and ending point of the data. This will help to discard the
    files which doesn't have the starting point and ending point within 175 meters of coord1 and coord2 respectively
    or vice versa.

    :param start_coordinate:
    :param end_coordinate:
    :return:
    """

    # coord1 and coord2 taken from the same files where data was valid
    coord1 = (-77.68016333333334,43.085848333333324)
    coord2 = (-77.43771166666667,43.138343333333324)

    if haversine(start_coordinate, coord1, unit=Unit.METERS) <= 175 and haversine(end_coordinate, coord2,
                                                                                  unit=Unit.METERS) <= 175:
        return True
    elif haversine(start_coordinate, coord2, unit=Unit.METERS) <= 175 and haversine(end_coordinate, coord1,
                                                                                  unit=Unit.METERS) <= 175:
        return True
    else:
        return False


def conversion(input_val):
    """
    This function helps convert the latitudes, longitudes to fractional degrees.
    :param input_val: coordinate in the form of (degrees*100 + minutes)
    :return: converted coordinates in the form of fractional degrees
    """
    # original value is in the format: degrees*100 + minutes
    # So we firstly divide by 100 and then split it on the decimal
    new_val = str(float(input_val / 100))
    new_val = new_val.split(".")

    val1 = float(new_val[0])
    val2 = float(input_val - (float(new_val[0]) * 100))  # this calculation gives us the minute fragment
    # of the input value

    # final result we get is the required fractional degree
    result = val1 + (val2 / 60)  # we divide by 60 to convert val2 from minutes to degrees

    return result


def openFile():
    """
    This function takes in each text file and parses it.
    :param:
    :return:
    """
    path = 'C:\\Users\\Naresh Shah\\PycharmProjects\\BDAproject\\FILES_TO_WORK'
    fileList = []
    fileName_list = []
    for filename in os.listdir(path):
        file = path + "\\" + filename
        name = filename[:len(filename) - 4]
        txtFile = filename
        file = open(file).read().splitlines()
        print(txtFile+":")
        gps_data = readCoord(file, name)
        if (len(gps_data) < 2):
            print()
            continue
        global file_name_list
        file_name_list.append(txtFile)
        detect_stops(gps_data)
        print()


def detect_left_or_right(gps_data, start, left_right_coordinates, skip_size):
    """
    This function is specifically created to identify the left and the right turns on the entire data set.
    The left and the right turns are identified irrespective of any traffic signal or stop signs present at
    that turn.

    gps_data has the following attributes:
    0 - latitudes
    1 - longitudes
    2 - speed
    3 - time
    4 - tracking angle

    :param gps_data: contains the attributes as mentioned above
    :param start: starting coordinate
    :param left_right_coordinates: list in which the coordinates are to be stored
    :param skip_size: This is the window size to which the current coordinate will be compared to
    :return:
    """

    while(start < len(gps_data) - skip_size):
        current_coord = gps_data[start][4]
        next_coord = gps_data[start + skip_size][4]

        if current_coord < next_coord and -120 < current_coord - next_coord < -60:
            # right turn
            left_right_coordinates.append((gps_data[start][0], gps_data[start][1]))  # store the coordinates
            start = start + skip_size
        elif current_coord <= next_coord and 60 < current_coord - next_coord + 360 < 120:
            # handles values in which current_coord is 0.16 degrees and next_coord is 358.2 degrees
            left_right_coordinates.append((gps_data[start][0], gps_data[start][1]))  # store the coordinates
            start = start + skip_size
        elif current_coord > next_coord and 60 < current_coord - next_coord < 120:
            # left turn
            left_right_coordinates.append((gps_data[start][0], gps_data[start][1]))  # store the coordinates
            start = start + skip_size
        else:
            # if no turn detected
            start += 1
    return left_right_coordinates


def detect_specific_stops(gps_data, stop_signs, traffic_signals, errands, start):
    """
    This function is created to detect three things:
        - Stop signs (Which includes left and right turns but will be counted as a different coordinate)
        - traffic signals
        - errands

    gps_data has the following attributes:
    0 - latitudes
    1 - longitudes
    2 - speed
    3 - time
    4 - tracking angle
    :param gps_data: contains the attributes as mentioned above
    :param stop_signs: list in which stop_signs coordinates are to be stored
    :param traffic_signals: list in which traffic_signals coordinates are to be stored
    :param errands: list in which errands coordinates are to be stored
    :param start: starting coordinate
    :return:
    """
    time_at_stops = 0
    while(start < len(gps_data)):
        current_coordinates = (gps_data[start][0], gps_data[start][1])
        current_speed = gps_data[start][2] * 1.1508
        current_time = gps_data[start][3]


        if(current_speed <= 10):

            next_point = 0
            # print(i, (gps_data[i][2] * 1.1508), (gps_data[i][0], gps_data[i][1]))
            if(start < len(gps_data) - 1):
                next_point = start + 1
            new_speed = (gps_data[next_point][2]*1.1508)
            # print(new_speed)
            while((0.0 <= new_speed <= 10) and next_point < len(gps_data)-1):
                new_speed = (gps_data[next_point][2] * 1.1508)
                next_point += 1


            # list_of_coordinates.append(gps_data[i])

            new_coordinates = (gps_data[next_point][0], gps_data[next_point][1])
            new_time = gps_data[next_point][3]
            # print(current_time, new_time)
            time_difference = abs(float(current_time) - float(new_time))
            haversine_distance = haversine(current_coordinates, new_coordinates, unit=Unit.MILES)
            if haversine_distance < 0.09:
                if (time_difference <= 7):
                    stop_signs.append(gps_data[start])  # stop_sign
                    time_at_stops += time_difference
                elif (7 < time_difference and time_difference <= 50):
                    traffic_signals.append(gps_data[start])  # traffic
                    time_at_stops += time_difference
                else:
                    if (time_difference > 50):
                        errands.append(gps_data[start])  # errands
                        time_at_stops += time_difference
            start = next_point
        start += 1

    return stop_signs, traffic_signals, errands, time_at_stops


def detect_stops(gps_data):
    """
    Detecting left_right turns and stop_signs, traffic_signals and errands
    gps_data has the following attributes:
    0 - latitudes
    1 - longitudes
    2 - speed
    3 - time
    4 - tracking angle
    :param gps_data: contains the attributes as mentioned above
    :return:
    """
    left_right_coordinates = []  # list in which the left right coordinates are to be stored
    stop_signs = []  # list in which the stop_signs coordinates are to be stored
    traffic_signals = []  # list in which the traffic_signals coordinates are to be stored
    errands = []  # list in which the errands coordinates are to be stored
    skip_size = 30
    i = 0  # start coordinate

    dict1 = {}

    # Here we are skipping the initial coordinates where speed is less than 10 mph otherwise they might be considered
    # as stop signs or turns
    while (i < len(gps_data) and gps_data[i][2] <= 10):
        i += 1
    start = i

    left_right_coordinates = detect_left_or_right(gps_data, start, left_right_coordinates, skip_size)

    stop_signs, traffic_signals, errands, time_at_stops = detect_specific_stops(gps_data, stop_signs, traffic_signals,
                                                                                errands, start)
    dict1['gps_data'] = gps_data
    dict1['left_right_coordinates'] = left_right_coordinates
    dict1['stop_signs'] = stop_signs
    dict1['traffic_signals'] = traffic_signals
    dict1['errands'] = errands

    global stops_list_of_dict
    stops_list_of_dict.append(dict1)

    calculate_tripTime(gps_data, stop_signs, traffic_signals, errands, time_at_stops, left_right_coordinates)

def calculate_tripTime(gps_data, stop_signs, traffic_signals, errands, time_at_stops, left_right_coordinates):
    """
    We are calculating the time of the entire trip in seconds

    :param gps_data: contains the attributes as mentioned above
    :param stop_signs: list of coordinates with stop signs
    :param traffic_signals: list of coordinates with traffic signals
    :param errands: list of coordinates where vehicles were stopped for errands
    :param time_at_stops: total time spent at all the stop signs, traffic signals and errands.
    :param left_right_coordinates: list of coordinates with left and right turns
    :return:
    """

    # trip time here is the difference between the first time and the last time.
    trip_time = abs(gps_data[0][3] - gps_data[len(gps_data)-1][3])
    cost_function(trip_time, gps_data, stop_signs, traffic_signals, errands, time_at_stops, left_right_coordinates)

def cost_function(trip_time, gps_data, stop_signs, traffic_signals, errands, time_at_stops, left_right_coordinates):
    """
    We are calculating the cost function through which we will be able to identify the best route. Our cost
    function consists of an objective function which is the trip time and we have added a regularization which
    includes max velocity, number of left right coordinates, time spent at stop signs and total number of stops.

    :param gps_data: contains the attributes as mentioned above
    :param stop_signs: list of coordinates with stop signs
    :param traffic_signals: list of coordinates with traffic signals
    :param errands: list of coordinates where vehicles were stopped for errands
    :param time_at_stops: total time spent at all the stop signs, traffic signals and errands.
    :param left_right_coordinates: list of coordinates with left and right turns
    :return:
    """
    velocity = []  # list of all velocities
    global file_name_list
    global cost_function_list
    for i in range(len(gps_data)):
        velocity.append(gps_data[i][2]*1.1508)

    max_velocity = max(velocity)
    time_at_stops_minutes = time_at_stops/60

    total_stops = len(stop_signs) + len(traffic_signals) + len(left_right_coordinates) + len(errands)
    final_cost_function = (0.5*(trip_time/30)) + (0.15*(time_at_stops_minutes/15)) + (0.15*(len(left_right_coordinates)/40))
    (0.1*(total_stops/20)) + (0.1*(max_velocity/60))


    cost_function_list.append(final_cost_function)
    print("trip time: ", (trip_time/60), "mins", " ----> cost: ", final_cost_function)


def create_best_kml(filename, gps_data, left_right_coordinates, stop_signs, traffic_signals, errands):
    """
    Creates 5 kml files i.e.
        - kml file of the actual txt file
        - kml file for stop signs
        - kml file for traffic signals
        - kml file for errands
        - kml file for left and right coordinates

    :param filename: name of the file
    :param gps_data: contains the attributes as mentioned above
    :param stop_signs: list of coordinates with stop signs
    :param traffic_signals: list of coordinates with traffic signals
    :param errands: list of coordinates where vehicles were stopped for errands
    :param left_right_coordinates: list of coordinates with left and right turns
    :return:
    """

    #  kml file of the gps data
    name = filename[:len(filename) - 4]
    kml = simplekml.Kml()
    ls = kml.newlinestring(extrude=1)
    ls.description = "Speed in knots, instead of altitude"
    ls.altitudemode = simplekml.AltitudeMode.relativetoground
    ls.tessellate = 1
    # Saving the tuples for kml file
    ls.coords = gps_data
    ls.style.linestyle.width = 4
    ls.style.linestyle.color = simplekml.Color.yellow

    # Creating the kml file
    kmlFile = name + ".kml"
    kml.save("C:\\Users\\Naresh Shah\\PycharmProjects\\BDAproject\\final_kml\\" + kmlFile)

    #  kml file of the left and right coordinates
    kml = simplekml.Kml()
    ls = kml.newpoint()
    ls.description = "Speed in knots, instead of altitude"
    ls.altitudemode = simplekml.AltitudeMode.relativetoground
    ls.tessellate = 1
    style = simplekml.Style()
    # Saving the tuples for kml file
    for i in range(len(left_right_coordinates)):
        pnt = kml.newpoint(name='Point: {0}, {1}'.format(left_right_coordinates[i][0], left_right_coordinates[i][1]))
        pnt.coords = [(left_right_coordinates[i][0], left_right_coordinates[i][1])]
        pnt.style = style
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/purple-circle.png'
    kmlFile_n = "left_right.kml"
    kml.save("C:\\Users\\Naresh Shah\\PycharmProjects\\BDAproject\\final_kml\\" + kmlFile_n)

    #  kml file of the stop signals coordinates
    kml = simplekml.Kml()
    ls1 = kml.newpoint()
    ls1.description = "Speed in knots, instead of altitude"
    ls1.altitudemode = simplekml.AltitudeMode.relativetoground
    ls1.tessellate = 1
    style = simplekml.Style()
    # Saving the tuples for kml file
    for i in range(len(stop_signs)):  # Generate longitude values
        pnt = kml.newpoint(name='Point: {0}, {1}'.format(stop_signs[i][0], stop_signs[i][1]))
        pnt.coords = [(stop_signs[i][0], stop_signs[i][1])]
        pnt.style = style
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/red-circle.png'
    kmlFile_n = "stop_signs.kml"
    kml.save("C:\\Users\\Naresh Shah\\PycharmProjects\\BDAproject\\final_kml\\" + kmlFile_n)

    #  kml file of the traffic signals coordinates
    kml = simplekml.Kml()
    ls2 = kml.newpoint()
    ls2.description = "Speed in knots, instead of altitude"
    ls2.altitudemode = simplekml.AltitudeMode.relativetoground
    ls2.tessellate = 1
    style = simplekml.Style()
    # Saving the tuples for kml file
    for i in range(len(traffic_signals)):  # Generate longitude values
        pnt = kml.newpoint(name='Point: {0}, {1}'.format(traffic_signals[i][0], traffic_signals[i][1]))
        pnt.coords = [(traffic_signals[i][0], traffic_signals[i][1])]
        pnt.style = style
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/grn-circle.png'
    kmlFile_n = "traffic_signal.kml"
    kml.save("C:\\Users\\Naresh Shah\\PycharmProjects\\BDAproject\\final_kml\\" + kmlFile_n)

    #  kml file of the errands coordinates
    kml = simplekml.Kml()
    ls3 = kml.newpoint()
    ls3.description = "Speed in knots, instead of altitude"
    ls3.altitudemode = simplekml.AltitudeMode.relativetoground
    ls3.tessellate = 1
    style = simplekml.Style()
    # Saving the tuples for kml file
    for i in range(len(errands)):  # Generate longitude values
        pnt = kml.newpoint(name='Point: {0}, {1}'.format(errands[i][0], errands[i][1]))
        pnt.coords = [(errands[i][0], errands[i][1])]
        pnt.style = style
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/orange-circle.png'
    kmlFile_n = "errands.kml"
    kml.save("C:\\Users\\Naresh Shah\\PycharmProjects\\BDAproject\\final_kml\\" + kmlFile_n)

def all_stops_together(filename, gps_data, left_right_coordinates, stop_signs, traffic_signals, errands):
    """
    Creates a kml file with all the stop markers in the same file.

    :param filename: name of the file
    :param gps_data: contains the attributes as mentioned above
    :param stop_signs: list of coordinates with stop signs
    :param traffic_signals: list of coordinates with traffic signals
    :param errands: list of coordinates where vehicles were stopped for errands
    :param left_right_coordinates: list of coordinates with left and right turns
    :return:
    """
    name = filename[:len(filename) - 4]

    # Creating the kml file
    kml = simplekml.Kml()
    ls = kml.newpoint()
    ls.description = "Speed in knots, instead of altitude"
    ls.altitudemode = simplekml.AltitudeMode.relativetoground
    ls.tessellate = 1
    style = simplekml.Style()
    # Saving the tuples for kml file
    for i in range(len(left_right_coordinates)):
        pnt = kml.newpoint(name='Point: {0}, {1}'.format(left_right_coordinates[i][0], left_right_coordinates[i][1]))
        pnt.coords = [(left_right_coordinates[i][0], left_right_coordinates[i][1])]
        pnt.style = style
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/purple-circle.png'

    ls1 = kml.newpoint()
    ls1.description = "Speed in knots, instead of altitude"
    ls1.altitudemode = simplekml.AltitudeMode.relativetoground
    ls1.tessellate = 1
    style = simplekml.Style()
    # Saving the tuples for kml file
    for i in range(len(stop_signs)):  # Generate longitude values
        pnt = kml.newpoint(name='Point: {0}, {1}'.format(stop_signs[i][0], stop_signs[i][1]))
        pnt.coords = [(stop_signs[i][0], stop_signs[i][1])]
        pnt.style = style
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/red-circle.png'

    ls2 = kml.newpoint()
    ls2.description = "Speed in knots, instead of altitude"
    ls2.altitudemode = simplekml.AltitudeMode.relativetoground
    ls2.tessellate = 1
    style = simplekml.Style()
    # Saving the tuples for kml file
    for i in range(len(traffic_signals)):  # Generate longitude values
        pnt = kml.newpoint(name='Point: {0}, {1}'.format(traffic_signals[i][0], traffic_signals[i][1]))
        pnt.coords = [(traffic_signals[i][0], traffic_signals[i][1])]
        pnt.style = style
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/grn-circle.png'


    ls3 = kml.newpoint()
    ls3.description = "Speed in knots, instead of altitude"
    ls3.altitudemode = simplekml.AltitudeMode.relativetoground
    ls3.tessellate = 1
    style = simplekml.Style()
    # Saving the tuples for kml file
    for i in range(len(errands)):  # Generate longitude values
        pnt = kml.newpoint(name='Point: {0}, {1}'.format(errands[i][0], errands[i][1]))
        pnt.coords = [(errands[i][0], errands[i][1])]
        pnt.style = style
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/orange-circle.png'
    kmlFile = "GPS_Hazards.kml"
    kml.save("C:\\Users\\Naresh Shah\\PycharmProjects\\BDAproject\\final_kml\\" + kmlFile)



def main():
    global file_name_list
    global cost_function_list
    global stops_list_of_dict
    print('Reading 173 kml files...')
    openFile()
    min_cost_index = cost_function_list.index(min(cost_function_list))
    file_name_min_cost = file_name_list[min_cost_index]
    dictonary = stops_list_of_dict[min_cost_index]
    print()
    print("-------------------------------------------------------------------------------")
    print("file with minimum cost: ", file_name_min_cost,)
    print("Calculated cost: ", min(cost_function_list))
    print("-------------------------------------------------------------------------------")

    create_best_kml(file_name_min_cost, dictonary['gps_data'], dictonary['left_right_coordinates'], dictonary['stop_signs'],
                                                                    dictonary['traffic_signals'], dictonary['errands'])

    all_stops_together(file_name_min_cost, dictonary['gps_data'], dictonary['left_right_coordinates'], dictonary['stop_signs'],
                                                                    dictonary['traffic_signals'], dictonary['errands'])
main()

