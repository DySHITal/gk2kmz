import simplekml

BASE = "http://maps.google.com/mapfiles/kml"

# Symbol name -> Google Earth icon URL
ICONS = {
    "Circle":     f"{BASE}/shapes/placemark_circle.png",
    "Square":     f"{BASE}/shapes/placemark_square.png",
    "Triangle":   f"{BASE}/shapes/triangle.png",
    "Star":       f"{BASE}/shapes/star.png",
    "Flag":       f"{BASE}/shapes/flag.png",
    "Target":     f"{BASE}/shapes/target.png",
    "Cross hair": f"{BASE}/shapes/cross-hairs.png",
    "Pushpin":    f"{BASE}/pushpin/ylw-pushpin.png",
}


def hex_to_kml(hex_color: str, opacity: float = 1.0) -> str:
    """Convert '#RRGGBB' to the KML color format 'aabbggrr'."""
    hex_color = hex_color.lstrip("#")
    red, green, blue = (
        hex_color[0:2],
        hex_color[2:4],
        hex_color[4:6],
    )
    alpha = f"{int(opacity * 255):02x}"
    return f"{alpha}{blue}{green}{red}"


def df_to_kmz_points(
    df,
    out_path,
    icon_name="Circle",
    color="#FFFFFF",
    scale=1.0,
):
    kml = simplekml.Kml()
    for row in df.itertuples():
        point = kml.newpoint(
            name=str(row.name),
            coords=[(row.lon, row.lat)],
        )
        point.style.iconstyle.icon.href = ICONS[icon_name]
        point.style.iconstyle.color = hex_to_kml(color)
        point.style.iconstyle.scale = scale

    kml.savekmz(out_path)
    return out_path


def df_to_kmz_polygon(
    df,
    out_path,
    color="#FF0000",
    fill_opacity=0.4,
    line_width=2,
    poly_name="Polygon",
    show_vertices=False,
):
    if len(df) < 3:
        raise ValueError("A polygon needs at least 3 points.")

    kml = simplekml.Kml()
    ring = [(row.lon, row.lat) for row in df.itertuples()]
    ring.append(ring[0])

    polygon = kml.newpolygon(name=poly_name, outerboundaryis=ring)
    polygon.style.polystyle.color = hex_to_kml(color, fill_opacity)
    polygon.style.polystyle.fill = 1
    polygon.style.linestyle.color = hex_to_kml(color, 1.0)
    polygon.style.linestyle.width = line_width

    if show_vertices:
        for row in df.itertuples():
            point = kml.newpoint(
                name=str(row.name),
                coords=[(row.lon, row.lat)],
            )
            point.style.iconstyle.icon.href = ICONS["Circle"]
            point.style.iconstyle.scale = 0.6

    kml.savekmz(out_path)
    return out_path