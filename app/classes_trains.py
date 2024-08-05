from app.functions_math import *

class Train:
    def __init__(self, id: int, tile_id: int, last_tile_id: int, coord_world: tuple[float, float], angle: float, type: str = "no_type"):
        """Initialization of the train."""

        # position on the map
        self.id = id
        self.tile_id = tile_id
        self.last_tile_id = last_tile_id
        self.coord_world = coord_world
        self.angle = angle
        self.train_type = type

        # movement parameters
        self.state = "stop" # "no_path"
        self.v_max = 3
        self.v_target = 0
        self.v_current = 0
        self.acceleration = 0.02
        self.turn_speed = 0.01
        self.movement_target = [] # main target of the unit movement
        self.movement_whole_path = [] # whole path to the closest target
        self.movement_free_path = [] # free path to the closest target
        self.run_in_loop = False

    def prepare_data_for_response(self):
        """Prepare Train's data for API response."""
        response = {
            "id": self.id,
            "coord": self.coord_world,
            "angle": self.angle,
            "type": self.train_type,
            "state": self.state,
        }
        return response

    def run(self, map, dict_with_trains):
        """Life-cycle of the train."""

        # check position
        coord_id = map.world2id(self.coord_world)
        current_tile_id = map.get_tile_by_coord_id(coord_id)
        if current_tile_id and current_tile_id != self.tile_id:
            self.last_tile_id = self.tile_id
            self.tile_id = current_tile_id

        # check collisions
        self.check_collisions(dict_with_trains)

        # check current movement target
        if len(self.movement_target):
            if self.movement_target[0] == current_tile_id:
                last_target = self.movement_target.pop(0) # remove the achieved target
                if self.run_in_loop:
                    self.movement_target.append(last_target)
                map.calculate_trains_path(dict_with_trains)

        # check current movement whole path
        if len(self.movement_whole_path):
            if self.movement_whole_path[0] == current_tile_id:
                self.movement_whole_path.pop(0) # remove the achieved tile

        # check current movement free path
        if len(self.movement_free_path):
            if self.movement_free_path[0] == current_tile_id:
                self.movement_free_path.pop(0) # remove the achieved tile

        # set parameters related to train movement
        self.set_velocity()
        self.set_turn_velocity()
        self.accelerate()
        self.set_state()

        # move the train
        if len(self.movement_free_path):  
            self.angle = self.get_new_angle(map.dict_with_tiles[self.movement_free_path[0]].coord_world)
        else:
            emergency_next_track_id = map.find_next_track(self.last_tile_id, self.tile_id)
            if emergency_next_track_id:
                self.angle = self.get_new_angle(map.dict_with_tiles[emergency_next_track_id].coord_world)
        self.coord_world = move_point(self.coord_world, self.v_current, self.angle)

        # add coordinates to trace list
        self.list_with_trace.append(self.coord_world)
        if len(self.list_with_trace) > 100:
            self.list_with_trace.pop(0)

    def find_movement_whole_path(self, map):
        """Find the entire route to the current target."""
        if len(self.movement_target):
            self.movement_whole_path = map.find_route(self.movement_target[0], self.last_tile_id, self.tile_id)
        else:
            self.movement_whole_path = []

    def find_movement_free_path(self, map, dict_with_trains, dict_with_reservations):
        """Select a collision-free start from the found route."""

        self.movement_free_path = []
        considered_segment = []

        # check path
        for tile_id in self.movement_whole_path:
            # check end of segment
            if len(map.dict_with_tiles[tile_id].list_with_tracks) != 2:
                self.movement_free_path += considered_segment
                considered_segment = []
            # check collisions
            if any((self.id != t_id and dict_with_trains[t_id].tile_id == tile_id) for t_id in dict_with_trains):
                break
            # check if the path is not reserved
            if tile_id not in dict_with_reservations: # path is still free
                considered_segment.append(tile_id)
            else:
                break
            # add last segment
            if len(self.movement_target) and tile_id == self.movement_target[0]:
                self.movement_free_path += considered_segment

        # reserve path
        for tile_id in self.movement_free_path:    
            dict_with_reservations[tile_id] = self.id

    def check_collisions(self, dict_with_trains):
        """Check collisions with other trains."""
        for train_id in dict_with_trains:
            if train_id != self.id and dict_with_trains[train_id].tile_id == self.tile_id:
                self.state = "broken"
                self.v_target = 0
                self.v_current = 0
                self.movement_free_path = []
                self.movement_target = []
                # self.color = RED

    def set_velocity(self):
        """Set target velocity based on distance to target."""
        dist = len(self.movement_free_path)
        if not dist: self.v_target = 0
        elif dist < self.v_max: self.v_target = dist
        else: self.v_target = self.v_max

    def set_turn_velocity(self):
        """Set turn velocity based on current linear speed."""
        self.turn_speed = self.v_current / 80

    def set_state(self):
        """Set train status."""
        if self.state != "broken":
            if self.state == "stop" and self.v_current != 0: self.state = "move"
            elif self.state == "move" and self.v_target == 0 and self.v_current == 0: self.state = "stop"

    def accelerate(self):
        """Accelerate the train - calculate the current speed."""
        if self.state != "broken":
            if self.v_target > self.v_current:
                self.v_current += self.acceleration
                if self.v_target < self.v_current: self.v_current = self.v_target
            if self.v_target < self.v_current:
                self.v_current -= self.acceleration
                if self.v_target > self.v_current: self.v_current = self.v_target

    def get_new_angle(self, coord_target: tuple[float, float]) -> float:
        """Return new angle closer to the movement target."""
        target_angle = angle_to_target(self.coord_world, coord_target)
        return turn_to_target_angle(self.angle, target_angle, self.turn_speed)
