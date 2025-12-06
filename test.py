#!/usr/bin/env python3
"""
Run the geodesic.compute shader (the corrected shader I provided) as a compute shader,
read back the output image and save to output.png.

This script will:
 - write geodesic.comp to disk if not present (contents embedded below)
 - create a standalone moderngl context
 - create an rgba32f texture and bind it to image unit 0
 - set uniforms used by the shader (you can adjust them)
 - dispatch compute groups sized to the window resolution / local_size (16)
 - read back floats, convert to 8-bit RGB and save with Pillow
"""

import os
import math
import numpy as np
from PIL import Image
import moderngl

# -------------------------------------------------------
# If you already have geodesic.comp, the script will use it.
# If not, it will save the embedded shader string below to geodesic.comp.
# -------------------------------------------------------

SHADER_PATH = "geodesic.comp"

EMBEDDED_SHADER = r"""
#version 430

layout(local_size_x = 16, local_size_y = 16) in;
layout(rgba32f, binding = 0) uniform image2D img;

uniform float diskInnerR;
uniform float diskOuterR;
uniform vec3 camPos;
uniform int windowWidth;
uniform int windowHeight;
uniform float bhMass; // M
uniform float rS;     // Schwarzschild radius = 2M

#define EPSILON 1e-6
#define UP vec3(0.0, 1.0, 0.0)
#define NUM_STEPS 5000
#define FOV 45.0
#define H 0.05
#define ESCAPE_R 1000.0
#define c 1.0

vec3 cartesianToSphericalPos(vec3 pos) {
    float x = pos.x;
    float y = pos.y;
    float z = pos.z;
    float r = length(pos);
    float theta = 0.0;
    float phi = 0.0;
    if (r > 0.0) {
        theta = acos(clamp(y / r, -1.0, 1.0));
        phi = atan(z, x);
    }
    return vec3(r, theta, phi);
}

vec3 sphericalToCartesianPos(vec3 s) {
    float r = s.x;
    float theta = s.y;
    float phi = s.z;
    float sinTheta = sin(theta);
    return vec3(
        r * sinTheta * cos(phi),
        r * cos(theta),
        r * sinTheta * sin(phi)
    );
}

vec3 cartesianToSphericalVel(vec3 vel, vec3 pos) {
    float x = pos.x;
    float y = pos.y;
    float z = pos.z;
    float vx = vel.x;
    float vy = vel.y;
    float vz = vel.z;

    float r = length(pos);
    if (r < EPSILON) return vec3(0.0);

    float theta = acos(clamp(y / r, -1.0, 1.0));
    float sinTheta = sin(theta);
    float dr = (x * vx + y * vy + z * vz) / r;

    float dtheta;
    if (abs(sinTheta) < EPSILON) {
        dtheta = 0.0;
    } else {
        float cosTheta = y / r;
        dtheta = (dr * cosTheta - vy) / (r * sinTheta);
    }

    float dphi;
    float sinThetaSq = sinTheta * sinTheta;
    if (sinThetaSq < EPSILON) {
        dphi = 0.0;
    } else {
        dphi = (x * vz - z * vx) / (r * r * sinThetaSq);
    }

    return vec3(dr, dtheta, dphi);
}

float computeConservedEnergy(float bhMass, float r, float dr, float dtheta, float dphi, float theta) {
    float f = 1.0 - (2.0 * bhMass) / r;
    float sinTheta = sin(theta);
    float angSquared = dtheta * dtheta + (sinTheta * sinTheta) * dphi * dphi;
    float inner = dr * dr + f * r * r * angSquared;
    inner = max(inner, 0.0);
    return sqrt(inner);
}

float computeTprime(float bhMass, float r, float conservedEnergy) {
    float f = 1.0 - (2.0 * bhMass) / r;
    if (abs(f) < EPSILON) f = EPSILON * sign(f);
    return conservedEnergy / f;
}

struct Ray {
    vec3 pos;
    float r; float theta; float phi;
    float dr; float dtheta; float dphi;
    float E;
    float state[6];
};

Ray generateRay(
    int windowWidth, int windowHeight,
    vec3 camPos, float bhMass, int pixelX, int pixelY
) {
    float aspect = float(windowWidth) / float(windowHeight);
    vec2 ndc = (vec2(float(pixelX) + 0.5, float(pixelY) + 0.5) / vec2(float(windowWidth), float(windowHeight))) * 2.0 - 1.0;
    float fovScale = tan(radians(FOV * 0.5));
    vec2 uv = vec2(ndc.x * aspect * fovScale, -ndc.y * fovScale);

    vec3 forward = normalize(-camPos);
    vec3 right = normalize(cross(forward, UP));
    vec3 up = cross(right, forward);

    vec3 dirRay = normalize(uv.x * right + uv.y * up + forward);

    vec3 sPos = cartesianToSphericalPos(camPos);
    float r = sPos.x;
    float theta = sPos.y;
    float phi = sPos.z;

    vec3 sVel = cartesianToSphericalVel(dirRay, camPos);
    float dr = sVel.x;
    float dtheta = sVel.y;
    float dphi = sVel.z;

    float E = computeConservedEnergy(bhMass, r, dr, dtheta, dphi, theta);

    float state[6];
    state[0] = r;
    state[1] = theta;
    state[2] = phi;
    state[3] = dr;
    state[4] = dtheta;
    state[5] = dphi;

    Ray ray;
    ray.pos = camPos;
    ray.r = r; ray.theta = theta; ray.phi = phi;
    ray.dr = dr; ray.dtheta = dtheta; ray.dphi = dphi;
    ray.E = E;
    for (int i = 0; i < 6; ++i) ray.state[i] = state[i];
    return ray;
}

void updateRayAttribs(inout Ray ray) {
    ray.r      = ray.state[0];
    ray.theta  = ray.state[1];
    ray.phi    = ray.state[2];
    ray.dr     = ray.state[3];
    ray.dtheta = ray.state[4];
    ray.dphi   = ray.state[5];
    ray.pos    = sphericalToCartesianPos(vec3(ray.r, ray.theta, ray.phi));
}

void geodesic(in float state[6], float rS, float bhMass, float E, out float result[6]) {
    float r = state[0];
    float theta = state[1];
    float phi = state[2];
    float dr = state[3];
    float dtheta = state[4];
    float dphi = state[5];

    result[0] = dr;
    result[1] = dtheta;
    result[2] = dphi;

    float M = bhMass;
    float f = 1.0 - (2.0 * M) / r;
    float r_minus_rS = max(r - rS, EPSILON);

    float tprime = computeTprime(M, r, E);

    float gamma_r_tt = (M * (r - rS)) / (r * r * r);
    float gamma_r_rr = - M / (r * (r - rS));
    float gamma_r_thth = - (r - rS);
    float gamma_r_phph = - (r - rS) * (sin(theta) * sin(theta));

    float rdd = - gamma_r_tt * (tprime * tprime)
                - gamma_r_rr * (dr * dr)
                - gamma_r_thth * (dtheta * dtheta)
                - gamma_r_phph * (dphi * dphi);

    float thdd = - 2.0 * (dr / r) * dtheta + (sin(theta) * cos(theta)) * (dphi * dphi);

    float cotTheta = 0.0;
    if (abs(sin(theta)) > EPSILON) cotTheta = cos(theta) / sin(theta);
    float phdd = - 2.0 * (dr / r) * dphi - 2.0 * cotTheta * dtheta * dphi;

    result[3] = rdd;
    result[4] = thdd;
    result[5] = phdd;
}

void rk4Step(inout float state[6], float rS, float bhMass, float E) {
    float k1[6];
    float k2[6];
    float k3[6];
    float k4[6];
    float temp[6];

    geodesic(state, rS, bhMass, E, k1);
    for (int i = 0; i < 6; ++i) temp[i] = state[i] + 0.5 * H * k1[i];
    geodesic(temp, rS, bhMass, E, k2);
    for (int i = 0; i < 6; ++i) temp[i] = state[i] + 0.5 * H * k2[i];
    geodesic(temp, rS, bhMass, E, k3);
    for (int i = 0; i < 6; ++i) temp[i] = state[i] + H * k3[i];
    geodesic(temp, rS, bhMass, E, k4);

    for (int i = 0; i < 6; ++i) {
        state[i] += (H / 6.0) * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]);
    }
}

bool crossesEquatorialPlane(vec3 currentPos, vec3 lastPos) {
    bool crossed = (lastPos.y * currentPos.y < 0.0);
    float cylR = length(vec2(currentPos.x, currentPos.z));
    return crossed && (cylR >= diskInnerR && cylR <= diskOuterR);
}

void main() {
    ivec2 pixel = ivec2(gl_GlobalInvocationID.xy);
    if (pixel.x >= windowWidth || pixel.y >= windowHeight) return;

    Ray ray = generateRay(windowWidth, windowHeight, camPos, bhMass, pixel.x, pixel.y);

    bool hitDisk = false;
    bool hitBH = false;
    vec3 color = vec3(0.0);
    vec3 lastPos = ray.pos;

    for (int i = 0; i < NUM_STEPS; ++i) {
        rk4Step(ray.state, rS, bhMass, ray.E);
        updateRayAttribs(ray);

        if (ray.r <= rS) {
            hitBH = true;
            break;
        }

        if (crossesEquatorialPlane(ray.pos, lastPos)) {
            hitDisk = true;
            break;
        }

        if (ray.r >= ESCAPE_R) {
            break;
        }

        lastPos = ray.pos;
    }

    if (hitDisk) {
        color = vec3(0.87, 0.11, 0.11);
    } else if (hitBH) {
        color = vec3(0.3, 0.11, 0.89);
    } else {
        color = vec3(0.0);
    }

    imageStore(img, pixel, vec4(color, 1.0));
}
"""

# Write shader file if missing
if not os.path.exists(SHADER_PATH):
    print(f"Writing shader to {SHADER_PATH} ...")
    with open(SHADER_PATH, "w") as f:
        f.write(EMBEDDED_SHADER)
else:
    print(f"Using existing shader file: {SHADER_PATH}")

# ----------------------------
# User-tweakable rendering params
# ----------------------------
WIDTH = 800
HEIGHT = 600
diskInnerR = 6.0
diskOuterR = 20.0
# Place camera at (0, y, z) or anywhere outside BH; shader assumes camera looks to origin
camPos = (0.0, 5.0, 40.0)
# bhMass (M) and rS (2M)
bhMass = 1.0
rS = 2.0 * bhMass

# ----------------------------
# Create moderngl context
# ----------------------------
ctx = moderngl.create_standalone_context(require=430)
print("Created standalone moderngl context")

# Read compute shader source
with open(SHADER_PATH, "r") as f:
    src = f.read()

prog = ctx.compute_shader(src)
print("Compiled compute shader")

# Create a float texture (RGBA32F)
tex = ctx.texture((WIDTH, HEIGHT), components=4, dtype='f4')
# Important: set filtering/wrap not needed but safe
tex.repeat_x = False
tex.repeat_y = False

# Bind texture to image unit 0 for write (as in shader: binding = 0)
tex.bind_to_image(0, read=False, write=True)

# Set uniforms
# The shader expects camPos vec3, windowWidth, windowHeight, diskInnerR, diskOuterR, bhMass, rS
prog['windowWidth'].value = int(WIDTH)
prog['windowHeight'].value = int(HEIGHT)
prog['diskInnerR'].value = float(diskInnerR)
prog['diskOuterR'].value = float(diskOuterR)
prog['camPos'].value = tuple(map(float, camPos))
prog['bhMass'].value = float(bhMass)
prog['rS'].value = float(rS)

# Dispatch compute shader: groups = ceil(dim / local_size)
local_size = 16
groups_x = (WIDTH + local_size - 1) // local_size
groups_y = (HEIGHT + local_size - 1) // local_size

print(f"Dispatching compute shader with groups {groups_x} x {groups_y}")
prog.run(groups_x, groups_y, 1)

# Read back the float32 data
# moderngl texture.read returns bytes in row-major order. For f4 dtype we can interpret as float32.
data = tex.read()  # bytes
arr = np.frombuffer(data, dtype=np.float32).copy()
# moderngl textures are read as rows from bottom to top by default; we'll flip vertically after reshape
try:
    arr = arr.reshape((HEIGHT, WIDTH, 4))
except Exception as e:
    raise RuntimeError("Failed to reshape texture readback: " + str(e))

# Clamp and convert float color [0..1] to 0..255
arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
rgb = np.clip(arr[:, :, :3], 0.0, 1.0)
rgb_u8 = (rgb * 255.0).astype(np.uint8)

# Flip vertically so image origin is top-left for viewing
rgb_u8 = np.flipud(rgb_u8)

img = Image.fromarray(rgb_u8, mode='RGB')
out_path = "output.png"
img.save(out_path)
print(f"Saved {out_path}")
