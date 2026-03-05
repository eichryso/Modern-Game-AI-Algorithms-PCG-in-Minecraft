import numpy as np

def multi_floor_dimensions(main_x, main_z, main_length, house_width, num_floors):
        """
        Generate dimensions for each floor, shrinking as floors go up.
        Ensures that all floors are at least 15x15.
        Inputs:
        - main_x, main_z: coordinates of the main floor
        - main_length, house_width: dimensions of the main floor
        - num_floors: total number of floors to generate
        Output:
        - List of dicts with keys 'x', 'z', 'width', 'length' for each floor
        """
        min_length, min_width = 15, 15
        prev_length, prev_width = main_length, house_width
        prev_x, prev_z = main_x, main_z
        floor_dims = [{'x': main_x, 'z': main_z, 'width': house_width, 'length': main_length}]
        for i in range(1, num_floors):
            if prev_length <= min_length or prev_width <= min_width:
                break
            next_min_length, next_min_width = max(min_length, prev_length // 2), max(min_width, prev_width // 2)
            if next_min_length >= prev_length or next_min_width >= prev_width:
                break
            length = np.random.randint(next_min_length, prev_length)
            width = np.random.randint(next_min_width, prev_width)
            if length < min_length or width < min_width:
                break
            x = prev_x + (prev_length - length) // 2
            z = prev_z + (prev_width - width) // 2
            floor_dims.append({'x': x, 'z': z, 'width': width, 'length': length})
            prev_length = length
            prev_width = width
            prev_x = x
            prev_z = z
        return floor_dims

def stair_position(floor_dims, floor, stair_positions):
    """
    Find a valid stair position for the given floor.
    Ensures stairs are placed in the overlapping area between current and next floor.
    We use a margin to ensure stairs are not placed at the extreme edges of the overlap area, 
    and we check for proximity to previous and next stairs to avoid overlaps.
    Inputs:
    - floor_dims: list of dicts with dimensions for each floor
    - floor: current floor index
    -stair_positions: dict mapping floor index to (x, z) stair position for already placed stairs
    Output:
    - (stair_x, stair_z) starting coordinates for the stair position on the current floor
    """
    dims = floor_dims[floor]
    x, z, width, length = dims['x'], dims['z'], dims['width'], dims['length']
    stair_x, stair_z = None, None
    if floor+1 < len(floor_dims):
        next_dims = floor_dims[floor+1]
        next_x = next_dims['x']
        next_z = next_dims['z']
        next_width = next_dims['width']
        next_length = next_dims['length']
        prev = stair_positions.get(floor-1) if floor > 0 else None
        next = stair_positions.get(floor+1) if floor+1 < len(floor_dims) else None
        valid_positions = []
        min_x = max(x, next_x)
        min_z = max(z, next_z)
        max_x = min(x+length, next_x+next_length)
        max_z = min(z+width, next_z+next_width)
        filler_margin = 5  
        for sx in range(min_x+filler_margin, max_x-filler_margin):
            for sz in range(min_z+filler_margin, max_z-filler_margin):
                in_current = (x+1 <= sx < x+length-1) and (z+1 <= sz < z+width-1)
                in_next = (next_x+1 <= sx < next_x+next_length-1) and (next_z+1 <= sz < next_z+next_width-1)
                wall_margin = 1
                is_wall = (
                    sx == x+wall_margin or sx == x+length-wall_margin-1 or
                    sz == z+wall_margin or sz == z+width-wall_margin-1 or
                    sx == next_x+wall_margin or sx == next_x+next_length-wall_margin-1 or
                    sz == next_z+wall_margin or sz == next_z+next_width-wall_margin-1
                )
                at_smallest_limit = (
                    sx < min_x+filler_margin or sx >= max_x-filler_margin or
                    sz < min_z+filler_margin or sz >= max_z-filler_margin
                )
                if not (in_current and in_next) or is_wall or at_smallest_limit:
                    continue
                overlap = False
                if prev and abs(sx-prev[0]) < 2 and abs(sz-prev[1]) < 2:
                    overlap = True
                if next and abs(sx-next[0]) < 2 and abs(sz-next[1]) < 2:
                    overlap = True
                if not overlap:
                    valid_positions.append((sx, sz))
        if valid_positions:
            stair_x, stair_z = valid_positions[np.random.randint(len(valid_positions))]
        else:
            # Fallback: place stairs in the center of the overlap area
            overlap_x_min = max(x+filler_margin, next_x+filler_margin)
            overlap_x_max = min(x+length-filler_margin, next_x+next_length-filler_margin)
            overlap_z_min = max(z+filler_margin, next_z+filler_margin)
            overlap_z_max = min(z+width-filler_margin, next_z+next_width-filler_margin)
            stair_x = (overlap_x_min + overlap_x_max) // 2
            stair_z = (overlap_z_min + overlap_z_max) // 2
            if stair_x == x+wall_margin or stair_x == x+length-wall_margin-1 or stair_x == next_x+wall_margin or stair_x == next_x+next_length-wall_margin-1:
                stair_x += 1
            if stair_z == z+wall_margin or stair_z == z+width-wall_margin-1 or stair_z == next_z+wall_margin or stair_z == next_z+next_width-wall_margin-1:
                stair_z += 1
    return stair_x, stair_z