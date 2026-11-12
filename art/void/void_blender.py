# 보이드 3D 모델 + 포즈 렌더 (Blender 4.5, 화면 없이 실행: blender -b -P void_blender.py -- <출력폴더>)
# 프레임마다 두 장을 뽑는다: id(재질 구분용 단색) / lit(흰색 조명만). 색 입히기는 void_pixelate.py가 한다.
import bpy, math, sys, json
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
OUT = sys.argv[sys.argv.index("--") + 1]
RES = 48
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

IDS = {"iron": (1, 0, 0), "back": (0.5, 0, 0), "rust": (1, 1, 0), "gold": (1, 0.5, 0), "cape": (0, 1, 0), "flame": (0, 0, 1),
       "core": (0, 1, 1), "eye": (1, 1, 1), "dark": (1, 0, 1)}
MATS = {}
for k, c in IDS.items():
    m = bpy.data.materials.new(k); m.diffuse_color = (*c, 1); MATS[k] = m

def finish(o, mat, parent, smooth=True):
    o.data.materials.append(MATS[mat])
    if smooth:
        for p in o.data.polygons: p.use_smooth = True
    if parent: o.parent = parent
    return o
def sphere(name, mat, loc, scale, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=loc); o = bpy.context.object; o.name = name; o.scale = scale
    return finish(o, mat, parent)
def cyl(name, mat, loc, r, h, parent=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=r, depth=h, location=loc, rotation=rot); o = bpy.context.object; o.name = name
    return finish(o, mat, parent)
def torus(name, mat, loc, R, r, parent=None, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=24, minor_segments=8, location=loc); o = bpy.context.object; o.name = name; o.scale = scale
    return finish(o, mat, parent)
def cube(name, mat, loc, scale, parent=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot); o = bpy.context.object; o.name = name; o.scale = scale
    return finish(o, mat, parent, smooth=False)
def cone(name, mat, loc, r, h, parent=None):
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=r, depth=h, location=loc); o = bpy.context.object; o.name = name
    return finish(o, mat, parent)
def empty(name, loc, parent=None):
    o = bpy.data.objects.new(name, None); o.location = loc; sc.collection.objects.link(o)
    if parent: o.parent = parent
    return o

# ---- 모델: 앞은 +X, 위는 +Z. 카메라 쪽(가까운 쪽)은 -Y ----
root = empty("root", (0, 0, 0))
body = empty("body", (0, 0, 0.62), root)                      # 허리 기준으로 숙이고 들썩인다
sphere("torso", "iron", (0, 0, 0.42), (0.68, 0.62, 0.5), body)
sphere("chestplate", "iron", (0.2, 0, 0.5), (0.45, 0.44, 0.36), body)
torus("belt", "back", (0, 0, 0.08), 0.5, 0.07, body, (1.05, 1, 1))
torus("rustrim", "rust", (0, 0, 0.0), 0.5, 0.045, body, (1.05, 1, 1))
sphere("buckle", "gold", (0.52, 0, 0.08), (0.07, 0.09, 0.09), body)
cube("crack", "dark", (0.6, -0.12, 0.5), (0.05, 0.035, 0.3), body, (0.3, 0, 0))
for i, a in enumerate([-70, -25, 25, 70, 130, 180, 230]):    # 치마 갑옷
    r = math.radians(a); cube(f"tasset{i}", "iron" if i < 4 else "back", (math.cos(r) * 0.45, math.sin(r) * 0.42, -0.1), (0.2, 0.26, 0.22), body, (0, 0, r))
for sy, mat in ((-1, "iron"), (1, "back")):                  # 어깨
    sphere(f"pauldron{sy}", mat, (0, sy * 0.6, 0.72), (0.3, 0.27, 0.24), body)
    sphere(f"rivet{sy}", "gold", (0.12, sy * 0.78, 0.74), (0.05, 0.05, 0.05), body)
    torus(f"prim{sy}", "rust", (0, sy * 0.6, 0.6), 0.25, 0.035, body, (1.1, 1, 1))
torus("collar", "rust", (0, 0, 0.9), 0.27, 0.075, body)
cyl("hole", "dark", (0, 0, 0.91), 0.24, 0.05, body)
# 유령불 머리
head = empty("head", (0, 0, 0.95), body)
sphere("flame", "flame", (0, 0, 0.26), (0.3, 0.3, 0.3), head)
sphere("flamecore", "core", (0.06, -0.06, 0.2), (0.2, 0.2, 0.17), head)
licks = [cone(f"lick{i}", "flame", (x, 0, z), r, h, head) for i, (x, z, r, h) in enumerate([(-0.02, 0.62, 0.2, 0.5), (-0.2, 0.5, 0.12, 0.34), (0.14, 0.5, 0.1, 0.26)])]
sphere("spark", "flame", (-0.3, 0, 0.95), (0.06, 0.06, 0.06), head)
for ey in (-0.19, 0.05):
    sphere(f"eye{ey}", "dark", (0.285, ey, 0.27), (0.05, 0.07, 0.11), head)
# 팔: 어깨 축에서 돌린다
arms = {}; parts = {}
for sy, mat in ((-1, "iron"), (1, "back")):
    piv = empty(f"arm{sy}", (0.02, sy * 0.76, 0.66), body)
    up = cyl(f"upper{sy}", mat, (0, 0, -0.2), 0.13, 0.4, piv)
    fi = sphere(f"fist{sy}", mat, (0.06, 0, -0.56), (0.25, 0.23, 0.23), piv)
    cu = torus(f"cuff{sy}", "rust", (0.02, 0, -0.33), 0.17, 0.04, piv)
    arms[sy] = piv; parts[sy] = (up, fi, cu)
# 다리: 골반 축에서 돌린다
legs = {}
for sy, mat in ((-1, "iron"), (1, "back")):
    piv = empty(f"leg{sy}", (0, sy * 0.3, 0.5), root)
    cyl(f"thigh{sy}", mat, (0, 0, -0.18), 0.17, 0.3, piv)
    sphere(f"boot{sy}", mat, (0.08, 0, -0.37), (0.33, 0.24, 0.17), piv)
    cube(f"sole{sy}", "rust", (0.07, 0, -0.48), (0.5, 0.36, 0.06), piv)
    legs[sy] = piv
# 망토: 격자 면. 프레임마다 꼭짓점을 물결치게 옮긴다
NX, NZ = 7, 8
mesh = bpy.data.meshes.new("cape"); verts = [(0, 0, 0)] * (NX * NZ)
faces = [(j * NX + i, j * NX + i + 1, (j + 1) * NX + i + 1, (j + 1) * NX + i) for j in range(NZ - 1) for i in range(NX - 1)]
mesh.from_pydata(verts, [], faces); cape = bpy.data.objects.new("cape", mesh); sc.collection.objects.link(cape); cape.parent = body
mesh.materials.append(MATS["cape"]); sol = cape.modifiers.new("s", "SOLIDIFY"); sol.thickness = 0.05
def set_cape(t, blow):
    for j in range(NZ):
        v = j / (NZ - 1)
        for i in range(NX):
            u = i / (NX - 1) - 0.5
            ragged = 0.12 * ((i * 7) % 3) / 2 if j == NZ - 1 else 0
            x = -0.42 - v * (0.25 + blow * 0.9) - 0.06 * math.sin(t * 6.283 + v * 4 + i) * v - 0.25 * (1 - 4 * u * u) * 0.3
            z = 0.8 - v * (1.0 - blow * 0.55) + ragged
            mesh.vertices[j * NX + i].co = (x, u * 1.25 * (1 + v * 0.25), z)
    mesh.update()

# ---- 카메라와 렌더 설정 ----
cam_d = bpy.data.cameras.new("cam"); cam_d.type = "ORTHO"; cam_d.ortho_scale = 3.3
cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
yaw, pitch, d = math.radians(26), math.radians(12), 10
target = Vector((0.15, 0, 1.05))
cam.location = target + Vector((math.sin(yaw) * math.cos(pitch) * d, -math.cos(yaw) * math.cos(pitch) * d, math.sin(pitch) * d))
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.engine = "BLENDER_WORKBENCH"; sc.render.resolution_x = sc.render.resolution_y = RES
sc.render.film_transparent = True; sc.render.image_settings.color_mode = "RGBA"; sc.render.filter_size = 0.01
sc.display.render_aa = "OFF"                                   # 안티에일리어싱 끔: 픽셀 경계가 깔끔하게
sc.view_settings.view_transform = "Standard"
sh = sc.display.shading
sc.display.light_direction = (-0.45, 0.4, 0.8); sc.display.shadow_focus = 0.9

def render(path, lit):
    sh.light = "STUDIO" if lit else "FLAT"; sh.color_type = "SINGLE" if lit else "MATERIAL"; sh.single_color = (1, 1, 1)
    sh.show_shadows = lit; sh.shadow_intensity = 0.55; sh.show_cavity = lit; sh.cavity_type = "BOTH"; sh.show_specular_highlight = False
    sc.render.filepath = path; bpy.ops.render.render(write_still=True)

# ---- 포즈: 동작 이름과 진행도(0..1)로 각 부위를 놓는다 ----
def pose(anim, u):
    w = u * 6.283
    bob = lean = 0.0; la = [0.0, 0.0]; aa = [0.15, -0.15]; ext = 0.0; blow = 0.0; fl = u; bx = 0.0
    if anim == "idle":
        bob = 0.03 * math.sin(w); aa = [0.12 + 0.05 * math.sin(w), -0.12 - 0.05 * math.sin(w)]
    elif anim == "run":
        bob = 0.07 * abs(math.sin(w)); lean = 0.3; blow = 0.8
        la = [0.85 * math.sin(w), -0.85 * math.sin(w)]; aa = [-1.0 * math.sin(w), 1.0 * math.sin(w)]
    elif anim == "punch":                                      # 당겼다가 뻗고 돌아온다
        # (숙임, 앞팔 각도, 팔 뻗는 길이, 가까운 다리, 먼 다리, 몸 앞으로, 들썩임)
        keys = [(-0.2, 0.8, 0.0, 0.1, -0.1, -0.05, 0.0), (0.36, -1.5, 0.22, -0.45, 0.5, 0.3, -0.05), (0.32, -1.45, 0.17, -0.4, 0.45, 0.26, -0.05), (0.1, -0.5, 0.0, -0.15, 0.2, 0.04, 0.0)]
        lean, a0, ext, l0, l1, bx, bob = keys[min(3, int(u * 4))]; aa = [a0, 0.6 if a0 < 0 else -0.4]; la = [l0, l1]; blow = 0.35 if a0 < -1 else 0.1
    elif anim == "jump":                                       # 0: 오르는 중, 1: 내려오는 중
        up = u < 0.5; la = [0.55, -0.2] if up else [-0.15, 0.35]; aa = [-0.5, 0.6] if up else [-1.9, -1.6]; lean = 0.1; blow = 0.25 if up else 0.75
    elif anim == "dash":
        lean = 0.6; la = [0.75, -0.75]; aa = [1.0, 0.8]; blow = 1.0; bob = -0.04
    elif anim == "slam":                                       # 0: 두 팔을 들어 올림, 1: 내려찍고 웅크림
        if u < 0.5: lean = -0.12; aa = [-2.5, -2.3]; bob = 0.04; blow = 0.3
        else: lean = 0.4; aa = [-0.8, -0.7]; bob = -0.13; la = [0.3, -0.3]; blow = 0.6
    body.location.z = 0.62 + bob; body.location.x = bx; body.rotation_euler = (0, lean, 0)
    for i, sy in enumerate((-1, 1)):
        legs[sy].rotation_euler = (0, -la[i], 0); arms[sy].rotation_euler = (0, aa[i], 0)
        legs[sy].location.z = 0.5 + (0.1 * max(0, math.sin(w + (0 if i == 0 else math.pi))) if anim == "run" else 0)
    up, fi, cu = parts[-1]                                      # 팔만 길어지고 주먹 크기는 그대로
    up.location.z = -(0.2 + ext / 2); up.scale.z = (0.4 + ext) / 0.4; fi.location.z = -0.56 - ext; cu.location.z = -0.33 - ext
    for i, l in enumerate(licks):                               # 불꽃 혀가 번갈아 길어지고 흔들린다
        s = 1 + 0.35 * math.sin(fl * 6.283 + i * 2.1); l.scale = (1, 1, s); l.rotation_euler = (0, -0.25 - blow * 0.7 + 0.2 * math.sin(fl * 6.283 + i), 0)
    head.rotation_euler = (0, -lean * 0.6, 0)
    set_cape(u, blow)

ANIMS = [("idle", 4), ("run", 6), ("punch", 4), ("jump", 2), ("dash", 1), ("slam", 2)]
def px(v):
    c = world_to_camera_view(sc, cam, v); return [round(c.x * RES, 1), round((1 - c.y) * RES, 1)]
bpy.context.view_layer.update()
anchors = {"size": RES, "feet": px(Vector((0, 0, 0))), "frames": {}}
for name, n in ANIMS:
    anchors["frames"][name] = []
    for f in range(n):
        pose(name, f / n); bpy.context.view_layer.update()
        anchors["frames"][name].append(px(head.matrix_world.translation) + px(parts[-1][1].matrix_world.translation))   # 목깃, 앞주먹
        for var, hide in (("full", False), ("body", True)):      # full: 유령불 머리 / body: 머리 없음(투구를 얹는 용)
            for o in head.children: o.hide_render = hide
            render(f"{OUT}/{name}_{f}_{var}_id.png", False); render(f"{OUT}/{name}_{f}_{var}_lit.png", True)
json.dump(anchors, open(f"{OUT}/anchors.json", "w"))
print("DONE")
