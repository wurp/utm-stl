"""
Hex tape cell for Rogozhin (4,6) UTM tape cell.

Each tape cell stands vertically on a post, hexagonal cross-section horizontal.
The 6 vertical faces each represent one symbol. Each face has:
  - A 3-bit pattern of pin-holes (drilled at print time, fixed)
  - An engraved label for human readers

Reader on the gantry has 3 spring-loaded plungers. Their up/down state
on the face currently presented to the reader = the symbol.

All tape cells are identical at print time. To "write" symbol X, rotate prism
so face X faces the reader.

Coordinate system:
  +Z = prism long axis (vertical when installed on rail post)
  Bottom face (z=0) has detent dimples that engage a sprung bump on the rail
  Face N's outward normal lies in XY plane at angle N*60° from +X
"""

from build123d import (
    BuildPart, BuildSketch, RegularPolygon, Circle, Sphere, Text,
    Plane, Locations, Location, Mode, Axis, extrude, export_stl,
)
from dataclasses import dataclass, field
import math


@dataclass
class TapeCellConfig:
    # Overall
    across_flats_mm: float = 25.0
    length_mm: float = 22.0
    bore_diameter_mm: float = 5.4   # for 5mm post, FDM clearance

    # Pin-hole encoding
    pin_count_per_face: int = 3
    pin_diameter_mm: float = 2.0
    pin_pitch_mm: float = 4.0
    pin_depth_mm: float = 2.5
    pin_lateral_offset_mm: float = 3.5  # pin column offset from face center

    # Detent dimples on bottom face (engage sprung bump on rail)
    detent_count: int = 6
    detent_ball_diameter_mm: float = 2.0
    detent_radius_factor: float = 0.75  # fraction of apothem

    # Engraved label
    label_size_mm: float = 5.0
    label_depth_mm: float = 0.6
    label_lateral_offset_mm: float = -3.5  # opposite side from pins

    # Symbol encoding: face_patterns[i] is a 3-bit value for face i.
    # Bit 0 = bottom pin, bit 1 = middle, bit 2 = top.
    face_patterns: list[int] = field(default_factory=lambda: [0, 1, 2, 3, 4, 5])
    face_labels: list[str] = field(default_factory=lambda: ["0", "1", "2", "3", "4", "5"])


def make_tape_cell(cfg: TapeCellConfig = TapeCellConfig()):
    apothem = cfg.across_flats_mm / 2

    pin_span = (cfg.pin_count_per_face - 1) * cfg.pin_pitch_mm
    z_first = (cfg.length_mm - pin_span) / 2

    with BuildPart() as prism:
        # Hex body
        with BuildSketch():
            RegularPolygon(radius=apothem, side_count=6, major_radius=False)
        extrude(amount=cfg.length_mm)

        # Through-bore for post
        with BuildSketch(Plane.XY):
            Circle(cfg.bore_diameter_mm / 2)
        extrude(amount=cfg.length_mm, mode=Mode.SUBTRACT)

        # Detent dimples on bottom face (z=0).
        # Sphere centered at z=0 carves a hemispherical recess upward.
        detent_r = apothem * cfg.detent_radius_factor
        for i in range(cfg.detent_count):
            theta = math.radians(i * 360.0 / cfg.detent_count)
            dx = detent_r * math.cos(theta)
            dy = detent_r * math.sin(theta)
            with Locations(Location((dx, dy, 0))):
                Sphere(cfg.detent_ball_diameter_mm / 2, mode=Mode.SUBTRACT)

        # Per-face: pin holes + engraved label
        for face_idx in range(6):
            theta = math.radians(face_idx * 60.0)
            nx, ny = math.cos(theta), math.sin(theta)
            face_origin = (apothem * nx, apothem * ny, cfg.length_mm / 2)
            # Face plane: x_dir = world +Z (along axis), z_dir = outward normal
            face_plane = Plane(
                origin=face_origin,
                x_dir=(0, 0, 1),
                z_dir=(nx, ny, 0),
            )

            # Pin holes (only where pattern bit is set)
            pattern = cfg.face_patterns[face_idx]
            if pattern != 0:
                with BuildSketch(face_plane):
                    for pin_idx in range(cfg.pin_count_per_face):
                        if not ((pattern >> pin_idx) & 1):
                            continue
                        # local x = along prism axis, y = lateral on face
                        local_x = z_first + pin_idx * cfg.pin_pitch_mm - cfg.length_mm / 2
                        local_y = cfg.pin_lateral_offset_mm
                        with Locations((local_x, local_y)):
                            Circle(cfg.pin_diameter_mm / 2)
                extrude(amount=-cfg.pin_depth_mm, mode=Mode.SUBTRACT)

            # Engraved label
            with BuildSketch(face_plane):
                with Locations((0, cfg.label_lateral_offset_mm)):
                    Text(cfg.face_labels[face_idx], font_size=cfg.label_size_mm)
            extrude(amount=-cfg.label_depth_mm, mode=Mode.SUBTRACT)

    return prism.part


if __name__ == "__main__":
    cfg = TapeCellConfig()
    part = make_tape_cell(cfg)
    export_stl(part, "/tmp/tape_cell.stl")
    print(f"Tape cell: {cfg.across_flats_mm}mm AF x {cfg.length_mm}mm tall")
    print(f"Bore: {cfg.bore_diameter_mm}mm")
    print(f"Symbol encoding (face -> 3-bit pattern -> label):")
    for i in range(6):
        bits = format(cfg.face_patterns[i], "03b")
        print(f"  face {i} ({i*60:>3d}deg): {bits}  '{cfg.face_labels[i]}'")
