import numpy as np
import cv2

from psychopy.visual import ImageStim
from psychopy.tools.monitorunittools import convertToPix

from pupil_labs.real_time_screen_gaze import marker_generator


class AprilTagStim(ImageStim):
    def __init__(self, marker_id=0, contrast=1.0, *args, **kwargs):
        self.marker_id = marker_id

        marker_data = marker_generator.generate_marker(marker_id, flip_x=True).astype(float)
        marker_data[marker_data == 0] = -contrast
        marker_data[marker_data > 0] = contrast

        marker_data = np.pad(marker_data, pad_width=1, mode="constant", constant_values=contrast)

        super().__init__(image=marker_data, *args, **kwargs)

    @property
    def marker_verts(self):
        vertices_in_pixels = self._vertices.pix
        size_with_margin = (
            abs(vertices_in_pixels[1][0] - vertices_in_pixels[0][0]),
            abs(vertices_in_pixels[2][1] - vertices_in_pixels[0][1])
        )
        size_without_margin = [v * 0.8 for v in size_with_margin]
        padding = size_with_margin[0] * 0.1

        top_left_pos = vertices_in_pixels[2]

        top_left = (
            top_left_pos[0] + padding,
            top_left_pos[1] - padding
        )
        bottom_right = (
            top_left[0] + size_without_margin[0],
            top_left[1] - size_without_margin[1]
        )

        return (
            top_left,
            (bottom_right[0], top_left[1]),
            bottom_right,
            (top_left[0], bottom_right[1]),
        )


class AprilTagFrameStim(ImageStim):
    def __init__(self, h_count=3, v_count=3, marker_ids=None, marker_size=0.125, marker_units='', contrast=1.0, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.marker_verts = {}

        win_size_pix = convertToPix(np.array([2, 2]), [0, 0], 'norm', self.win).astype(int)
        marker_size_pix = convertToPix(np.array([marker_size, marker_size]), [0, 0], marker_units, self.win).astype(int)
        marker_padding = marker_size_pix[0] / 10
        image_data = np.zeros((win_size_pix[1], win_size_pix[0], 4))

        marker_positions_pix = self._frame_positions(win_size_pix, marker_size_pix[0], [h_count, v_count]).astype(int)

        if marker_ids is None:
            marker_count = 2 * (h_count + v_count) - 4
            marker_ids = list(range(marker_count))

        self.marker_ids = marker_ids

        for marker_id, position_pix in zip(marker_ids, marker_positions_pix):
            marker_data = marker_generator.generate_marker(marker_id, flip_x=True)
            marker_data = np.pad(marker_data, pad_width=1, mode="constant", constant_values=255)
            marker_data = cv2.cvtColor(marker_data.astype(np.float32), cv2.COLOR_GRAY2RGBA)
            marker_data[:, :, 3] = 255
            marker_data = cv2.resize(marker_data, marker_size_pix, fx=0, fy=0, interpolation=cv2.INTER_NEAREST)

            top_left = position_pix
            w = marker_size_pix[0]
            bottom_right = [top_left[0] + w, top_left[1] + w]

            image_data[top_left[1]: bottom_right[1], top_left[0]: bottom_right[0]] = marker_data

            # save marker verts for surface registration
            top_left = [v + marker_padding for v in top_left]
            bottom_right = [v - marker_padding for v in bottom_right]

            top_left[0] -= win_size_pix[0] / 2
            top_left[1] -= win_size_pix[1] / 2
            bottom_right[0] -= win_size_pix[0] / 2
            bottom_right[1] -= win_size_pix[1] / 2

            self.marker_verts[str(marker_id)] = (
                (top_left[0], bottom_right[1]),
                bottom_right,
                (bottom_right[0], top_left[1]),
                top_left,
            )

        # Convert to psychopy color space
        image_data[image_data > 0] = 0.5 + contrast / 2
        image_data[image_data == 0] = 0.5 - contrast / 2

        self.image = image_data

    def _frame_grid(self, h_count, v_count):
        counts = (h_count, v_count)
        direction_offsets = [
            [1, 0],
            [0, 1],
            [-1, 0],
            [0, -1],
        ]
        positions = [[0, 0]]

        for direction_idx, offset in enumerate(direction_offsets):
            for count in range(counts[direction_idx % 2] - 1):
                last_pos = positions[-1]
                p = [v[0] + v[1] for v in zip(last_pos, offset)]
                positions.append(p)

        return positions[:-1]

    def _frame_positions(self, frame_size, marker_size, grid_counts):
        spacing = np.array([
            (frame_size[axis] - marker_size) / (grid_counts[axis] - 1)
            for axis in [0, 1]
        ])

        return spacing * np.array(self._frame_grid(*grid_counts))
