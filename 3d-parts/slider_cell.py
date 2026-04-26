"""
Linear-slider tape cell for Rogozhin (4,6) UTM.

Each cell holds one slider that translates perpendicular to the tape axis.
Six detent positions along the slider's travel = six symbols. The slider
carries a 6x3 grid of bumps along its length; in any detent position, one
column of 3 bumps sits under three stationary reader probes on the gantry.
That gives a parallel 3-bit read of the symbol.

A lock bar parallel to the tape axis drops into a notch on the slider and
holds it in position. A triangle pin pushed in from the top lifts the lock
bar. The writer arm then drags the slider to a target detent (the arm is
spring-loaded and stops when it hits a peg printed on the transition plate).
The triangle pin withdraws, the lock bar drops, the slider is held.

Coordinate system:
  +X = slider travel direction (perpendicular to tape, "across" the rail)
  +Y = tape axis (cells chain along Y)
  +Z = vertical, reader probes drop from +Z, triangle pin pushed in from +Z

Cell origin is at the bottom-front-left corner of the cell body so cells
tile cleanly along +Y.
"""

from build123d import (
    BuildPart, BuildSketch, Rectangle, Box, Cylinder, Sphere,
    Plane, Locations, Location, Mode, Align, extrude, export_stl,
)
from dataclasses import dataclass, field


@dataclass
class SliderCellConfig:
    # Cell body (the housing the slider lives in)
    cell_pitch_y_mm: float = 25.0           # along tape axis, matches hex cell
    cell_width_x_mm: float = 40.0           # across tape; must contain slider travel + walls
    cell_height_z_mm: float = 12.0          # vertical
    wall_mm: float = 2.0                    # housing wall thickness

    # Slider
    slider_length_x_mm: float = 30.0        # slider total length along travel axis
    slider_width_y_mm: float = 8.0          # along tape axis (narrower than cell pitch)
    slider_height_z_mm: float = 6.0         # vertical
    slider_clearance_mm: float = 0.4        # FDM slip-fit clearance on each side
    slider_travel_mm: float = 15.0          # max travel from one end stop to the other

    # Detents (6 positions along slider travel)
    detent_count: int = 6
    detent_pitch_mm: float = 3.0            # spacing between detents along X
    detent_ball_diameter_mm: float = 1.6    # hemispherical dimple on slider underside

    # Symbol-encoding bumps (6x3 grid on top of slider)
    # Three reader probe lanes along Y, six columns along X aligned with detents.
    pin_diameter_mm: float = 1.8
    pin_height_mm: float = 1.2              # bumps stick UP for probes to feel
    pin_lane_pitch_y_mm: float = 2.0        # spacing of the 3 probe lanes along Y
    # symbol_patterns[i] is a 3-bit value for detent column i.
    # Bit 0 = -Y lane, bit 1 = center lane, bit 2 = +Y lane.
    # Default: codes 1..6 (skip 000 so "no slider" reads as a clearly invalid 0).
    symbol_patterns: list[int] = field(default_factory=lambda: [1, 2, 3, 4, 5, 6])
    symbol_labels: list[str] = field(default_factory=lambda: ["1", "2", "3", "4", "5", "6"])

    # Lock notches on slider top (lock bar is gantry-side, not modeled here)
    lock_notch_width_x_mm: float = 3.0      # along slider travel
    lock_notch_depth_mm: float = 1.5        # depth into slider top
    lock_notch_y_clearance_mm: float = 0.5  # extra Y so the notch crosses the slider

    # Reader probe access: a slot in the top of the housing exposes the
    # 6x3 bump grid to the gantry's probes, and admits the lock bar and
    # triangle pin from above.
    probe_slot_clearance_mm: float = 1.0


def make_slider_cell(cfg: SliderCellConfig = SliderCellConfig()):
    """
    Returns a build123d Part of the cell HOUSING with the slider modeled
    in its 'home' (detent 0) position as a separate solid that prints in
    place inside the housing. After printing, breaking the support material
    frees the slider.

    The result is a single STL containing both the housing and the slider,
    intended to be print-in-place with sufficient clearance gaps that the
    slicer treats them as independent bodies.
    """
    # Derived dimensions
    slot_x = cfg.slider_length_x_mm + cfg.slider_clearance_mm * 2 + cfg.slider_travel_mm
    slot_y = cfg.slider_width_y_mm + cfg.slider_clearance_mm * 2
    slot_z = cfg.slider_height_z_mm + cfg.slider_clearance_mm * 2

    # Probe access slot dimensions (over the slider top, full travel)
    probe_slot_x = slot_x - cfg.wall_mm * 2
    probe_slot_y = slot_y + cfg.probe_slot_clearance_mm * 2

    with BuildPart() as cell:
        # Outer housing block, origin at bottom-front-left corner.
        with BuildSketch():
            with Locations((cfg.cell_width_x_mm / 2, cfg.cell_pitch_y_mm / 2)):
                Rectangle(cfg.cell_width_x_mm, cfg.cell_pitch_y_mm)
        extrude(amount=cfg.cell_height_z_mm)

        # Slider channel (subtract a long slot through the housing).
        slot_z_origin = cfg.wall_mm  # leave a floor under the slider
        with BuildSketch(Plane.XY.offset(slot_z_origin)):
            with Locations((cfg.cell_width_x_mm / 2, cfg.cell_pitch_y_mm / 2)):
                Rectangle(slot_x, slot_y)
        extrude(amount=slot_z, mode=Mode.SUBTRACT)

        # Open the top of the housing above the slider channel so the
        # gantry's reader probes, lock bar, and triangle pin can all reach
        # the slider from above.
        top_slot_z_origin = slot_z_origin + slot_z
        if top_slot_z_origin < cfg.cell_height_z_mm:
            with BuildSketch(Plane.XY.offset(top_slot_z_origin)):
                with Locations((cfg.cell_width_x_mm / 2, cfg.cell_pitch_y_mm / 2)):
                    Rectangle(probe_slot_x, probe_slot_y)
            extrude(
                amount=cfg.cell_height_z_mm - top_slot_z_origin,
                mode=Mode.SUBTRACT,
            )

        # Slider, modeled in its home position (detent 0 against -X end stop).
        slider_x0 = cfg.wall_mm + cfg.slider_clearance_mm
        slider_x_center = slider_x0 + cfg.slider_length_x_mm / 2
        slider_y_center = cfg.cell_pitch_y_mm / 2
        slider_z0 = slot_z_origin + cfg.slider_clearance_mm
        slider_z_center = slider_z0 + cfg.slider_height_z_mm / 2

        with Locations(Location((slider_x_center, slider_y_center, slider_z_center))):
            Box(cfg.slider_length_x_mm, cfg.slider_width_y_mm, cfg.slider_height_z_mm)

        # Detent dimples on slider underside (6 hemispheres carved upward
        # into the slider's bottom face). Sphere centered at slider bottom z.
        slider_top_z = slider_z0 + cfg.slider_height_z_mm
        # Detent column 0 sits at the home X stop; subsequent detents are
        # spaced by detent_pitch_mm toward +X.
        for i in range(cfg.detent_count):
            dx = slider_x0 + cfg.detent_ball_diameter_mm / 2 + i * cfg.detent_pitch_mm
            with Locations(Location((dx, slider_y_center, slider_z0))):
                Sphere(cfg.detent_ball_diameter_mm / 2, mode=Mode.SUBTRACT)

        # Symbol-encoding bumps on slider top: 6 columns x 3 rows.
        # Columns share X with detent positions so that when the slider is
        # latched at detent k, column k of bumps sits under the reader probes.
        # Probes are stationary on the gantry above the cell-pitch-Y center.
        for col in range(cfg.detent_count):
            pattern = cfg.symbol_patterns[col]
            col_x = slider_x0 + cfg.detent_ball_diameter_mm / 2 + col * cfg.detent_pitch_mm
            for lane in range(3):
                if not ((pattern >> lane) & 1):
                    continue
                lane_y = slider_y_center + (lane - 1) * cfg.pin_lane_pitch_y_mm
                with Locations(Location((col_x, lane_y, slider_top_z))):
                    Cylinder(
                        radius=cfg.pin_diameter_mm / 2,
                        height=cfg.pin_height_mm,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )

        # One lock notch per detent column, cut into the slider top.
        notch_y_extent = cfg.slider_width_y_mm + cfg.lock_notch_y_clearance_mm * 2
        for col in range(cfg.detent_count):
            notch_x = slider_x0 + cfg.detent_ball_diameter_mm / 2 + col * cfg.detent_pitch_mm
            with Locations(Location((notch_x, slider_y_center, slider_top_z))):
                Box(
                    cfg.lock_notch_width_x_mm,
                    notch_y_extent,
                    cfg.lock_notch_depth_mm * 2,
                    mode=Mode.SUBTRACT,
                )

    return cell.part


if __name__ == "__main__":
    cfg = SliderCellConfig()
    part = make_slider_cell(cfg)
    export_stl(part, "/tmp/slider_cell.stl")
    print(f"Slider cell: {cfg.cell_width_x_mm} x {cfg.cell_pitch_y_mm} x {cfg.cell_height_z_mm} mm")
    print(f"Slider travel: {cfg.slider_travel_mm} mm, {cfg.detent_count} detents at {cfg.detent_pitch_mm} mm pitch")
    print(f"Symbol encoding (detent column -> 3-bit pattern -> label):")
    for i in range(cfg.detent_count):
        bits = format(cfg.symbol_patterns[i], "03b")
        print(f"  col {i}: {bits}  '{cfg.symbol_labels[i]}'")
