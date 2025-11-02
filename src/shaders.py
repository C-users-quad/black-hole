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
    #define NUM_STEPS 5000
    #define FOV 45.0
    #define H 1.0
    #define ESCAPE_R 1e5
    #define c 1.0

    vec3 cartesianToSphericalPos(vec3 pos) {
        float x = pos.x;
        float y = pos.y;
        float z = pos.z;

        float r = length(pos);
        float theta = (r >= 0) ? acos(clamp(z / r, -1, 1)) : 0.0;
        float phi = atan(y, x);

        return vec3(r, theta, phi);
    }

    vec3 sphericalToCartesianPos(vec3 pos) {
        float sinTheta = sin(pos.y);
        return vec3(
            pos.x*sinTheta*cos(pos.z),
            pos.x*sinTheta*sin(pos.z),
            pos.x*cos(pos.y)
        );
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
        vec3 camPos, float bhMass, int pixelX, int pixelY
    ) {
        // calculate initial cartesian velocity
        float aspect = float(windowWidth) / windowHeight;
        vec3 forward = normalize(-camPos);
        vec3 right = normalize(cross(forward, UP));
        vec3 up = cross(right, forward);
        float tanHalfFov = tan(radians(FOV) / 2.0);

        float x = (
            (2.0*(pixelX + 0.5) / windowWidth - 1.0) *
            (tanHalfFov * aspect)
        );
        float y = (
            (1.0 - 2.0*(pixelY + 0.5) / windowHeight) *
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

        // initialize and return generated ray
        Ray ray;
        ray.pos = camPos;
        ray.r = r; ray.theta = theta; ray.phi = phi;
        ray.dr = dr; ray.dtheta = dtheta; ray.dphi = dphi;
        ray.E = E;
        for(int i=0; i < 6; i++) ray.state[i] = state[i];
        return ray;
    }

    void updateRayAttribs(inout Ray ray) {
        ray.r      = ray.state[0];
        ray.theta  = ray.state[1];
        ray.phi    = ray.state[2];
        ray.dr     = ray.state[3];
        ray.dtheta = ray.state[4];
        ray.dphi   = ray.state[5];
        ray.pos    = (
            sphericalToCartesianPos(vec3(ray.r, ray.theta, ray.phi))
        );
    }

    // the geodesic trajectory.
    void geodesic(in float state[6], float rS, float bhMass, float E, out float result[6]) {
        // modify result[6] in place here (kX)
        // unpack state vector
        float r=state[0]; float theta=state[1]; float phi=state[2];
        float dr=state[3]; float dtheta=state[4]; float dphi=state[5];

        // add velocity vector to new state vector
        result[0] = dr; result[1] = dtheta; result[2] = dphi;

        // recalculate key values
        float dt = computeDt(bhMass, r, E);
        float f = 1 - rS / r;

        // radial acceleration
        result[3] = (
            - (c*c*rS*f)/(2.0*r*r)*dt*dt
            + rS/(2.0*r*r*f)*dr*dr
            + r*f*dtheta*dtheta
            + r*f*sin(theta)*sin(theta)*dphi*dphi
        );

        // azimuthal acceleration
        result[4] = (
            - (1.0/r)*dr*dtheta
            + sin(theta)*cos(theta)*dphi*dphi
        );

        // polar acceleration
        result[5] = (
            - (1.0/r)*dr*dphi
            - (1.0/tan(theta))*dtheta*dphi
        );
    }

    void rk4Step(inout float state[6], float rS, float bhMass, float E) {
        float k1[6], k2[6], k3[6], k4[6], temp[6];

        geodesic(state, rS, bhMass, E, k1);
        for (int i=0; i < 6; i++) temp[i]=state[i] + (H/2.0) * k1[i];
        geodesic(temp, rS, bhMass, E, k2);
        for (int i=0; i < 6; i++) temp[i]=state[i] + (H/2.0) * k2[i];
        geodesic(temp, rS, bhMass, E, k3);
        for (int i=0; i < 6; i++) temp[i]=state[i] + H * k3[i];
        geodesic(temp, rS, bhMass, E, k4);

        for (int i=0; i < 6; i++) {
            state[i] += (H/6.0)*(k1[i] + 2*k2[i] + 2*k3[i] + k4[i]);
        }
    }

    bool crossesEquatorialPlane(vec3 currentPos, vec3 lastPos) {
        bool crossed = (oldPos.y * newPos.y < 0.0);
        float r = length(vec2(newPos.x, newPos.z));
        return crossed && (r >= diskInnerR && r <= diskOuterR);
    }

    void main() {
        // create ray
        Ray ray = generateRay(
            windowWidth, windowHeight, camPos, bhMass, pixelX, pixelY
        );

        // initialize variables
        bool hitDisk = false; bool hitBH = false;
        vec4 color = vec4(0.0);
        vec3 lastPos = ray.pos;

        // step ray
        for (int i=0; i < NUM_STEPS; i++) {
            // update ray
            rk4Step(ray.state, rS, bhMass, ray.E);
            updateRayAttribs(ray);

            // checks if ray hits black hole.
            if (ray.r <= rS) {
                hitBH = true;
                break;
            }

            // checks if ray hit the accretion disk.
            if (crossesEquatorialPlane(ray.pos, lastPos)) {
                hitDisk = true;
                break;
            }

            // checks if ray escapes off to infinity
            if (ray.r >= ESCAPE_R) {
                break;
            }

            // stores last position.
            lastPos = ray.pos;
        }

        // determines pixel color based on ray trajectory
        if (hitDisk) {
            color = vec4(1.0);
        } else if (hitBH) {
            color = vec4(0.0);
        } else {
            color = vec4(0.0);
        }

    }
    """
)
