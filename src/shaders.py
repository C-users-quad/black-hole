vert_shader=(
    """
    #version 330

    in vec3 in_vert;
    in vec3 in_color;

    uniform mat4 mvp;

    out vec3 v_color;

    void main() {
        gl_Position = mvp * vec4(in_vert, 1.0);
        v_color = in_color;
    }
    """
)

frag_shader=(
    """
    #version 330

    in vec3 v_color;

    out vec4 f_color;

    void main() {
        f_color = vec4(v_color, 1.0);
    }
    """
)

compute_shader = (
    """
    #version 430

    #define EPSILON 1e-5
    #define UP vec3(0.0, 1.0, 0.0)
    #define FOV 45.0
    #define h 1.0

    vec3 cartesianToSphericalPos(vec3 pos) {
        float x = pos[0];
        float y = pos[1];
        float z = pos[2];

        float r = length(pos);
        float theta = (r >= 0) ? acos(clamp(z / r, -1, 1)) : 0.0;
        float phi = atan(y, x);

        return vec3(r, theta, phi);
    }

    vec3 cartesianToSphericalVel(vec3 vel, vec3 pos) {
        // initialize values needed for velocity calculation
        vec3 sPos = cartesianToSphericalPos(pos);
        float x = pos.x; float y = pos.y; float z = pos.z;
        float r = sPos.x; float theta = sPos.y; float phi = sPos.z;
        float vx = vel.x; float vy = vel.y; float vz = vel.z;
        float sinTheta = sin(theta);

        // declare velocity values
        float dr = (x*vx + y*vy + z*vz) / r; float dtheta; float dphi;

        if (sinTheta < EPSILON) {
            dtheta = 0.0;
            dphi = 0.0;
        } else {
            dtheta = (dr*cos(theta) - vz) / (r*sin(theta));
            dphi = (vy*cos(phi) - vx*sin(phi)) / (r*sin(theta));
        }

        return vec3(dr, dtheta, dphi);
    }

    float computeConservedEnergy(
        float bhMass, float r, float dr, float dphi
    ) {
        float f = 1 - 2*bhMass / r;
        return f * sqrt((dr*dr/f + r*r*dphi*dphi/f) / f);
    }

    float computeDt(float bhMass, float r, float conservedEnergy) {
        return conservedEnergy / (1 - 2 * bhMass / r);
    }

    struct Ray {
        vec3 pos;
        float r; float theta; float phi;
        float dr; float dtheta; float dphi;
        float E; float state[6];
    };

    Ray generateRay(
        int windowWidth, int windowHeight,
        vec3 camPos, float bhMass, int i, int j
    ) {
        // calculate initial cartesian velocity
        float aspect = float(windowWidth) / windowHeight;
        vec3 forward = normalize(-camPos);
        vec3 right = normalize(cross(forward, UP));
        vec3 up = cross(right, forward);
        float tanHalfFov = tan(radians(FOV) / 2.0)

        float x = (
            (2.0*(i + 0.5) / windowWidth - 1) *
            (tanHalfFov * aspect)
        );
        float y = (
            (1 - 2.0*(j + 0.5) / windowHeight) *
            tanHalfFov
        );

        vec3 dirRay = normalize(x*right + y*up + forward);

        // calculate initial spherical position
        vec3 sPos = cartesianToSphericalPos(camPos);
        float r=sPos.x; float theta=sPos.y; float phi=sPos.z;

        // calculate initial spherical velocity
        vec3 sVel = cartesianToSphericalVel(dirRay, camPos);
        float dr=sVel.x; float dtheta=sVel.y; float dphi=sVel.z;

        // caluclate conserved energy
        float E = computeConservedEnergy(bhMass, r, dr, dphi);

        // create state vector
        float state[6] = float[6](r, theta, phi, dr, dtheta, dphi);

        // return generated ray
        Ray ray;
        ray.pos = camPos;
        ray.r = r; ray.theta = theta; ray.phi = phi;
        ray.dr = dr; ray.dtheta = dtheta; ray.dphi = dphi;
        ray.E = E;
        for(int i=0; i < 6; i++) ray.state[i] = state[i];
        return ray;
    }

    void geodesic(in float state[6], float rS, float E, out float result[6]) {
        // modify result[6] in place here (kX)
    }

    void rk4Step(in float state[6], float E, float rS, out float result[6]) {
        float k1[6], k2[6], k3[6], k4[6], temp[6];

        geodesic(state, rS, E, k1);
        for (int i=0; i < 6; i++) temp[i]=state[i] + (h/2.0) * k1[i];
        geodesic(temp, rS, E, k2);
        for (int i=0; i < 6; i++) temp[i]=state[i] + (h/2.0) * k2[i];
        geodesic(temp, rS, E, k3);
        for (int i=0; i < 6; i++) temp[i]=state[i] + h * k3[i];
        geodesic(temp, rS, E, k4);

        for (int i=0; i < 6; i++) {
            result[i] = (
                state[i] + (h/6.0)*(k1[i] + 2*k2[i] + 2*k3[i] + k4[i])
            );
        }
    }

    void main() {
        vec3 pos = vec3(camPos)

        Ray ray = Ray()
    }
    """
)
