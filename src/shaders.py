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

    #define UP vec3(0.0, 1.0, 0.0)
    #define EPSILON 1e-5

    vec3 cartesianToSphericalPos(vec3 pos) {
        // unpack pos
        float x = pos[0];
        float y = pos[1];
        float z = pos[2];

        // calculate spherical position
        float r = length(pos);
        float theta = (r >= 0) ? acos(clamp(z / r, -1.0, 1.0)) : 0.0;
        float phi = atan(y, x);

        return vec3(r, theta, phi);
    }

    vec3 cartesianToSphericalVel(vec3 vel, vec3 pos) {
        // unpack input into variables and calculate spherical pos.
        float x = pos.x; float y = pos.y; float z = pos.z;
        float vx = vel.x; float vy = vel.y; float vz = vel.z;

        vec3 sPos = cartesianToSphericalPos(pos);
        float r = sPos.x; float theta = sPos.y; float phi = sPos.z;

        float dr; float dtheta; float dphi;
        float sinTheta = sin(theta);

        // calculate dr, dtheta, and dphi.
        dr = (x*vx + y*vy + z*vz) / r;
        if (abs(sinTheta) < EPSILON) {
            dtheta = 0.0; dphi = 0.0;
        } else {
            dtheta = (dr*cos(theta) - vz) / (r*sinTheta);
            dphi = (vy*cos(phi) - vx*sin(phi)) / (r*sinTheta);
        }

        return vec3(dr, dtheta, dphi);
    }

    float computeConservedEnergy(float bhMass, float r, float dr, float dphi) {
        // f = 1 - 2M/r
        float f = 1.0 - 2.0 * bhMass / r;

        // E = sqrt( f + dr^2 + r^2 * f * dphi^2 )
        return sqrt( f + dr * dr + r * r * f * dphi * dphi );
    }

    float computeDt(float bhMass, float r, float conservedEnergy) {
        return conservedEnergy / (1.0 - 2.0 * bhMass / r);
    }

    struct Ray {
        vec3 pos;
        float r;  float theta;  float phi;
        float dr; float dtheta; float dphi;
        float E;  float state[6];
    };

    Ray generateRay(
        int windowWidth, int windowHeight, vec3 camPos, float bhMass, int i, int j, int fov
    ) {
        // initialize variables
        float state[6];
        float x; float y; vec3 dirRay; vec3 sVel;
        float dr; float dtheta; float dphi; float E;

        // calculate initial spherical position of ray
        vec3 sPos = cartesianToSphericalPos(camPos);
        float r=sPos.x; float theta=sPos.y; float phi=sPos.z;

        // calculate relative axis of camera.
        float aspect = float(windowWidth) / windowHeight;
        vec3 forward = normalize(-camPos);
        vec3 right = normalize(cross(forward, UP));
        vec3 up = cross(right, forward);

        // calculate initial cartesian velocity of ray
        x = (
            (2.0*(i+0.5)/float(windowWidth) - 1.0) *
            (tan(radians(fov)/2.0)*aspect)
        );
        y = (
            (1.0 - 2.0*(j+0.5)/float(windowHeight)) *
            tan(radians(fov)/2.0)
        );
        dirRay = normalize(x*right + y*up + forward);

        // convert velocity to spherical velocity
        sVel = cartesianToSphericalVel(dirRay, camPos);
        dr = sVel.x; dtheta = sVel.y; dphi = sVel.z;

        // calculate conserved energy
        E = computeConservedEnergy(bhMass, r, dr, dphi);

        // create state vector
        state = float[6](r, theta, phi, dr, dtheta, dphi);

        return Ray(camPos, r, theta, phi, dr, dtheta, dphi, E, state);
    }

    void main() {
        vec3 pos = vec3(camPos);

        Ray ray = Ray()
    }
    """
)
