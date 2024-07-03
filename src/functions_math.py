import math


# constants
SQRT3 = math.sqrt(3)


# functions

def world2screen(point, offset_x, offset_y, scale = 1):
# calculate coordinates from world coordinate system to screen coordinate system
# return coordinates in the screen coordinate system
    return ((point[0] + offset_x)*scale, (point[1] + offset_y)*scale)

def screen2world(point, offset_x, offset_y, scale = 1):
# calculate coordinates from screen coordinate system to world coordinate system
# return coordinates in the world coordinate system
    return (point[0]/scale - offset_x, point[1]/scale - offset_y)

def move_point(point, offset, angle):
# function that changes coordinates of point by angle and offset
    return (point[0] + offset * math.cos(angle), point[1] + offset * math.sin(angle))

def move_point_by_vector(point, vector, angle):
# function that changes coordinates of point by adding vector turned by angle
    return (point[0] + vector[0] * math.cos(angle) - vector[1] * math.sin(angle), 
                point[1] + vector[0] * math.sin(angle) + vector[1] * math.cos(angle))

def dist_two_points(point1, point2):
# function that calculates distance between two points
    # return math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)
    return math.hypot(point1[0]-point2[0], point1[1]-point2[1])

def dist_two_points_square(point1, point2):
# function that calculates square of distance between two points
    return (point1[0]-point2[0])**2 + (point1[1]-point2[1])**2

def dist_two_angles(angle1, angle2):
# function that calculates angular distance between two angles
    result = abs(angle1 - angle2)
    if result > math.pi: return 2*math.pi - result
    else: return result

def angle_to_target(origin, target):
# function that calculates angle between two points
# return angle in radians - in the range of 0 to 2pi
    angle = math.atan2(target[1] - origin[1], target[0] - origin[0])
    if angle < 0: angle += 2*math.pi
    return angle

def turn_to_target_angle(origin_angle, target_angle, turn_speed):
# function that slowly (by turn_speed) changes origin_angle in target_angle_direction
# return angle in radians - in the range of 0 to 2pi

    if abs(target_angle - origin_angle) > turn_speed: # damping:

        origin_quadrant = get_quadrant(origin_angle)
        target_quadrant = get_quadrant(target_angle)

        if target_quadrant == origin_quadrant:
            if origin_angle > target_angle:
                origin_angle -= turn_speed
            else:
                origin_angle += turn_speed

        elif target_quadrant == 1:
            if origin_quadrant == 2: origin_angle -= turn_speed
            elif origin_quadrant == 4: origin_angle += turn_speed
            else:
                if origin_angle > target_angle + math.pi:
                    origin_angle += turn_speed
                else:
                    origin_angle -= turn_speed

        elif target_quadrant == 2:
            if origin_quadrant == 1: origin_angle += turn_speed
            elif origin_quadrant == 3: origin_angle -= turn_speed
            else:
                if origin_angle > target_angle + math.pi:
                    origin_angle += turn_speed
                else:
                    origin_angle -= turn_speed

        elif target_quadrant == 3:
            if origin_quadrant == 2: origin_angle += turn_speed
            elif origin_quadrant == 4: origin_angle -= turn_speed
            else:
                if origin_angle > target_angle - math.pi:
                    origin_angle += turn_speed
                else:
                    origin_angle -= turn_speed

        elif target_quadrant == 4:
            if origin_quadrant == 1: origin_angle -= turn_speed
            elif origin_quadrant == 3: origin_angle += turn_speed
            else:
                if origin_angle > target_angle - math.pi:
                    origin_angle += turn_speed
                else:
                    origin_angle -= turn_speed
                    
        else:
            if origin_angle > target_angle:
                origin_angle -= turn_speed
            else:
                origin_angle += turn_speed

    else:
        origin_angle = target_angle

    if origin_angle > 2*math.pi: origin_angle -= 2*math.pi
    elif origin_angle < 0: origin_angle += 2*math.pi

    return origin_angle

def get_quadrant(angle):
# return quadrant of the coordinate system
    if angle < 0 : return 0
    elif angle <= math.pi / 2: return 1
    elif angle <= math.pi: return 2
    elif angle <= 3 * math.pi / 2 : return 3
    elif angle <= 2 * math.pi: return 4
    else: return 5