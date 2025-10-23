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
        float x = pos[0]; float y = pos[1]; float z = pos[2];
        float r = cartesianToSphericalPos()
    }

    float computeConservedEnergy(
        float bhMass, float r, float dr, float dphi
    ) {
        float f = 1 - 2*bhMass / r;
        return f * sqrt((dr*dr/f + r*r*dphi*dphi/f) / f);
    }

    float computeDt(float bh_mass, float r, float conservedEnergy) {
        return conservedEnergy / (1 - 2 * bh_mass / r);
    }

    Ray generate_ray(
        int windowWidth, int windowHeight, vec3 camPos, float bhMass
    ) {
        float aspect = float(windowWidth) / windowHeight;
        vec3 forward = normalize(-camPos);
        vec3 right = normalize(cross(forward, UP));
        vec3 up = cross(right, forward);
        
    }

    struct Ray {
        vec3 pos;
        float r; float theta; float phi;
        float dr; float dtheta; float dphi;
        float E; float state[6];
    };

    void main() {
        vec3 pos = vec3(camPos)

        Ray ray = Ray()
    }
    """
)
