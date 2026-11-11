"""Procedural placeholder visualizations for the Blatec project (HP DOMY).
Usage: python3 scene.py <shot> <out.png> [samples] [width] [height]
Shots: hero, street, bungalow, garden, aerial
"""
import sys, math, random
import bpy
from mathutils import Vector

shot = sys.argv[1]
out = sys.argv[2]
samples = int(sys.argv[3]) if len(sys.argv) > 3 else 48
EXPO = float(sys.argv[6]) if len(sys.argv) > 6 else -1.0
W = int(sys.argv[4]) if len(sys.argv) > 4 else 1600
H = int(sys.argv[5]) if len(sys.argv) > 5 else 900
random.seed(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------- materials ----------
def mat(name, color, rough=0.6, metal=0.0, spec=0.5, emit=None, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = spec
    if coat and "Coat Weight" in b.inputs:
        b.inputs["Coat Weight"].default_value = coat
    if emit:
        b.inputs["Emission Color"].default_value = (*emit[0], 1)
        b.inputs["Emission Strength"].default_value = emit[1]
    return m

def noise_mat(name, c1, c2, scale=6.0, rough=0.8, bump=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 8
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*c1, 1)
    ramp.color_ramp.elements[1].color = (*c2, 1)
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    if bump:
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = bump
        nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

def wood_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    wv = nt.nodes.new("ShaderNodeTexWave")
    wv.wave_type = 'BANDS'
    wv.bands_direction = 'Z'
    wv.inputs["Scale"].default_value = 3.0
    wv.inputs["Distortion"].default_value = 6
    wv.inputs["Detail"].default_value = 4
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.20, 0.105, 0.05, 1)
    ramp.color_ramp.elements[1].color = (0.42, 0.24, 0.12, 1)
    nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
    nt.links.new(wv.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.55
    return m

M = {
    "plaster": noise_mat("plaster", (0.80, 0.79, 0.76), (0.86, 0.85, 0.82), 40, 0.85, 0.05),
    "plaster_dark": mat("plaster_dark", (0.055, 0.056, 0.058), 0.7),
    "frame": mat("frame", (0.025, 0.026, 0.028), 0.35, 0.3),
    "glass": mat("glass", (0.012, 0.016, 0.02), 0.03, 0.0, 1.0, coat=0.0),
    "wood": wood_mat("wood"),
    "grass": noise_mat("grass", (0.06, 0.13, 0.03), (0.13, 0.22, 0.05), 3, 0.95, 0.1),
    "paving": noise_mat("paving", (0.30, 0.30, 0.29), (0.42, 0.41, 0.39), 25, 0.8, 0.1),
    "asphalt": noise_mat("asphalt", (0.05, 0.05, 0.055), (0.11, 0.11, 0.115), 60, 0.9, 0.05),
    "gravel": noise_mat("gravel", (0.35, 0.33, 0.30), (0.55, 0.52, 0.48), 80, 0.9, 0.3),
    "leaf": noise_mat("leaf", (0.05, 0.12, 0.03), (0.16, 0.25, 0.06), 4, 0.8, 0.2),
    "leaf2": noise_mat("leaf2", (0.12, 0.13, 0.03), (0.25, 0.27, 0.08), 4, 0.8, 0.2),
    "trunk": mat("trunk", (0.09, 0.07, 0.05), 0.9),
    "fence": mat("fence", (0.04, 0.042, 0.045), 0.5, 0.4),
    "soil": noise_mat("soil", (0.09, 0.06, 0.04), (0.16, 0.11, 0.07), 10, 0.95, 0.2),
    "warm": mat("warm", (0.9, 0.7, 0.45), 0.5, emit=((1.0, 0.72, 0.42), 6.0)),
    "car": mat("car", (0.35, 0.36, 0.38), 0.25, 0.8, coat=1.0),
    "tyre": mat("tyre", (0.02, 0.02, 0.02), 0.8),
    "white": mat("white", (0.82, 0.82, 0.80), 0.4),
}

CLAY = True
if CLAY:
    def _c(name, rgb, rough=0.8):
        M[name] = noise_mat(name + "_c", tuple(v * 0.97 for v in rgb), rgb, 30, rough, 0.04)
    _c("grass", (0.50, 0.50, 0.475), 0.95)
    _c("leaf", (0.78, 0.78, 0.75), 0.9)
    _c("leaf2", (0.72, 0.72, 0.69), 0.9)
    _c("asphalt", (0.24, 0.24, 0.245), 0.9)
    _c("paving", (0.62, 0.62, 0.60), 0.85)
    _c("gravel", (0.50, 0.49, 0.47), 0.9)
    _c("trunk", (0.40, 0.39, 0.37), 0.9)
    M["car"] = mat("car_c", (0.80, 0.80, 0.78), 0.5)
    M["plaster"] = noise_mat("plaster_c", (0.90, 0.895, 0.88), (0.93, 0.925, 0.91), 40, 0.85, 0.03)

def box(name, loc, size, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(material)
    if bevel:
        mod = o.modifiers.new("bv", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return o

def window(wall, x, y, z, w, h, axis="y", depth=0.25, frame=0.06, divide=0, warm=False):
    """window on a wall facing -y (axis='y') or -x/+x. (x,y,z) = center of opening on wall face."""
    if axis == "y":
        cut(wall, (x, y, z), (w, depth * 2, h))
        box("glass", (x, y + depth * 0.5, z), (w, 0.04, h), M["warm"] if warm else M["glass"])
        box("reveal", (x, y + depth * 0.25, z + h / 2), (w + 0.02, depth * 0.5, 0.02), M["frame"])
        for dx in (-w / 2, w / 2):
            box("f", (x + dx, y + depth * 0.4, z), (frame, 0.08, h), M["frame"])
        for dz in (-h / 2, h / 2):
            box("f", (x, y + depth * 0.4, z + dz), (w, 0.08, frame), M["frame"])
        for i in range(1, divide + 1):
            box("f", (x - w / 2 + w * i / (divide + 1), y + depth * 0.4, z), (frame * 0.8, 0.08, h), M["frame"])
    else:
        sgn = 1 if axis == "x+" else -1
        cut(wall, (x, y, z), (depth * 2, w, h))
        box("glass", (x - sgn * depth * 0.5, y, z), (0.04, w, h), M["warm"] if warm else M["glass"])
        for dy in (-w / 2, w / 2):
            box("f", (x - sgn * depth * 0.4, y + dy, z), (0.08, frame, h), M["frame"])
        for dz in (-h / 2, h / 2):
            box("f", (x - sgn * depth * 0.4, y, z + dz), (0.08, w, frame), M["frame"])

def cut(target, loc, size):
    c = box("cutter", loc, size, M["frame"])
    mod = target.modifiers.new("cut", "BOOLEAN")
    mod.object = c
    mod.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(c, do_unlink=True)

def tree(x, y, h=6.0, r=2.0, kind=0):
    box("trunk", (x, y, h * 0.3), (0.22, 0.22, h * 0.6), M["trunk"])
    for i in range(3):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=r * random.uniform(0.7, 1.0),
                                              location=(x + random.uniform(-0.6, 0.6), y + random.uniform(-0.6, 0.6),
                                                        h * 0.62 + random.uniform(-0.3, 0.9)))
        o = bpy.context.active_object
        o.scale = (1, 1, random.uniform(0.9, 1.25))
        d = o.modifiers.new("d", "DISPLACE")
        tex = bpy.data.textures.new("t", "CLOUDS")
        tex.noise_scale = 0.5
        d.texture = tex
        d.strength = 0.6
        o.data.materials.append(M["leaf"] if kind == 0 else M["leaf2"])
        bpy.ops.object.shade_smooth()

def shrub(x, y, r=0.6):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=r, location=(x, y, r * 0.5))
    o = bpy.context.active_object
    o.scale = (1, 1, 0.7)
    d = o.modifiers.new("d", "DISPLACE")
    tex = bpy.data.textures.new("t", "CLOUDS")
    tex.noise_scale = 0.25
    d.texture = tex
    d.strength = 0.25
    o.data.materials.append(M["leaf"])
    bpy.ops.object.shade_smooth()

def car(x, y, rot=0.0):
    parts = []
    parts.append(box("body", (0, 0, 0.62), (4.5, 1.82, 0.7), M["car"], 0.15))
    parts.append(box("cabin", (-0.25, 0, 1.18), (2.5, 1.6, 0.55), M["glass"], 0.18))
    for dx in (-1.45, 1.4):
        for dy in (-0.82, 0.82):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.34, depth=0.24, location=(dx, dy, 0.34), rotation=(math.pi / 2, 0, 0))
            t = bpy.context.active_object
            t.data.materials.append(M["tyre"])
            parts.append(t)
    bpy.ops.object.empty_add(location=(x, y, 0))
    e = bpy.context.active_object
    for p in parts:
        p.parent = e
    e.rotation_euler = (0, 0, rot)

# ---------- house types ----------
def house_two_storey(ox, oy, rot=0.0, mirror=False, lights=False):
    """Patrový dům: ground floor 11.5 x 9, upper floor 9 x 8.6 cantilevered, flat roofs. Front faces -y."""
    objs_before = set(bpy.data.objects)
    g = box("gf", (0, 0, 1.55), (11.5, 9.0, 3.1), M["plaster"])
    u = box("uf", (1.1, 0.4, 4.55), (9.0, 8.6, 2.9), M["plaster"])
    # attic edges
    box("attic_g", (0, 0, 3.15), (11.6, 9.1, 0.12), M["plaster_dark"])
    box("attic_u", (1.1, 0.4, 6.05), (9.1, 8.7, 0.14), M["plaster_dark"])
    # dark recessed entry block + wood cladding
    box("entry_dark", (-4.2, -4.52, 1.55), (2.6, 0.06, 3.1), M["plaster_dark"])
    for i in range(14):
        box("slat", (-5.35 + i * 0.17, -4.6, 1.55), (0.07, 0.08, 3.0), M["wood"])
    # door
    box("door", (-3.4, -4.58, 1.15), (1.1, 0.05, 2.3), M["frame"])
    # ground-floor windows front
    window(g, 0.6, -4.5, 1.35, 3.6, 2.5, divide=1, warm=lights)
    window(g, 4.3, -4.5, 1.6, 1.6, 1.4)
    # upper windows front
    window(u, -1.5, -3.9, 4.55, 2.6, 1.6, warm=lights)
    window(u, 2.6, -3.9, 4.4, 1.0, 2.2)
    window(u, 4.7, -3.9, 4.55, 1.6, 1.6)
    # side windows (x+)
    window(g, 5.75, -1.0, 1.4, 2.4, 2.4, axis="x+", divide=1, warm=lights)
    window(u, 5.6, 2.2, 4.55, 2.0, 1.5, axis="x+")
    # side (x-)
    window(g, -5.75, 1.5, 1.4, 1.8, 2.3, axis="x-")
    window(u, -3.4, 1.0, 4.55, 1.5, 1.5, axis="x-")
    # back terrace glass
    box("terrace", (0, 6.0, 0.08), (9.0, 3.0, 0.16), M["wood"])
    window(g, 0, 4.5, 1.45, 6.0, 2.6, axis="y", divide=2) if False else None
    box("glass_back", (0, 4.52, 1.45), (6.0, 0.05, 2.6), M["glass"])
    for dx in (-3.0, -1.0, 1.0, 3.0):
        box("mull", (dx, 4.56, 1.45), (0.07, 0.06, 2.6), M["frame"])
    for dz in (0.15, 2.75):
        box("mull", (0, 4.56, dz), (6.07, 0.06, 0.07), M["frame"])
    box("glass_up", (2.6, 4.72, 4.5), (3.2, 0.05, 1.7), M["glass"])
    box("glass_up2", (-1.8, 4.72, 4.5), (1.4, 0.05, 1.7), M["glass"])
    for dx in (1.0, 4.2, 2.6, -2.5, -1.1):
        box("mull", (dx, 4.76, 4.5), (0.07, 0.06, 1.7), M["frame"])
    box("pergola", (0, 6.6, 3.0), (9.2, 3.6, 0.12), M["plaster_dark"])
    for dx in (-4.5, 4.5):
        box("post", (dx, 8.3, 1.5), (0.12, 0.12, 3.0), M["plaster_dark"])
    # sill line / plinth
    box("plinth", (0, 0, 0.12), (11.62, 9.12, 0.24), M["plaster_dark"])
    _place(objs_before, ox, oy, rot, mirror)

def house_bungalow(ox, oy, rot=0.0, mirror=False, lights=False):
    """Přízemní dům: L shape 14 x 9 + 5 x 4 wing, flat roof with overhang."""
    objs_before = set(bpy.data.objects)
    mw = box("main", (0, 0, 1.6), (14.0, 9.0, 3.2), M["plaster"])
    box("wing", (-4.5, 6.0, 1.6), (5.0, 3.6, 3.2), M["plaster"])
    box("roof", (0.2, -0.2, 3.28), (14.8, 9.8, 0.18), M["plaster_dark"])
    box("roof2", (-4.5, 6.0, 3.28), (5.6, 4.2, 0.18), M["plaster_dark"])
    # wood band at entry
    for i in range(18):
        box("slat", (-6.2 + i * 0.17, -4.6, 1.6), (0.07, 0.08, 3.05), M["wood"])
    box("door", (-4.0, -4.58, 1.15), (1.1, 0.05, 2.3), M["frame"])
    window(mw, 0.5, -4.5, 1.45, 4.2, 2.5, divide=2, warm=lights)
    window(mw, 4.9, -4.5, 1.65, 2.0, 1.5)
    window(mw, 7.0, 0.0, 1.45, 3.0, 2.5, axis="x+", divide=1, warm=lights)
    window(mw, -7.0, 1.0, 1.6, 1.6, 1.6, axis="x-")
    box("plinth", (0, 0, 0.12), (14.12, 9.12, 0.24), M["plaster_dark"])
    box("terrace", (2.5, 6.2, 0.08), (8.0, 3.4, 0.16), M["wood"])
    _place(objs_before, ox, oy, rot, mirror)

def _place(before, ox, oy, rot, mirror):
    new = [o for o in bpy.data.objects if o not in before and o.parent is None]
    bpy.ops.object.empty_add(location=(ox, oy, 0))
    e = bpy.context.active_object
    for o in new:
        o.parent = e
    e.rotation_euler = (0, 0, rot)
    if mirror:
        e.scale = (-1, 1, 1)

def hedge(loc, size):
    o = box("hedge", loc, size, M["leaf"], 0.25)
    d = o.modifiers.new("sd", "SUBSURF"); d.levels = 2; d.render_levels = 2
    o2 = o
    bpy.context.view_layer.objects.active = o
    mod = o.modifiers.new("dp", "DISPLACE")
    tex = bpy.data.textures.new("h", "CLOUDS"); tex.noise_scale = 0.18
    mod.texture = tex; mod.strength = 0.12
    return o

def plot(ox, oy, w=20, d=28, fence=True, rot=0.0, drive_x=-6.5):
    """Lawn plot with paved parking + path. Front edge at oy - d/2 (towards -y)."""
    before = set(bpy.data.objects)
    box("lawn", (0, 0, 0.01), (w, d, 0.02), M["grass"])
    box("park", (drive_x, -d / 2 + 3.6, 0.025), (5.4, 7.2, 0.03), M["paving"])
    box("path", (drive_x + 3.3, -d / 2 + 4.5, 0.025), (1.3, 9.0, 0.03), M["paving"])
    box("gravel", (0, -d / 2 + 9.7, 0.022), (12.2, 0.6, 0.02), M["gravel"])
    if fence:
        for sx in (-w / 2 + 0.4, w / 2 - 0.4):
            hedge((sx, 3.5, 0.6), (0.8, d - 7, 1.2))
        hedge((0, d / 2 - 0.4, 0.8), (w, 0.8, 1.6))
        # low front fence beside parking
    _place(before, ox, oy, rot, False)

# ---------- world ----------
def world(strength=1.0, sun_elev=18, sun_rot=210, az=-35):
    wd = bpy.data.worlds.new("w")
    scene.world = wd
    wd.use_nodes = True
    nt = wd.node_tree
    bg = nt.nodes["Background"]
    sky = nt.nodes.new("ShaderNodeTexSky")
    for t in ("MULTIPLE_SCATTERING", "NISHITA", "SINGLE_SCATTERING", "HOSEK_WILKIE"):
        try:
            sky.sky_type = t
            break
        except Exception:
            pass
    try:
        sky.sun_elevation = math.radians(sun_elev)
        sky.sun_rotation = math.radians(sun_rot)
        sky.altitude = 200
        sky.air_density = 1.2
        sky.dust_density = 1.5
        sky.sun_intensity = 0.4
    except Exception as ex:
        print("sky props", ex)
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength
    # explicit sun for crisp shadows
    bpy.ops.object.light_add(type='SUN', rotation=(math.radians(90 - sun_elev), 0, math.radians(az)))
    s = bpy.context.active_object
    s.data.energy = 3.2
    s.data.angle = math.radians(1.2)
    s.data.color = (1.0, 0.9, 0.78)

def ground(material="grass", size=3000):
    box("ground", (0, 0, -0.02), (size, size, 0.02), M[material])

def camera(loc, target, lens=35, shift_y=0.0):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.active_object
    d = Vector(target) - Vector(loc)
    c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    c.data.lens = lens
    c.data.shift_y = shift_y
    scene.camera = c

def rng_trees(n, xr, yr, avoid):
    k = 0
    while k < n:
        x, y = random.uniform(*xr), random.uniform(*yr)
        if any(abs(x - ax) < aw and abs(y - ay) < ah for ax, ay, aw, ah in avoid):
            continue
        tree(x, y, random.uniform(5, 9), random.uniform(1.6, 2.8), random.randint(0, 1))
        k += 1

# ---------- shots ----------
if shot == "hero":
    world(1.0, 14, 235)
    ground("grass")
    box("road", (0, -24, 0.0), (300, 7, 0.02), M["asphalt"])
    box("pavement", (0, -19.8, 0.01), (300, 1.8, 0.03), M["paving"])
    plot(0, 0)
    house_two_storey(0, 1.5)
    car(-6.5, -10.6, math.pi / 2)
    plot(21, 0, fence=True); house_bungalow(21, 1.5, mirror=True)
    plot(-21, 0); house_two_storey(-21, 1.5, mirror=True)
    for (x, y) in [(-9.2, 9), (-30, 8), (9.5, 10)]:
        tree(x, y, 6.5, 2.0, 0)
    for x in (-3.4, -2.2, 4.0, 5.4, 9.0):
        shrub(x, -7.6, 0.45)
    rng_trees(16, (-90, 90), (25, 70), [])
    camera((15.0, -26.0, 1.7), (0.6, 0, 3.0), 26, 0.13)

elif shot == "street":
    world(1.05, 22, 200)
    ground("grass")
    box("road", (0, -18, 0.0), (300, 6.5, 0.02), M["asphalt"])
    box("pavement", (0, -14, 0.01), (300, 1.6, 0.03), M["paving"])
    xs = [-63, -42, -21, 0, 21, 42, 63]
    for i, x in enumerate(xs):
        plot(x, 0)
        if i % 3 == 1:
            house_bungalow(x, 1.5, mirror=(i % 2 == 0))
        else:
            house_two_storey(x, 1.5, mirror=(i % 2 == 0))
        tree(x + 8, -9.5, 5.5, 1.7, i % 2)
    for i in range(4):
        car(xs[i * 2] - 6.5, -10.6, math.pi / 2)
    rng_trees(30, (-120, 120), (22, 80), [])
    camera((-48, -44, 16), (-6, 0, 2), 32)

elif shot == "bungalow":
    world(1.0, 26, 160)
    ground("grass")
    box("road", (0, -24, 0.0), (300, 7, 0.02), M["asphalt"])
    plot(0, 0, w=22)
    house_bungalow(0, 1.5)
    car(-6.5, -10.6, math.pi / 2)
    tree(9, -8, 6, 2.1, 1)
    tree(-11, 10, 7, 2.4, 0)
    for x in (-1.5, 0.5, 2.5, 6.5):
        shrub(x, -7.4, 0.5)
    rng_trees(14, (-90, 90), (25, 70), [])
    camera((-19, -30, 3.0), (0.5, 0, 1.8), 34, 0.1)

elif shot == "garden":
    world(1.0, 16, 30, az=160)
    ground("grass")
    plot(0, 0)
    house_two_storey(0, 1.5, lights=False)
    tree(-7.6, 11.0, 6.5, 2.1, 1)
    for x in (6.5, 8.0):
        shrub(x, 12.4, 0.6)
    rng_trees(12, (-90, 90), (-80, -30), [])
    camera((-7.0, 12.4, 1.65), (1.5, 5.0, 2.4), 24)

elif shot == "entry":
    world(1.0, 20, 0, az=-50)
    ground("grass")
    box("road", (0, -24, 0.0), (300, 7, 0.02), M["asphalt"])
    plot(0, 0)
    house_two_storey(0, 1.5)
    for x in (-1.5, -0.3, 3.8, 5.0):
        shrub(x, -7.6, 0.45)
    rng_trees(10, (-90, 90), (25, 70), [])
    camera((-13.5, -17.5, 1.6), (-2.0, -3.0, 2.6), 30)

elif shot == "bungalow_back":
    world(1.0, 22, 0, az=150)
    ground("grass")
    plot(0, 0, w=22)
    house_bungalow(0, 1.5)
    tree(8.5, 11.5, 6.5, 2.2, 0)
    for x in (-8, -6.6):
        shrub(x, 12.6, 0.6)
    rng_trees(10, (-90, 90), (-80, -30), [])
    camera((9.5, 13.0, 1.7), (-0.5, 5.5, 1.7), 26)

elif shot == "aerial":
    world(1.1, 35, 200)
    ground("grass")
    box("road", (0, -18, 0.0), (300, 6.5, 0.02), M["asphalt"])
    xs = [-42, -21, 0, 21, 42]
    for i, x in enumerate(xs):
        plot(x, 0)
        (house_bungalow if i % 2 else house_two_storey)(x, 1.5, mirror=(i % 2 == 0))
    rng_trees(24, (-100, 100), (22, 70), [])
    camera((30, -60, 48), (0, 0, 0), 40)

# ---------- render ----------
r = scene.render
r.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = samples
scene.cycles.use_denoising = True
try:
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception:
    pass
scene.cycles.max_bounces = 4
scene.cycles.diffuse_bounces = 2
scene.cycles.glossy_bounces = 2
scene.cycles.transmission_bounces = 2
r.resolution_x = W
r.resolution_y = H
r.resolution_percentage = 100
r.image_settings.file_format = 'PNG'
try:
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
except Exception:
    try:
        scene.view_settings.look = 'Medium High Contrast'
    except Exception:
        pass
scene.view_settings.exposure = EXPO
r.filepath = out
bpy.ops.render.render(write_still=True)
print("DONE", out)
